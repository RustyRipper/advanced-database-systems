
ALTER SYSTEM FLUSH SHARED_POOL;
ALTER SYSTEM FLUSH BUFFER_CACHE;
DROP INDEX idx_reservation_parking_spot_id;
DROP INDEX idx_parkingspot_active;

EXPLAIN PLAN FOR
SELECT cc.brand,
       cc.color,
       COUNT(r.id) AS total_parking_count,
       (SELECT COUNT(*)
        FROM Reservation r_sub
                 JOIN ClientCar cc_sub
                      ON cc_sub.registration_number = r_sub.registration_number
        WHERE r_sub.user_id = r.user_id
          AND cc_sub.brand = cc.brand
          AND r_sub.start_date BETWEEN '2020-05-01 12:12:12'  AND '2020-05-12 12:12:12'
           )       AS user_specific_brand_count,
       (SELECT COUNT(*)
        FROM Reservation r_sub
                 JOIN ClientCar cc_sub
                      ON cc_sub.registration_number = r_sub.registration_number
        WHERE cc_sub.brand = cc.brand
          AND r_sub.start_date BETWEEN '2020-05-01 12:12:12'  AND '2020-05-12 12:12:12'
           )       AS overall_brand_parking_count,
       (SELECT COUNT(*)
        FROM Reservation r_sub
        WHERE r_sub.parking_spot_id = r.parking_spot_id
          AND r_sub.start_date BETWEEN '2020-05-01 12:12:12'  AND '2020-05-12 12:12:12'
           )       AS parking_spot_total
FROM ClientCar cc
         JOIN
     Reservation r ON cc.registration_number = r.registration_number
         JOIN
     ParkingSpot ps ON r.parking_spot_id = ps.id
         JOIN
     Parking p ON ps.parking_id = p.id
WHERE r.start_date BETWEEN '2020-05-01 12:12:12'  AND '2020-05-12 12:12:12'
GROUP BY cc.brand, cc.color, r.user_id, r.parking_spot_id
ORDER BY total_parking_count DESC;
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
