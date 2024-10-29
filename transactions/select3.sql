SELECT u.firstname || ' ' || u.lastname   AS user_name,
       ps.spot_number                     AS parking_spot,
       COUNT(r.id)                        AS total_reservations,
       SUM(r.amount)                      AS total_amount,
       (SELECT COUNT(*)
        FROM Reservation r2
        WHERE r2.parking_spot_id = ps.id
          AND r2.end_date < r.start_date) AS past_reservations,
       (SELECT CASE
                   WHEN COUNT(r3.id) > 0 THEN 'ACTIVE'
                   ELSE 'NONE'
                   END
        FROM Reservation r3
        WHERE r3.user_id = u.id
          AND r3.start_date <= r.end_date
          AND r3.end_date >= r.start_date
          AND r3.id != r.id)              AS concurrent_reservations
FROM Reservation r
         JOIN ParkingUser u ON r.user_id = u.id
         JOIN ParkingSpot ps ON r.parking_spot_id = ps.id
         JOIN Parking pk ON pk.id = ps.parking_id
WHERE pk.id = :parking_id
  AND r.start_date BETWEEN :start_date
    AND :end_date
GROUP BY u.firstname, u.lastname, ps.spot_number
HAVING SUM(r.amount) > 0
ORDER BY total_amount DESC;