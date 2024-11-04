SELECT cc.brand                   AS car_brand,
       (SELECT COUNT(DISTINCT r.id)
        FROM Reservation r
                 JOIN ParkingSpot ps ON r.parking_spot_id = ps.id
                 JOIN Parking p ON ps.parking_id = p.id
                 JOIN ClientCar ccc
                      ON r.registration_number = ccc.registration_number
                 JOIN User u ON r.user_id = u.id
        WHERE ccc.brand = cc.brand
          AND r.start_date >= TO_TIMESTAMP(:min_date, 'YYYY-MM-DD HH24:MI:SS') 
          AND u.role NOT IN ('PARKING_MANAGER', 'ADMIN')
          AND ps.active = 'Y'
          AND ccc.registration_number NOT LIKE 'WR%'
          AND p.id = :parking_id) AS total_reservations,
       (SELECT SUM(sc.amount)
        FROM StripeCharge sc
                 JOIN Reservation r ON sc.reservation_id = r.id
                 JOIN ParkingSpot ps ON r.parking_spot_id = ps.id
                 JOIN Parking p ON ps.parking_id = p.id
                 JOIN ClientCar ccc
                      ON r.registration_number = ccc.registration_number
        WHERE ccc.brand = cc.brand
          AND sc.success = 'SUCCESS'
          AND sc.amount > :min_amount
          AND r.start_date >= TO_TIMESTAMP(:min_date, 'YYYY-MM-DD HH24:MI:SS') 
          AND ps.active = 'Y'
          AND ccc.registration_number NOT LIKE 'WR%'
          AND p.id = :parking_id) AS total_amount
FROM ClientCar cc
GROUP BY cc.brand;
