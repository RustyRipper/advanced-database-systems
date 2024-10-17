INSERT INTO Reservation
(parking_spot_id, user_id, start_date, end_date, amount, active,
 registration_number)
SELECT r.parking_spot_id,
       r.user_id,
       :new_start_date + (r.start_date - Trunc(r.start_date)) AS start_date,
       :new_end_date + (r.end_date - Trunc(r.end_date))       AS end_date,
       p.cost_rate * (
           Extract(hour FROM (:new_end_date - :new_start_date))
           )                                                  AS amount,
       'Y'                                                    AS active,
       r.registration_number
FROM Reservation r
         JOIN Parkingspot ps ON r.parking_spot_id = ps.id
         JOIN Parking p ON ps.parking_id = p.id
WHERE r.user_id = :user_id
  AND p.id = :parking_id
  AND Trunc(r.start_date) = Trunc(:reference_date)
  AND ps.active = 'Y'
  AND NOT EXISTS (SELECT 1
                  FROM Reservation r2
                  WHERE r2.parking_spot_id = r.parking_spot_id
                    AND r2.start_date < :new_end_date
                    AND r2.end_date > :new_start_date
                    AND r2.active = 'Y');
