"""A unit regarding the functinality for MySQL database."""
import mysql.connector.pooling

"""Class regarding the MySQL result set."""


class MySQLResult:
    def __init__(self, connection, cursor=None):
        if cursor is not None:
            self._rowcount = cursor.rowcount
            self._fetch_all_and_fetch_one(cursor)
            self._lastrowid = cursor.lastrowid
        else:
            self._rowcount = None
            self._fetchall = None
            self._fetchone = None
            self._lastrowid = None

        self._cursor = cursor

        self._connection = connection

        self._active_transaction = False

    @property
    def fetchone(self) -> ():
        if len(self._fetchall) > 1:
            raise Exception(f"Multiple rows returned: {len(self._fetchall)}")
        return self._fetchone

    @property
    def fetchall(self) -> [()]:
        return self._fetchall

    @property
    def rowcount(self) -> int:
        return self._rowcount

    @property
    def lastrowid(self) -> any:
        return self._lastrowid

    @property
    def cursor(self):
        return self._cursor

    @property
    def connection(self):
        return self._connection

    @cursor.setter
    def cursor(self, cursor):
        if cursor is not None:
            self._rowcount = cursor.rowcount
            self._fetch_all_and_fetch_one(cursor)
            self._lastrowid = cursor.lastrowid
        else:
            self._rowcount = 0
            self._fetchall = []
            self._fetchone = None
            self._lastrowid = None

        self._cursor = cursor

    def close_connection(self):
        self._close(self._connection, self._cursor)

    def commit(self):
        self._connection.commit()

    def rollback(self):
        if self._active_transaction:
            self._active_transaction = False
            self._connection.rollback()

    def start_transaction(self):
        if not self._active_transaction:
            self._active_transaction = True
            self._connection.start_transaction()

    def _close(self, connection, cursor):
        if self._active_transaction:
            self.rollback()
        if cursor is not None:
            cursor.close()
        if not connection.is_closed():
            connection.close()

    def _fetch_all_and_fetch_one(self, cursor):
        if "insert" not in cursor.statement.lower():
            self._fetchall = cursor.fetchall()
            if cursor.fetchone():
                self._fetchone = cursor.fetchone()
            else:
                if self._fetchall and len(self._fetchall) > 0:
                    self._fetchone = self._fetchall[0]
                else:
                    self._fetchone = None


class MySqlConnection:
    def __init__(self, host, database, user, password, port=3306):
        self._database = database
        self._user = user
        self._password = password

        self._dbconfig = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database
        }

        self._pool = self._create_pool()

    def _create_pool(self, pool_name="mypool", pool_size=10) -> mysql.connector.pooling.MySQLConnectionPool:
        return mysql.connector.pooling.MySQLConnectionPool(
            pool_name=pool_name, pool_size=pool_size, pool_reset_session=False,
            autocommit=True,
            **self._dbconfig
        )

    @staticmethod
    def close(connection, cursor):
        cursor.close()
        connection.close()

    def pool_connection(self) -> MySQLResult:
        connection = self._pool.get_connection()

        return MySQLResult(connection)

    def execute(self, sql, args=None, commit=False, mysqlResult=None) -> MySQLResult:
        connection = self._pool.get_connection() if mysqlResult is None else mysqlResult.connection
        cursor = connection.cursor(
            buffered=True) if mysqlResult is None or mysqlResult.cursor is None else mysqlResult.cursor

        cursor.reset()

        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)

        if commit:
            connection.commit()

        if mysqlResult is not None:
            mysqlResult.cursor = cursor

        return mysqlResult if mysqlResult is not None else MySQLResult(connection, cursor)
