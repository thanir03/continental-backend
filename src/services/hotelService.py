from src.db import convertToDict

# Too much work to just show an liked btn
def search_hotel(cur, no_adults, no_children, room_num, query, start_price, end_price, sort):
    sql = """SELECT  hotel.id, hotel.name, hotel.rating, hotel.starting_price, hi.image_url, hotel.latitude, hotel.longtitude, hotel.city, hotel.description, hotel.category
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
    WHERE (LOWER(hotel.city) LIKE LOWER(%s)
          OR LOWER(HOTEL.name) LIKE LOWER(%s) or LOWER(hotel.address) LIKE LOWER(%s))"""

    if start_price:
        sql += """AND (starting_price >= %s
      and starting_price <= %s)"""

    if sort:
        if sort == "rating":
            sql += " ORDER BY rating DESC"
        elif sort == "lowest_price":
            sql += " ORDER BY starting_price ASC"
        else:
            sql += " ORDER BY starting_price DESC"
    sql = sql + ";"
    if start_price:
      cur.execute(sql, (no_adults, no_children, room_num, "%"+ query+"%", "%"+ query+"%",  "%"+ query+"%", start_price, end_price))
    else: 
      cur.execute(sql, (no_adults, no_children, room_num, "%"+ query+"%", "%"+ query+"%",  "%"+ query+"%"))
    
    res = cur.fetchall()
    arr = []
    for item in res:
        arr.append(convertToDict(item, ["id", "name", "rating", "price", "image_url", "lat", "long","city", "desc", "category"]))
    return arr

def get_room_details(cur, id:int):
    sql = """
      SELECT room.*, json_agg(ri.image_url) as room_images FROM ROOM
      inner join (select image_url, room_id from room_image where rank = 1) ri on ROOM.id = ri.room_id
      where hotel_id = %s
      GROUP BY  room.id;
  """
    cur.execute(sql, (id,))
    res = cur.fetchall()
    arr = []
    for item in res:
        arr.append(convertToDict(item, ["id", "name", "bed", "size", "num_rooms", "no_adult", "no_child","price", "hotel_id", "room_images"]))
    return arr

def get_hotel_details(cur, id:int, email:str):
    select_key = ["id", "name", "address", "desc", "rating", "city",  "starting_price", "agoda_url", "lat","lng","category","hotel_images"]
    sqlTuple = []
    sql = "SELECT hotel.*, json_agg(hi.image_url) "
    if email:
        sql += " , CASE WHEN li.hotel_id IS NOT NULL THEN TRUE ELSE FALSE END  AS isLiked"
        select_key.append("isLiked")
    sql += " from hotel"

    if email:
        sql += " left join  (select * from liked_hotel where user_email = %s) as li on li.hotel_id = hotel.id"
        sqlTuple.append(email)
    sql += " inner join (SELECT * FROM hotel_image ORDER BY rank) hi  on hotel.id = hi.hotel_id where hotel.id =%s group by hotel.id"
    sqlTuple.append(id)

    if email:
        sql += " , li.hotel_id"
    sql+= ";"
    print(sql)
    cur.execute(sql, tuple(sqlTuple))
    res = cur.fetchone()
    return convertToDict(res, select_key)


def does_hotel_exist(cur, id:int):
    sql = "SELECT COUNT(hotel.id) from hotel where id = %s"

    cur.execute(sql, (id,))
    res = cur.fetchone()
    return res[0] == 1

def does_room_exist(cur, id:int):
    sql = "SELECT COUNT(room.id) from room where id = %s"
    cur.execute(sql, (id,))
    res = cur.fetchone()
    return res[0] == 1

def get_room_minor_details(cur, id:int):
    sql = "SELECT * from room where id = %s"
    cur.execute(sql, (id,))
    res = cur.fetchone()
    return convertToDict(res, ["id", "name", "bed", "size", "room_count", "no_adult", "no_child", "price", "hotel_id"])

def get_room_count(cur, id:int):
    sql = "SELECT room_count from room where id = %s"
    cur.execute(sql, (id,))
    res = cur.fetchone()
    return res[0]

