from flask import Flask, jsonify
from dotenv import load_dotenv
from src.auth import AuthController
from src.db import DB
from os import getenv


app = Flask(__name__)
load_dotenv("./.env")

DB_NAME = getenv("DB_NAME")
DB_USER = getenv("DB_USER")
DB_HOST = getenv("DB_HOST")
DB_PASSWORD = getenv("DB_PASSWORD") 



@app.route("/", methods=["GET"])
def index():
  cursor = DB.conn.cursor()
  cursor.execute("""
  SELECT * FROM (
        SELECT hotel.*, hotel_image.image_url, ROW_NUMBER() OVER (PARTITION BY hotel_id ORDER BY hotel_image.id) AS image_rank
        FROM HOTEL INNER JOIN HOTEL_IMAGE ON HOTEL_IMAGE.hotel_id = HOTEL.id
) as hotel_data where image_rank = 1;
""")
  res = cursor.fetchall()
  cursor.close()
  return jsonify(res), 200

if __name__ == "__main__":
    try: 
      print(DB_PASSWORD)
      conn = DB()
      print(DB.conn)
    except Exception as e:
      print(e)
      print("Unable to connect to database")
    app.register_blueprint(AuthController.auth_bp, url_prefix="/auth")
    app.run(host="0.0.0.0", port=7000, debug=True)
