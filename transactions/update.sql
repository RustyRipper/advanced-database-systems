BEGIN
    DECLARE
        v_min_age              NUMBER := 18;
        v_days_since_reservation NUMBER := 7;
        v_count_updated        NUMBER := 0;
        v_start_date           DATE := TO_DATE('2012-01-01', 'YYYY-MM-DD');
        v_end_date             DATE := TO_DATE('2024-11-01', 'YYYY-MM-DD');
    BEGIN
        UPDATE ClientCar cc
        SET color = CASE
                        WHEN (SELECT TRUNC(MONTHS_BETWEEN(SYSDATE, pu.date_of_birth) / 12)
                              FROM ParkingUser pu
                              WHERE pu.id = cc.client_id) >= v_min_age THEN 'Blue'
                        WHEN cc.client_id IN (
                            SELECT pu.id
                            FROM ParkingUser pu
                            LEFT JOIN Reservation r ON r.user_id = pu.id
                            LEFT JOIN Payment p ON p.reservation_id = r.id
                            WHERE (p.created_at IS NULL OR EXTRACT(YEAR FROM p.created_at) < EXTRACT(YEAR FROM SYSDATE) - 1)
                        ) THEN 'Yellow'
                        WHEN UPPER(cc.brand) = 'TOYOTA' THEN 'Silver'
                        WHEN UPPER(cc.brand) = 'BMW' THEN 'Dark Blue'
                        WHEN UPPER(cc.brand) = 'HONDA' THEN 'Orange'
                        WHEN cc.client_id IN (
                            SELECT r.user_id
                            FROM Reservation r
                            WHERE r.start_date BETWEEN v_start_date AND v_end_date
                        ) THEN 'Purple'
                        WHEN cc.client_id IN (
                            SELECT id FROM ParkingUser WHERE UPPER(role) = 'ADMIN'
                        ) THEN 'Black'
                        ELSE color
                    END
        WHERE EXISTS (SELECT 1 FROM ParkingUser pu WHERE pu.id = cc.client_id);

        v_count_updated := SQL%ROWCOUNT;
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('Liczba zaktualizowanych rekordow: ' || v_count_updated);
    END;
END;
