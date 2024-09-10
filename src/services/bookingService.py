from src.db import convertToDict

def create_booking(cur, roomId, email, start_date, end_date, no_room, total_price, status):
  sql = "INSERT INTO BOOKING (room_id, user_email ,start_date, end_date, no_room, total_price, status) VALUES (%s, %s, %s, %s,%s,%s, %s) RETURNING id"
  cur.execute(sql , (roomId, email, start_date, end_date, no_room, total_price, status))
  res = cur.fetchone()
  return res[0]


def get_minor_booking(cur, bookingId:int):
  sql = "SELECT * FROM booking where id = %s"
  cur.execute(sql, (bookingId,))
  res = cur.fetchone()
  return convertToDict(res, ["id", "no_room", "user_email", "room_id", "start_date", "end_date", "total_price", "status"])


def get_booking_details_by_status(cur, status: str, email:str):
  keys = [email]
  sql = "SELECT booking.*, r.name, r.price, r.no_child, r.no_adult, h.name, hi.image_url, h.address, h.longtitude, h.latitude, h.id FROM booking inner join room r on booking.room_id = r.id inner join hotel h on r.hotel_id = h.id inner join (SELECT image_url, hotel_id FROM hotel_image where rank = 1) as hi on hi.hotel_id = h.id inner join app_user on booking.user_email = app_user.email where booking.user_email = %s "
  if status != "ALL": 
    sql += "and booking.status = %s"
    keys.append(status)
  sql+=';'
  cur.execute(sql, keys)
  
  res = cur.fetchall()
  arr = []
  for item in res:
    arr.append(convertToDict(item, ["bookingId", "no_room", "user_email", "room_id", "start_date", "end_date", "total_price", "status", "room_name", "room_price", "room_no_child", "room_no_adult", "hotel_name", "hotel_image", "address", "lat", "lng", "hotel_id"]))
  return arr


def cancel_booking(cur, bookingId):
    sql = "UPDATE booking set status ='CANCELLED' where id = %s"
    cur.execute(sql , (bookingId,))
    
def get_all_bookings(cur):
    sql = "SELECT * FROM BOOKING WHERE status = 'SOON' or status = 'CURRENT';"
    cur.execute(sql)
    res = cur.fetchall()
    arr = []
    for item in res:
        arr.append(convertToDict(item, ["id", "no_room", "user_email", "room_id", "start_date", "end_date", "total_price", "status"]))
    return arr


def update_booking_status(cur, bookingId:int , status:str):
    sql = "UPDATE booking set status = %s where id = %s"
    cur.execute(sql , (status, bookingId))
