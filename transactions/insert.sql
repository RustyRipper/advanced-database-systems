SELECT *
FROM Reservation r
         JOIN Parkingspot ps ON r.parking_spot_id = ps.id
         JOIN Parking p ON ps.parking_id = p.id
where USER_ID = :user_id
  and PARKING_ID = :parking_id;

INSERT INTO Reservation
(parking_spot_id, user_id, start_date, end_date, amount, active,
 registration_number)
SELECT r.parking_spot_id,
       r.user_id,
       TO_TIMESTAMP(:new_start_date, 'YYYY-MM-DD HH24:MI:SS') AS start_date,
       TO_TIMESTAMP(:new_end_date,
                    'YYYY-MM-DD HH24:MI:SS')                  AS end_date,
       p.cost_rate *
       (24 * (TO_TIMESTAMP(:new_end_date, 'YYYY-MM-DD HH24:MI:SS') -
              TO_TIMESTAMP(:new_start_date,
                           'YYYY-MM-DD HH24:MI:SS'))) + 1     AS amount,
       'Y'                                                    AS active,
       r.registration_number
FROM Reservation r
         JOIN Parkingspot ps ON r.parking_spot_id = ps.id
         JOIN Parking p ON ps.parking_id = p.id
WHERE r.user_id = :user_id
  AND p.id = :parking_id
  AND TRUNC(r.start_date) = TO_DATE(:reference_date, 'YYYY-MM-DD')
  AND ps.active = 'Y'
  AND NOT EXISTS (SELECT 1
                  FROM Reservation r2
                  WHERE r2.parking_spot_id = r.parking_spot_id
                    AND r2.start_date < TO_TIMESTAMP(:new_end_date,
                                                     'YYYY-MM-DD HH24:MI:SS')
                    AND r2.end_date > TO_TIMESTAMP(:new_start_date,
                                                   'YYYY-MM-DD HH24:MI:SS'));


SELECT r.parking_spot_id,
       r.user_id,
       :new_start_date                                                AS start_date,
       :new_end_date                                                  AS end_date,
       p.cost_rate *
       Extract(hour FROM (TO_TIMESTAMP(:new_end_date, 'YYYY-MM-DD HH24:MI:SS') -
                          TO_TIMESTAMP(:new_start_date,
                                       'YYYY-MM-DD HH24:MI:SS'))) + 1 AS amount,
       'Y'                                                            AS active,
       r.registration_number
FROM Reservation r
         JOIN Parkingspot ps ON r.parking_spot_id = ps.id
         JOIN Parking p ON ps.parking_id = p.id
WHERE r.user_id = :user_id
  AND p.id = :parking_id
  AND TRUNC(r.start_date) = TO_DATE(:reference_date, 'YYYY-MM-DD')
  AND ps.active = 'Y'
  AND NOT EXISTS (SELECT 1
                  FROM Reservation r2
                  WHERE r2.parking_spot_id = r.parking_spot_id
                    AND r2.start_date < TO_TIMESTAMP(:new_end_date,
                                                     'YYYY-MM-DD HH24:MI:SS')
                    AND r2.end_date > TO_TIMESTAMP(:new_start_date,
                                                   'YYYY-MM-DD HH24:MI:SS'));
