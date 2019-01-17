from psycopg2 import connect, IntegrityError, OperationalError, DataError
from psycopg2.extras import RealDictCursor


# klasy Baza danych, zapytania
class DB:
    username = "postgres"
    passwd = "coderslab"
    hostname = "localhost"
    db_name = "homework_d2"  # nazwa bazy tylko z malej litery!

    def connect(self):
        self.cnx = connect(user=self.username, password=self.passwd, host=self.hostname, database=self.db_name)
        return self.cnx

    def create_tables(self):
        sql_c = 'CREATE TABLE Cinemas(id serial, name varchar(100) not NULL , address varchar(200),capacity SMALLINT, PRIMARY KEY (id));'
        sql_m = 'CREATE TABLE Movies(id serial, name varchar(100) not NULL , description text, rating DECIMAL(4,2), PRIMARY KEY (id));'
        sql_t = '''CREATE TABLE Tickets(id serial, quantity int not NULL , price decimal(5,2) not NULL ,id_show SMALLINT not null,
                   PRIMARY KEY (id),FOREIGN KEY(id_show) REFERENCES shows(id) on DELETE CASCADE);'''
        sql_p = """CREATE TABLE payments(ticket_id INT not null,type VARCHAR (100), date DATE,
                    PRIMARY KEY (ticket_id), FOREIGN KEY (ticket_id) REFERENCES tickets(id) on DELETE CASCADE);"""
        sql_s = """CREATE TABLE shows(id serial not null, id_cinema int not null, id_movie int not null, PRIMARY KEY (id), UNIQUE (id_cinema, id_movie),
                   FOREIGN key(id_cinema) REFERENCES cinemas(id) on DELETE CASCADE, FOREIGN  key (id_movie) REFERENCES movies(id) on DELETE CASCADE); """
        sqls = [sql_c, sql_m, sql_s, sql_t, sql_p]
        cnx = self.connect()
        with cnx.cursor() as curs:
            for sql in sqls:
                curs.execute(sql)
            cnx.commit()
        cnx.close()

    def delete(self, table, id):
        cnx = self.connect()
        with cnx.cursor() as cursor:
            if table == 'payments':
                sql = "DELETE FROM {} WHERE ticket_id={} returning ticket_id;".format(table, id)
            else:
                sql = "DELETE FROM {} WHERE id={} returning id;".format(table, id)
            cursor.execute(sql)
            self.id = cursor.fetchone()
            cnx.commit()
        cnx.close()

    def insert(self, sql, values):
        cnx = self.connect()
        with cnx.cursor() as cursor:
            cursor.execute(sql, values)
            if 'returning' in sql:
                self.id = cursor.fetchone()
            cnx.commit()
        cnx.close()

    def select(self, sql):
        cnx = self.connect()
        with cnx.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql)
            self.data = [row for row in cursor]  # lista slownikow!
            cnx.commit()
        cnx.close()


class createDB(DB):
    def run(self):
        sql = "CREATE DATABASE homework_d2;"
        cnx = connect(user=self.username, password=self.passwd, host=self.hostname)
        cnx.autocommit = True
        with cnx.cursor() as curs:
            curs.execute(sql)
        cnx.close()

    def clean(self):
        sql = "DROP DATABASE IF EXISTS homework_d2;"
        cnx = connect(user=self.username, password=self.passwd, host=self.hostname)
        cnx.autocommit = True
        with cnx.cursor() as curs:
            curs.execute(sql)
        cnx.close()


# Funkcja walidacyjna
def data_validation(x, float_number=False, rating=False, name=False):
    if name:
        if not x:
            return "Validation error.Name can't be empty."
        else:
            try:
                int(x)
                return "Validation error.Name can't be only a number."
            except Exception:
                return None

    if not float_number:
        try:
            int(x)
        except Exception:
            return "Validation error.For fields:'rating','price' only FLOAT numbers are allowed. For fields:'capacity','quantity' only INT numbers are allowed."

    if float_number:
        try:
            float(x)
        except Exception:
            return "Validation error.For fields:'rating','price' only FLOAT numbers are allowed. For fields:'capacity','quantity' only INT numbers are allowed."

    if rating:
        if float(x) < 1 or float(x) > 10:
            return "Validation error.Rating can't be lower than 1 or higher than 10."
    return None


def select(sql):
    o1 = DB()
    o1.select(sql)
    table_rows = o1.data
    return table_rows


def t_form():
    sql = 'select shows.id, movies.name as m_name, cinemas.name as c_name from shows inner join movies on movies.id= shows.id_movie inner join cinemas on cinemas.id=shows.id_cinema;'
    table_rows = select(sql)
    return table_rows
