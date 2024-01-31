"""Unit regarding an API server in order to support the front-end project."""
import logging
import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify, abort
from flask_cors import CORS

from common.neo4JConnection import Neo4JConnection
from common.webUtils import WebUtils

# Load environment variables from .env file
load_dotenv()

"""Properties regarding the web server configuration."""
PORT = os.environ.get("API_WORKPROJECT_PORT")

"""Database connectivity parameters."""
"""Properties regarding the Neo4j connection configuration."""
uri = os.environ.get("DB_NEO4J")
username = os.environ.get("DB_NEO4J_USERNAME")
password = os.environ.get("DB_NEO4J_PASSWORD")
database = os.environ.get("DB_NEO4J_DATABASE_FE_NAME")

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

"""Neo4J Connection regarding workpackage Graph."""


class WorkColabNeo4JConnection(Neo4JConnection):
    @staticmethod
    def read_project_by_title(tx, filters):
        return {}

    @staticmethod
    def insert_schema_work_plan(tx, values):
        workplan_query = (
            """CREATE (w:Workplan {number: $number, title: $title})"""
        )

        result = tx.run(workplan_query, **values)

        return result

    @staticmethod
    def insert_schema_workpackage(tx, values):
        workpackage_query = (
            "CREATE (w:Workpackage {number: $number, description: $description, workpackage_id: $workpackage_id})"
        )

        result = tx.run(workpackage_query, **values)

    @staticmethod
    def connect_workpackage_to_workplan(tx, values):
        relation_query = (
            """MATCH (w:Workplan {number: $workplan_id})
            MATCH (t:Workpackage {number: $workpackage_id})
            CREATE (w)-[:CONTAINS]->(t)"""
        )

        result = tx.run(relation_query, **values)

        return result

    @staticmethod
    def insert_schema_task(tx, values):
        task_query = (
            """CREATE (t:Task {workpackage_id: $workpackage_id, task_id: $task_id, number: $number, description: $description})"""
        )

        result = tx.run(task_query, **values)

    @staticmethod
    def connect_task_to_workpackage(tx, values):
        relation_query = (
            """MATCH (w:Workpackage {workpackage_id: $workpackage_id})
            MATCH (t:Task {task_id: $task_id})
            CREATE (w)-[:CONTAINS]->(t)"""
        )

        result = tx.run(relation_query, **values)

        return result

    @staticmethod
    def insert_period(tx, values):
        period_query = (
            """CREATE (p:Period {period_id: $period_id, start_date: $start_date, end_date: $end_date})"""
        )

        result = tx.run(period_query, **values)

        return result

    @staticmethod
    def connect_task_to_period(tx, values):
        relation_query = (
            """MATCH (t:Task {task_id: $task_id})
            MATCH (p:Period {period_id: $period_id})
            CREATE (t)-[:HAS_PERIOD]->(p)"""
        )

        result = tx.run(relation_query, **values)

        return result

    @staticmethod
    def get_workplan_by_id(tx, values):
        query = (
            """MATCH (w:Workplan {number: $workplan_id, title: $workplan_title})-[:CONTAINS]->
            (wp:Workpackage)-[:CONTAINS]-> (t:Task)-[:HAS_PERIOD]-> (p:Period)
            RETURN w.number AS workplan_number, w.title AS workplan_description, 
            wp.number AS workpackage_number, wp.description AS workpackage_description,
            t.number AS task_number, t.description AS task_description, 
            p.start_date AS period_start, p.end_date AS period_end"""
        )
        records = tx.run(query, **values)

        return tuple(records)


