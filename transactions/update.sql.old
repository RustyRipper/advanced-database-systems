UPDATE Reservation r
SET r.active = 'N',
    r.amount = r.amount * 0.9
WHERE r.user_id IN (
    SELECT u.id
    FROM ParkingUser u
    WHERE u.active = 'N')
  AND r.registration_number IN (
    SELECT c.registration_number
    FROM ClientCar c
    WHERE c.active = 'N')
  AND r.end_date < SYSDATE
  AND r.registration_number IN (
    SELECT cc.registration_number
    FROM ClientCar cc
    WHERE cc.parking_spot_id IN (
        SELECT p.parking_spot_id
        FROM Parking p
        WHERE p.parking_id = :parking_id)
      AND cc.parking_start_time BETWEEN :start_date AND :end_date
      AND (SYSDATE - cc.parking_start_time) * 24 > (
        SELECT p.max_parking_duration
        FROM Parking p
        WHERE p.parking_spot_id = cc.parking_spot_id
        )
      AND cc.status != 'Wydłużone parkowanie'
    );
