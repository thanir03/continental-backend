from flask import Blueprint, request, jsonify
from src.db import DB
from src.services import hotelService, bookingService
from src.utils import loginEndpointMiddleware
from datetime import datetime
import stripe 
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")

book_bp = Blueprint("Booking" ,__name__)


# Only room id is accepted
@book_bp.route("/", methods=["POST"])
def book_hotel():
  conn = DB.conn
  cur = conn.cursor() 
  res = loginEndpointMiddleware(cur, request)
  if not res["status"]:
    return res, 403 

  email = res["payload"]["email"]
  data = request.json
  if ("roomId" not in data) or ("end_date" not in data) or ("start_date" not in data) or ("no_rooms" not in data):
    return jsonify({"status": False, "message" : "Incomplete data provided"}), 400

  start_date = datetime.strptime(data["start_date"], "%Y-%m-%d")
  end_date = datetime.strptime(data["end_date"], "%Y-%m-%d")
  no_rooms = data["no_rooms"]
  roomId = data["roomId"]

  conn = DB.conn
  cur = conn.cursor()
  if not hotelService.does_room_exist(cur,roomId):
    return jsonify({"status": False, "message" : "Room not found"}), 404

  days_difference = (end_date - start_date).days
  if days_difference == 0:
    return jsonify({"status": False, "message" : "Start date and End date is on the same day"}), 400
    
  if start_date >= end_date:
    return jsonify({"status": False, "message" : "End date is before start date"}), 400

  if start_date < datetime.now():
      return jsonify({"status": False, "message" : "Start date is past"}), 400
  
  roomData = hotelService.get_room_minor_details(cur, roomId)

  if no_rooms > roomData["room_count"]:
    return jsonify({"status" : False,  "message" : "Selected room number exceeds available rooms"}) 

  total_price = roomData["price"] * days_difference
  bookingId = bookingService.create_booking(cur, roomId, email, start_date, end_date, no_rooms, total_price ,"PENDING")
  
  hotelService.update_room_count(cur, roomId, no_rooms)
  
  cur.close()
  conn.commit()
  return jsonify({"status": True, "booking_id" : bookingId }), 200



@book_bp.route("/checkout", methods=["POST"])
def create_payment():
  conn = DB.conn
  cur = conn.cursor() 
  res = loginEndpointMiddleware(cur, request)
  if not res["status"]:
    return res, 403 
  data = request.json
  email = res["payload"]["email"]

  if "bookingId" not in data:
    return jsonify({"status" : False,  "message" : "Incomplete data is provided"}) , 400
  bookingId = data["bookingId"]
  bd  = bookingService.get_minor_booking(cur, bookingId)
  if not bd: 
    return jsonify({"status" : False,  "message" : "Booking id not found"}) , 400
  
  if bd["user_email"] != email:
    return jsonify({"status": False, "message": "Cannot pay for booking for other users"}), 400
  
  start_date = bd["start_date"].strftime("%Y-%m-%d")

  end_date = bd["end_date"].strftime("%Y-%m-%d")
  
  bd["start_date"] = start_date
  bd["end_date"] = end_date
  print(bd)
  paymentIntent = stripe.PaymentIntent.create(
    amount=bd["total_price"] * 100, 
    currency="myr", 
    payment_method_types=["grabpay", "card"]
  )
  client_secret = paymentIntent.client_secret
  return jsonify({"client_secret": client_secret, "public_key": STRIPE_PUBLIC_KEY }), 200



@book_bp.route("/details", methods=["GET"])
def get_booking_details():
  conn = DB.conn
  cur = conn.cursor() 
  res = loginEndpointMiddleware(cur, request)
  if not res["status"]:
    return res, 403 
  
  email = res["payload"]["email"]
  status = request.args.get("status")
  if not status or (status != "PENDING" and status != "CURRENT" and status != "PAST" and status != "CANCELLED" and status != "ALL" and status != "SOON"):
    return jsonify({"status" : False,  "message" : "Invalid booking status"}) , 400
  
  res = bookingService.get_booking_details_by_status(cur,status, email)
  for item in res: 
    start_date = item["start_date"].strftime("%Y-%m-%d")
    end_date = item["end_date"].strftime("%Y-%m-%d")
    print(item["start_date"], item["end_date"])
    item["start_date"] = start_date
    item["end_date"] = end_date


  cur.close()
  return jsonify(res), 200


@book_bp.route("/cancel", methods=["PUT"])
def cancel_booking():
  conn = DB.conn
  cur = conn.cursor() 
  res = loginEndpointMiddleware(cur, request)
  if not res["status"]:
    return res, 403 
  
  email = res["payload"]["email"]
  data = request.json
  if "bookingId" not in data:
    return jsonify({"status" : False,  "message" : "Incomplete data is provided"}) , 400
  bookingId = data["bookingId"]
  bd  = bookingService.get_minor_booking(cur, bookingId)
  if not bd: 
    return jsonify({"status" : False,  "message" : "Booking id not found"}) , 400
  
  if bd["user_email"] != email:
    return jsonify({"status": False, "message": "Cannot cancel booking for other users"}), 400
  
  if bd["status"] != "SOON" or bd["status"] != "PENDING":
    bookingService.cancel_booking(cur, bookingId)
  cur.close()
  conn.commit()
  return jsonify({"status" : True, "message": "Successfully cancelled" })


