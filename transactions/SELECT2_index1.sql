CREATE INDEX idx_reservation_user_parking_startdate_btree ON Reservation(user_id, parking_spot_id, start_date);
