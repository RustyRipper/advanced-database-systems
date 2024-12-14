CREATE INDEX idx_btree
    ON Reservation (user_id, parking_spot_id, start_date);