from flask import Flask
from dotenv import load_dotenv
from src.controller import AuthController, HotelController, BookingController
from src.db import DB
from flask_apscheduler import APScheduler
from src.services import bookingService
from datetime import datetime, timedelta
import random

app = Flask(__name__)
scheduler = APScheduler()
load_dotenv("./.env")

@scheduler.task('interval', id='update_booking_status', days=1)
def my_job():
    conn = DB.conn
    cur = conn.cursor()
    try:
      print('This job is executed everyday')
      res = bookingService.get_all_bookings(cur)
      print("Retrieving all booking data")

      for item in res:
        start = item["start_date"]
        end = item["end_date"]
        now = datetime.now().date()
        if now >= start and now <= end and item["status"] != "CURRENT":
          bookingService.update_booking_status(cur, item["id"], "CURRENT")
          # send notification to users about the booking status
          print(f"UPDATED booking  for id= {item['id']} status from {item['status']} to CURRENT")
        elif now > end:
          bookingService.update_booking_status(cur, item["id"], "PAST")
          print(f"UPDATED booking  for id= {item['id']} status from {item['status']} to PAST")
      cur.close()
      conn.commit()
    except Exception as e:
       print(e)
       cur.close()
       conn.rollback()


if __name__ == "__main__":
    try: 
      conn = DB()
    except Exception as e:
      print(e)
      print("Unable to connect to database")
    app.register_blueprint(AuthController.auth_bp, url_prefix="/auth")
    app.register_blueprint(HotelController.hotel_bp, url_prefix="/hotel")
    app.register_blueprint(BookingController.book_bp, url_prefix="/book")
    scheduler.init_app(app)
    scheduler.start()
    app.run(host="0.0.0.0", port=7000, debug=True)