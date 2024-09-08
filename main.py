from flask import Flask, jsonify
from dotenv import load_dotenv
from src.controller import AuthController, HotelController
from src.db import DB
from os import getenv


app = Flask(__name__)
load_dotenv("./.env")

DB_NAME = getenv("DB_NAME")
DB_USER = getenv("DB_USER")
DB_HOST = getenv("DB_HOST")
DB_PASSWORD = getenv("DB_PASSWORD") 


if __name__ == "__main__":
    try: 
      print(DB_PASSWORD)
      conn = DB()
      print(DB.conn)
    except Exception as e:
      print(e)
      print("Unable to connect to database")
    app.register_blueprint(AuthController.auth_bp, url_prefix="/auth")
    app.register_blueprint(HotelController.hotel_bp, url_prefix="/hotel")
    app.run(host="0.0.0.0", port=7000, debug=True)