neo4JConnection = WorkColabNeo4JConnection(uri, username, password, database).driver

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/get_workplan/<string:text>", methods=["GET"])
def get_workplan(text: str):
    workplan = {}

    with neo4JConnection.session() as session:
        records = session.read_transaction(WorkColabNeo4JConnection.get_workplan_by_id, {
            "workplan_id": text,
            "workplan_title": text
        })

        logging.log(logging.INFO, f"Workplan found = {records}")

        if records is None or len(records) == 0:
            raise abort(WebUtils.NOT_FOUND, description=f"""Workplan with id [{text}] not found!""")

        workpackages = dict()
        tasks = dict()

        for record in records:
            workplan_number = record['workplan_number']
            workplan_description = record['workplan_description']
            workpackage_number = record['workpackage_number']
            workpackage_description = record['workpackage_description']
            task_number = record['task_number']
            task_description = record['task_description']
            period_start = record['period_start']
            period_end = record['period_end']

            if not workplan:
                # If workplan doesn't exist, create a new one
                workplan = {
                    "number": workplan_number,
                    "title": workplan_description,
                    "workpackages": []
                }

            # Check if the task already exists in the workplan
            workpackage = workpackages.get(f"{workpackage_number}_${workplan_number}", None)
            if not workpackage:
                # If task doesn't exist, create a new one
                workpackage = {
                    "number": workpackage_number,
                    "description": workpackage_description,
                    "tasks": []
                }
                workplan["workpackages"].append(workpackage)
                workpackages[f"{workpackage_number}_${workplan_number}"] = workpackage

            # Check if the task already exists in the workplan
            task = tasks.get(f"{task_number}_${workpackage_number}_${workplan_number}", None)

            if not task:
                # If task doesn't exist, create a new one
                task = {
                    "number": task_number,
                    "description": task_description,
                    "periods": []
                }
                workpackage["tasks"].append(task)
                tasks[f"{task_number}_${workpackage_number}_${workplan_number}"] = task

            # Add period to the task
            task["periods"].append({
                "start": WebUtils.date_to_str(period_start, DATE_TIME_FORMAT),
                "end": WebUtils.date_to_str(period_end, DATE_TIME_FORMAT)
            })

    return jsonify(workplan)


"""Route regarding the inserting of workplan."""


@app.route("/insert_workplan", methods=["POST"])
def insert_workplan():
    data = request.json

    with neo4JConnection.session() as session:
        workplan_id = WebUtils.get_a_random_string()

        vworkplan = {
            "number": workplan_id,
            "title": data["title"]
        }

        # Write workplan header.
        session.write_transaction(WorkColabNeo4JConnection.insert_schema_work_plan, vworkplan)

        for workpackage in data["workpackages"]:
            workpackage_id = WebUtils.get_a_random_string()

            vworkpackage = {
                "workpackage_id": workpackage_id,
                "number": workpackage["number"],
                "description": workpackage["description"]
            }

            # Write workplan header.
            session.write_transaction(WorkColabNeo4JConnection.insert_schema_workpackage, vworkpackage)

            workpackage_connection = {
                "workplan_id": workplan_id,
                "workpackage_id": workpackage_id
            }

            session.write_transaction(WorkColabNeo4JConnection.connect_workpackage_to_workplan, workpackage_connection)

            for task in workpackage["tasks"]:
                task_id = WebUtils.get_a_random_string()

                vtask = {
                    "workpackage_id": workpackage_id,
                    "task_id": task_id,
                    "number": task["number"],
                    "description": task["description"]
                }

                # Write tasks.
                session.write_transaction(WorkColabNeo4JConnection.insert_schema_task, vtask)

                task_connection = {
                    "workpackage_id": workpackage_id,
                    "task_id": task_id
                }

                # Connect each task to workplan.
                session.write_transaction(WorkColabNeo4JConnection.connect_task_to_workpackage, task_connection)

                for period in task["periods"]:
                    period_id = WebUtils.get_a_random_string()
                    vperiod = {}

                    for key in ["start", "end"]:
                        vperiod[f"{key}_date"] = WebUtils.str_to_date(period[key], DATE_TIME_FORMAT)

                    vperiod["period_id"] = period_id

                    session.write_transaction(WorkColabNeo4JConnection.insert_period, vperiod)

                    period_connection = {
                        "task_id": task_id,
                        "period_id": period_id
                    }

                    session.write_transaction(WorkColabNeo4JConnection.connect_task_to_period, period_connection)

    return {"message": f"The workpan inserted sucessfully with id ${workplan_id}!"}


# Handle HTTP errors with a JSON response
@app.errorhandler(Exception)
def http_error(error):
    return WebUtils.handle_error(error)


if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)

    app.run(host="0.0.0.0", port=PORT, debug=True)
