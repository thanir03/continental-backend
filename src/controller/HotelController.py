from flask import Blueprint, request, jsonify
from src.db import DB
from src.services import hotelService
from http import HTTPStatus

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
    return jsonify({"message": "Invalid data provided"}), HTTPStatus.BAD_REQUEST
  if sort and (sort not in ["rating", "lowest_price", "highest_price"]): 
    return jsonify({"message": "Invalid sort field"}) , HTTPStatus.BAD_REQUEST
  
  if start_price and not end_price or not start_price and end_price:
      return jsonify({"message": "Invalid pricing"}), HTTPStatus.BAD_REQUEST
  
  if start_price and end_price:
    if float(start_price) > float(end_price): return jsonify({"message": "Invalid pricing"}), HTTPStatus.BAD_REQUEST

  cur = DB.conn.cursor()
  
  res = hotelService.search_hotel(cur, no_adults, no_children, room_num, query, start_price, end_price, sort)
  cur.close()
  return jsonify(res), 200
  


# Hotel id is provided
@hotel_bp.route("/<int:id>/", methods=["GET"])
def hotel_details(id: int):
  cur = DB.conn.cursor()
  if not hotelService.does_hotel_exist(cur, id):
    return jsonify({"message" : "Hotel not found"}), 404
  res = hotelService.get_hotel_details(cur,id)
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