
import psycopg2
from os import getenv

class DB:
  conn = None
  def __init__(self):
    if not DB.conn: 
      self.connect_db()

  def connect_db(self):
    DB_NAME = getenv("DB_NAME")
    DB_USER = getenv("DB_USER")
    DB_HOST = getenv("DB_HOST")
    DB_PASSWORD = getenv("DB_PASSWORD") 

    try: 
      DB.conn = psycopg2.connect(f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' password={DB_PASSWORD}")
      print("Successful connection")
    except Exception as e:
      print(e)
      print("Unable to connect to database")
      return None