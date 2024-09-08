from src.db import convertToDict

def search_hotel(cur, no_adults, no_children, room_num, query, start_price, end_price, sort):
    sql = """SELECT  hotel.id, hotel.name, hotel.rating, hotel.starting_price, hi.image_url, hotel.latitude, hotel.longtitude, hotel.city, hotel.description
    FROM hotel
    inner join (
            SELECT hotel_id from room where
            room.no_adult >= %s
            AND room.no_child >= %s
            AND room.room_count >= %s
            GROUP BY hotel_id
    ) as room on room.hotel_id = hotel.id
    inner join (SELECT image_url, hotel_id FROM hotel_image where rank = 1) as hi
        on hi.hotel_id = hotel.id
    WHERE (hotel.city LIKE %s
          OR HOTEL.name LIKE %s)"""

    if start_price:
        sql += """AND (starting_price >= %s
      and starting_price <= %s)"""

    if sort:
        if sort == "rating":
            sql += "ORDER BY rating DESC"
        elif sort == "lowest_price":
            sql += "ORDER BY starting_price ASC"
        else:
            sql += "ORDER BY starting_price DESC"
    sql = sql + ";"
    if start_price:
      cur.execute(sql, (no_adults, no_children, room_num, "%"+ query+"%", "%"+ query+"%", start_price, end_price))
    else: 
      cur.execute(sql, (no_adults, no_children, room_num, "%"+ query+"%", "%"+ query+"%"))
    
    res = cur.fetchall()
    arr = []
    for item in res:
        arr.append(convertToDict(item, ["id", "name", "rating", "price", "image_url", "lat", "long","city", "desc"]))
    return arr

def get_room_details(cur, id:int):
    sql = """
      SELECT room.*, json_agg(ri.image_url) as room_images FROM ROOM
      inner join room_image ri on ROOM.id = ri.room_id
      where hotel_id = %s
      GROUP BY  room.id;
  """
    cur.execute(sql, (id,))
    res = cur.fetchall()
    arr = []
    for item in res:
        arr.append(convertToDict(item, ["id", "name", "bed", "size", "num_rooms", "no_adult", "no_child","price", "hotel_id", "room_images"]))
    return arr

def get_hotel_details(cur, id:int):
    sql = """
      SELECT hotel.*, json_agg(hi.image_url) as hotel_images from hotel
	    inner join hotel_image hi on hotel.id = hi.hotel_id
      where hotel.id = %s
      group by hotel.id;
  """
    cur.execute(sql, (id,))
    res = cur.fetchone()
    return convertToDict(res, ["id", "name", "address", "desc", "rating", "city",  "starting_price", "agoda_url", "lat","lng", "hotel_images"])


def does_hotel_exist(cur, id:int):
    sql = "SELECT COUNT(hotel.id) from hotel where id = %s"

    cur.execute(sql, (id,))
    res = cur.fetchone()
    return res[0] == 1