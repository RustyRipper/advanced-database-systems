SELECT cc.brand,
       cc.color,
       COUNT(r.id) AS total_parking_count,
       (SELECT COUNT(*)
        FROM Reservation r_sub
                 JOIN ClientCar cc_sub
                      ON cc_sub.registration_number = r_sub.registration_number
        WHERE r_sub.user_id = r.user_id
          AND cc_sub.brand = cc.brand
          AND r_sub.start_date BETWEEN TO_TIMESTAMP(:start_date, 'YYYY-MM-DD HH24:MI:SS')  AND TO_TIMESTAMP(:end_date, 'YYYY-MM-DD HH24:MI:SS')
           )       AS user_specific_brand_count,
       (SELECT COUNT(*)
        FROM Reservation r_sub
                 JOIN ClientCar cc_sub
                      ON cc_sub.registration_number = r_sub.registration_number
        WHERE cc_sub.brand = cc.brand
          AND r_sub.start_date BETWEEN TO_TIMESTAMP(:start_date, 'YYYY-MM-DD HH24:MI:SS')  AND TO_TIMESTAMP(:end_date, 'YYYY-MM-DD HH24:MI:SS')
           )       AS overall_brand_parking_count,
       (SELECT COUNT(*)
        FROM Reservation r_sub
        WHERE r_sub.parking_spot_id = r.parking_spot_id
          AND r_sub.start_date BETWEEN TO_TIMESTAMP(:start_date, 'YYYY-MM-DD HH24:MI:SS')  AND TO_TIMESTAMP(:end_date, 'YYYY-MM-DD HH24:MI:SS')
           )       AS parking_spot_total
FROM ClientCar cc
         JOIN
     Reservation r ON cc.registration_number = r.registration_number
         JOIN
     ParkingSpot ps ON r.parking_spot_id = ps.id
         JOIN
     Parking p ON ps.parking_id = p.id
WHERE r.start_date BETWEEN TO_TIMESTAMP(:start_date, 'YYYY-MM-DD HH24:MI:SS')  AND TO_TIMESTAMP(:end_date, 'YYYY-MM-DD HH24:MI:SS')
GROUP BY cc.brand, cc.color, r.user_id, r.parking_spot_id
ORDER BY total_parking_count DESC
