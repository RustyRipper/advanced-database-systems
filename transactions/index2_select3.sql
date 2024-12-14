CREATE BITMAP INDEX idx_bitmap_select3_date
    ON Reservation (parking_spot_id, start_date, end_date)