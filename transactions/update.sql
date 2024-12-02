BEGIN
    UPDATE ClientCar cc
    SET color = CASE
                    WHEN (SELECT TRUNC(MONTHS_BETWEEN(SYSDATE, pu.date_of_birth) / 12)
                          FROM ParkingUser pu
                          WHERE pu.id = cc.client_id) >= :p_min_age THEN 'Blue'
                    WHEN cc.client_id IN (
                        SELECT pu.id
                        FROM ParkingUser pu
                        LEFT JOIN Reservation r ON r.user_id = pu.id
                        LEFT JOIN Payment p ON p.reservation_id = r.id
                        WHERE (p.created_at IS NULL OR EXTRACT(YEAR FROM p.created_at) < EXTRACT(YEAR FROM SYSDATE) - 1)
                    ) THEN 'Yellow'
                    WHEN UPPER(cc.brand) = 'TOYOTA' THEN :p_color_toyota
                    WHEN UPPER(cc.brand) = 'BMW' THEN :p_color_bmw
                    WHEN UPPER(cc.brand) = 'HONDA' THEN :p_color_honda
                    WHEN cc.client_id IN (
                        SELECT r.user_id
                        FROM Reservation r
                        WHERE r.start_date >= TRUNC(SYSDATE) - :p_days_since_reservation
                    ) THEN 'Purple'
                    WHEN cc.client_id IN (
                        SELECT id FROM ParkingUser WHERE UPPER(role) = 'ADMIN'
                    ) THEN :p_color_admin
                    ELSE :p_color_default
                END
    WHERE EXISTS (SELECT 1 FROM ParkingUser pu WHERE pu.id = cc.client_id);
    
    DBMS_OUTPUT.PUT_LINE('Liczba zaktualizowanych rekordów: ' || SQL%ROWCOUNT);
    
    ROLLBACK;
END;
