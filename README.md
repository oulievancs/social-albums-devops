# social-albums
Regarding a project on HUA University about Backend development of MSc. Presenting a social
network ETL project consuming two datasets from two databases *MongoDB* and *Neo4J*. Using
the *Kafka*, datasources are extracted and transformed into a relational database *MySQL*,
creating the associations between music albums and artists that was located into the *MongoDB*
and users that was located into the *Neo4J DB*.

*API*s are configured in order to provide intelligent ideas, that creates suggestions
of music albums and artists to users regarding its associations into the social network.

---

## Modules Containing
### List of Modules

* Flask API that starts `extraction/artistsWebApp.py` the extraction of artists from the
*MongoDB* into a *Kafka* topic.

* Flask API that starts `extraction/usersWebApp.py` the extraction of users from the *Neo4J*
into a *Kafka* topic.

* The *Kafka* consumers `transformationLoad/transformationAndLoadApp.py` that defining
two *Kafka* consumers into isolated threads, each consumer regarding into each *Kafka*
topic and load the consumed data's into a *MySQL* database.

* A *Flask* API that provides intelligent recommendation of music albums and artists on
a requested user, regarding its associations in the social network and the preferences 
of its friends. This module, located on `api/apiServer.py`.


Finally, an extra, out of scope module presented on `api/workProjectBackend.py`
that regarding an example of the FR - front end exercise, and how
data regarding a *Workplan* can be stored on a *Neo4J* database.