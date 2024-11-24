SELECT u.id || ' ' || u.firstname || ' ' || u.lastname AS parking_user,
       ps.id                                           AS parking_spot_id,
       COUNT(r.id)                                     AS total_reservations,
       SUM(r.amount)                                   AS total_amount,
       (SELECT COUNT(*)
        FROM Reservation r2
                 Join PARKINGUSER u2 ON r2.user_id = u2.id
                 JOIN ParkingSpot ps2 ON r2.parking_spot_id = ps2.id
                 JOIN Parking pk2 ON pk2.id = ps2.parking_id
        WHERE r2.USER_ID = u.id
          AND pk2.id = :parking_id
          AND ps2.id = ps.id
          AND r2.end_date < CURRENT_TIMESTAMP)         AS past_reservations

FROM Reservation r
         JOIN ParkingUser u ON r.user_id = u.id
         JOIN ParkingSpot ps ON r.parking_spot_id = ps.id
         JOIN Parking pk ON pk.id = ps.parking_id
WHERE pk.id = :parking_id
  AND r.start_date BETWEEN TO_TIMESTAMP(:start_date, 'YYYY-MM-DD HH24:MI:SS')
    AND TO_TIMESTAMP(:end_date, 'YYYY-MM-DD HH24:MI:SS')
GROUP BY u.id, u.firstname, u.lastname, ps.ID
HAVING SUM(r.amount) > 0
ORDER BY total_reservations DESC
