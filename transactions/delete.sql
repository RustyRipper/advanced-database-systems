DELETE
FROM Reservation r
WHERE
    ( r.end_date
    > TO_TIMESTAMP(:discard_date_min, 'YYYY-MM-DD HH24:MI:SS') ) AND
    ( r.end_date
    < TO_TIMESTAMP(:discard_date_max, 'YYYY-MM-DD HH24:MI:SS') )
   OR r.id IN (
    SELECT r2.id
    FROM
    Reservation r2
    JOIN StripeCharge sc ON r2.id = sc.reservation_id
    WHERE
    sc.success = 'FAILURE'
    )
   OR r.parking_spot_id IN (
    SELECT ps.id
    FROM
    ParkingSpot ps
    WHERE
    ps.active = 'N'
    );
