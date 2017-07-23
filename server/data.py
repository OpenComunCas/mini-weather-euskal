import sqlite3
from datetime import datetime

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class Conexion(object):
    def  __init__(self,db_name='medidas.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def commit(self):
        self.conn.commit()

    def open(self):
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = dict_factory
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def execute_select(self,query,params = None):
        if params is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query,params)
        return self.cursor.fetchall()

    def execute_query(self,query,params = None):
        if params is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query,params)

    def execute(self,query,params=None):
        if query.strip().lower().startswith("select"):
            return self.execute_select(query,params)
        else:
            return self.execute_query(query,params)

class DaoMedidas(object):
    def __init__(self):
        self.__table__ = "medidas"
        self.create_table()

    def create_table(self):
        query = """
               CREATE TABLE IF NOT EXISTS {0} (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               temp NUMERIC,
               hum NUMERIC,
               timestamp text NOT NULL
               );
               """.format(self.__table__)

        with Conexion() as ctx:
           ctx.execute(query)
           ctx.commit()

    def insertar(self,json):
        timestamp = datetime.now()
        query = "INSERT INTO "+self.__table__+" (temp,hum,timestamp) VALUES (?,?,?)"
        params =(json["temp"],json["hum"],str(timestamp))
        with Conexion() as ctx:
            ctx.execute(query,params)
            ctx.commit()

    def obtener_todos(self):
        query= "SELECT * FROM {0} ORDER BY timestamp DESC".format(self.__table__)
        medidas = []
        with Conexion() as ctx:
            data = ctx.execute(query)
            if data is not None:
                medidas = [dict(e) for e in data]
        return medidas

    def current(self):
        query= "SELECT * FROM {0} where id = (select max(id) from {0})".format(self.__table__)
        with Conexion() as ctx:
            data = ctx.execute(query)
            if data is not None:
                return  dict(data[0])
        return None


