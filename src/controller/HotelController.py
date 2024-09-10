from flask import Blueprint, request, jsonify
from src.db import DB
from src.services import hotelService
from src.utils import capitilize_str, loginEndpointMiddleware

hotel_bp = Blueprint("Hotel",__name__)

@hotel_bp.route("/search/", methods=["GET"])
def search_hotel_endpoint():
  query = request.args.get("q")
  room_num = request.args.get("room_num")
  no_adults = request.args.get("no_adults")
  no_children = request.args.get("no_children")
  
  # Optional fields 
  start_price = request.args.get("start_price")
  end_price = request.args.get("end_price")
  sort = request.args.get("sort")

  if not query or not room_num or not no_adults or not no_children:
    return jsonify({"message": "Invalid data provided"}), 400
  if sort and (sort not in ["rating", "lowest_price", "highest_price"]): 
    return jsonify({"message": "Invalid sort field"}) , 400
  
  if (start_price and not end_price) or (not start_price and end_price):
      return jsonify({"message": "Invalid pricing"}), 400
  
  if start_price and end_price:
    if float(start_price) > float(end_price): return jsonify({"message": "Invalid pricing"}), 400

  cur = DB.conn.cursor()
  
  res = hotelService.search_hotel(cur, no_adults, no_children, room_num, query, start_price, end_price, sort)
  cur.close()
  return jsonify(res), 200
  


# Hotel id is provided
@hotel_bp.route("/<int:id>/", methods=["GET"])
def hotel_details(id: int):
  conn = DB.conn
  cur = conn.cursor() 
  res = loginEndpointMiddleware(cur, request)

  email = ""
  if  res["status"]:
    email = res["payload"]["email"]
  if not hotelService.does_hotel_exist(cur, id):
    return jsonify({"message" : "Hotel not found"}), 404
  res = hotelService.get_hotel_details(cur,id, email)
  cur.close()
  return jsonify(res), 200
  
# Hotel id is provided
@hotel_bp.route("/<int:id>/rooms/", methods=["GET"])
def room_details(id: int):
  cur = DB.conn.cursor()
  if not hotelService.does_hotel_exist(cur, id):
    return jsonify({"message" : "Hotel not found"}), 404
  res = hotelService.get_room_details(cur,id)
  cur.close()
  return jsonify(res), 200


@hotel_bp.route("/<int:id>/landmarks/", methods=["GET"])
def get_hotel_landmarks(id: int):
  cur = DB.conn.cursor()
  if not hotelService.does_hotel_exist(cur, id):
    return jsonify({"message" : "Hotel not found"}), 404
  res = hotelService.get_landmarks(cur,id)
  cur.close()
  return jsonify(res), 200

# To get hotels by categories
@hotel_bp.route("/category/<string:category>/", methods=["GET"])
def get_hotel_by_category(category: str):
    conn = DB.conn
    cur = conn.cursor() 
    res = loginEndpointMiddleware(cur, request)
    email = ""
    if  res["status"]:
      email = res["payload"]["email"]
    
    limit_param = request.args.get("limit")
    limit = limit_param  if limit_param else 20  
    category = " ".join(map(capitilize_str, category.split(" ")))
    res = hotelService.get_hotel_by_category(cur,category, limit, email)
    cur.close()
    return jsonify(res), 200


@hotel_bp.route("/like/<int:id>/", methods=["POST"])
def like_hotel(id: int):
  conn = DB.conn
  cur = conn.cursor() 
  res = loginEndpointMiddleware(cur, request)
  if not res["status"]:
    return res, 403 
  
  if not hotelService.does_hotel_exist(cur, id):
    return jsonify({"status": False, "message" : "Hotel not found"}), 404

  email = res["payload"]["email"]
  action = "like"
  if hotelService.has_user_like_hotel(cur,id, email): 
      hotelService.dislike_hotel(cur,id, email)
      action = "dislike"
  else: 
      hotelService.like_hotel(cur,id, email)
  conn.commit()
  cur.close()
  return jsonify({"status": True, "action": action }), 200


@hotel_bp.route("/cities/", methods=["GET"])
def getCities():
    query = request.args.get("q")
    conn = DB.conn
    cur = conn.cursor()
    res = hotelService.get_city(cur, query)
    cur.close()
    return jsonify(res) ,200



# TODAY 
# Wireless Dev
# 1. Complete Booking and payment api
# 2. Complete booking details api
# 3. Payment api 
# 4. CRON Job for updating booking details 

