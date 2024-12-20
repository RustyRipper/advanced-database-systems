CREATE TABLE Parking
(
    id          NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    name        VARCHAR2(100),
    city        VARCHAR2(100),
    street      VARCHAR2(100),
    zip_code    VARCHAR2(20),
    open_time   TIMESTAMP,
    close_time  TIMESTAMP,
    cost_rate   NUMBER(10, 2)
);

CREATE TABLE ParkingSpot
(
    id          NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    parking_id  NUMBER NOT NULL,
    active      CHAR(1) CHECK (active IN ('Y', 'N')),
    spot_number VARCHAR2(50),
    CONSTRAINT fk_parking FOREIGN KEY (parking_id) REFERENCES Parking (id) ON DELETE CASCADE,
    CONSTRAINT unique_spot_per_parking UNIQUE (parking_id, spot_number)
);

CREATE TABLE ParkingUser
(
    id                   NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    email                VARCHAR2(255) UNIQUE NOT NULL,
    date_of_birth        DATE,
    firstname            VARCHAR2(100),
    lastname             VARCHAR2(100),
    password             VARCHAR2(255)        NOT NULL,
    role                 VARCHAR2(20) CHECK (Role IN ('USER', 'PARKING_MANAGER', 'ADMIN')),
    parking_id           NUMBER,
    CONSTRAINT fk_parking_user FOREIGN KEY (parking_id) REFERENCES Parking (id) ON DELETE CASCADE
);

CREATE TABLE ClientCar
(
    id                  NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    addition_time       TIMESTAMP,
    client_id           NUMBER NOT NULL,
    active              CHAR(1) CHECK (active IN ('Y', 'N')),
    registration_number VARCHAR2(50) UNIQUE,
    brand               VARCHAR2(50),
    color               VARCHAR2(50),
    CONSTRAINT fk_client FOREIGN KEY (client_id) REFERENCES ParkingUser (id) ON DELETE CASCADE
);

CREATE TABLE Reservation
(
    id                  NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    parking_spot_id     NUMBER    NOT NULL,
    user_id             NUMBER    NOT NULL,
    start_date          TIMESTAMP NOT NULL,
    end_date            TIMESTAMP NOT NULL,
    amount              NUMBER(10, 2),
    active              CHAR(1) CHECK (active IN ('Y', 'N')),
    registration_number VARCHAR2(50),
    CONSTRAINT fk_parking_spot FOREIGN KEY (parking_spot_id) REFERENCES ParkingSpot (id) ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES ParkingUser (id) ON DELETE CASCADE
);

CREATE TABLE Payment
(
    id             NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    reservation_id NUMBER NOT NULL,
    created_at     TIMESTAMP,
    card_number    VARCHAR2(19),
    cvc            VARCHAR2(4),
    exp_month      VARCHAR2(2),
    exp_year       VARCHAR2(4),
    token          VARCHAR2(255) UNIQUE,
    CONSTRAINT fk_reservation FOREIGN KEY (reservation_id) REFERENCES Reservation (id) ON DELETE CASCADE
);

CREATE TABLE StripeCharge
(
    id             NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    charge_id      VARCHAR2(100) UNIQUE,
    created_at     TIMESTAMP,
    reservation_id NUMBER,
    payment_id     NUMBER NOT NULL,
    amount         NUMBER(10, 2),
    success        VARCHAR2(10),
    currency       VARCHAR2(10),
    message        VARCHAR2(255),
    CONSTRAINT fk_reservation_stripe FOREIGN KEY (reservation_id) REFERENCES Reservation (id) ON DELETE CASCADE,
    CONSTRAINT fk_payment FOREIGN KEY (payment_id) REFERENCES Payment (id) ON DELETE CASCADE
);

