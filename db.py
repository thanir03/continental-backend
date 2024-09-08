select_hotel_query = """
SELECT * FROM (
        SELECT hotel.*, hotel_image.image_url, ROW_NUMBER() OVER (PARTITION BY hotel_id ORDER BY hotel_image.id) AS image_rank
        FROM HOTEL INNER JOIN HOTEL_IMAGE ON HOTEL_IMAGE.hotel_id = HOTEL.id
) as hotel_data where image_rank = 1;
"""