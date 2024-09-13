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


def getFullBooking(cur, bookingId:int, email:str):
    sql = """
        SELECT h.name, hi.image_url, h.address, h.latitude, h.longtitude, h.id, h.rating, r.name, r.price, r.no_child, r.no_adult,r.bed, r.size, ri.image_url, booking.* FROM booking
        inner join room r on booking.room_id = r.id
        inner join hotel h on r.hotel_id = h.id
        inner join (SELECT image_url, hotel_id FROM hotel_image where rank = 1) as hi on hi.hotel_id = h.id
        inner join (SELECT image_url, room_id FROM room_image where rank = 1) as ri on ri.room_id = r.id
        inner join app_user on booking.user_email = app_user.email where booking.user_email = %s and booking.id = %s
    """
    cur.execute(sql, (email, bookingId))
    res = cur.fetchone()
    return convertToDict(res, ["h_name", "h_img", "h_address", "h_lat", "h_lng", "h_id", "h_rating", "r_name", "r_price", "r_no_child", "r_no_adult", "r_bed", "r_size", "r_img", "b_id", 
    "b_no_room", "email", "r_id", "b_start", "b_end", "total", "status"])


def completeBookingPayment(cur, bookingId: int):
   sql = "UPDATE BOOKING SET status = 'SOON' where id = %s"
   cur.execute(sql, (bookingId,))