def get_hotel_by_category(cur, category:str, limit:int, email:str):
    select_key = ["id", "name", "rating", "price", "image_url", "lat", "long","city", "desc", "category", "image_url"]

    sql = """SELECT  hotel.id, hotel.name, hotel.rating, hotel.starting_price, hi.image_url, hotel.latitude, hotel.longtitude, hotel.city, hotel.description, hotel.category, hi.image_url"""
    if email: 
        sql += " , CASE WHEN lh.hotel_id IS NOT NULL THEN TRUE ELSE FALSE END AS isLiked"
        select_key.append("isLiked")
    sql += " FROM hotel inner join (SELECT image_url, hotel_id FROM hotel_image where rank = 1) as hi on hi.hotel_id = hotel.id"
    
    sqlTuple = []
    
    if email: 
        sql += " left join (select hotel_id from liked_hotel where user_email =%s) lh on hotel.id = lh.hotel_id"
        sqlTuple.append(email)

    if category.lower() != "all":
        sql += " where category=%s"
        sqlTuple.append(category)
    sql+= " ORDER BY hotel.rating DESC LIMIT %s;"
    sqlTuple.append(limit)
     
    cur.execute(sql, tuple(sqlTuple))
    
    res = cur.fetchall()
    arr = []
    for item in res:
        arr.append(convertToDict(item, select_key))
    return arr


def has_user_like_hotel(cur, hotel_id:int, email:str):
    sql = "SELECT * from liked_hotel where user_email = %s and hotel_id = %s;"
    cur.execute(sql, (email, hotel_id))
    res = cur.fetchall()
    return len(res) != 0

def get_landmarks(cur, hotel_id:int):
    sql = "SELECT l.name, lh.distance  FROM landmark_hotel lh inner join landmark l on l.id = lh.landmark_id where hotel_id = %s"
    cur.execute(sql, (hotel_id,))
    res = cur.fetchall()
    arr = []
    for item in res:
        arr.append(convertToDict(item, ["name", "distance"]))
    return arr


def like_hotel(cur, hotel_id:int, email:str):
    sql = "INSERT INTO liked_hotel (user_email, hotel_id) values (%s, %s);"
    cur.execute(sql, (email, hotel_id))

def dislike_hotel(cur, hotel_id:int, email:str):
    sql = "DELETE FROM  liked_hotel where user_email = %s and hotel_id = %s;"
    cur.execute(sql, (email, hotel_id))
    
def get_city(cur, query:str):
    input_data = []
    sql = "SELECT * FROM CITY"
    if query: 
        sql += " WHERE LOWER(name) LIKE %s"
        query = query.lower()
        print(query)
        input_data.append("%" + query + "%")
    sql +=';'
    cur.execute(sql, tuple(input_data))
    res = cur.fetchall()
    arr = []
    for item in res:
        arr.append(convertToDict(item, ["id", "name", "image"]))
    return arr


def update_room_count(cur, roomId : int , no_rooms_booked: int):
    sql = "UPDATE ROOM SET room_count = room_count - %s where id = %s;"
    cur.execute(sql, (no_rooms_booked, roomId))

def getLikedHotels(cur, email:str):
    sql = """
        SELECT hotel.id, hotel.name, hotel.address, hotel.description, hotel.rating, hotel.city, hotel.starting_price, hotel.agoda_url,hotel.latitude, hotel.longtitude, hotel.category, hi.image_url from liked_hotel
        inner join hotel on liked_hotel.hotel_id = hotel.id
        inner join (SELECT * FROM hotel_image WHERE rank = 1) hi on hi.hotel_id = hotel.id
        where liked_hotel.user_email = %s"""
    cur.execute(sql, (email,))
    res = cur.fetchall()
    arr = []
    for item in res:
        arr.append(convertToDict(item, ["id", "name", "address", "desc", "rating", "city", "price", "agoda_url", "lat", "lng", "category", "img"]))
    return arr


def getPopularHotels(cur):
    sql = "SELECT hotel.*, hi.image_url FROM HOTEL inner join (select hotel_id , image_url from hotel_image where rank = 1) hi on HOTEL.id = hi.hotel_id where hotel.city != 'Tokyo' ORDER BY hotel.rating DESC LIMIT 20"
    cur.execute(sql)
    res = cur.fetchall()
    arr = []
    for item in res:
        arr.append(convertToDict(item, ["id", "name", "address", "desc", "rating", "city", "price", "agoda_url", "lat", "lng", "category", "img"]))
    return arr