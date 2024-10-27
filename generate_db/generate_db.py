import csv
import random
from datetime import datetime, timedelta
from faker import Faker
import string

fake = Faker()

NUM_PARKING = 100
NUM_USERS = 20000
NUM_CARS = 50000
NUM_SPOTS = 10000
NUM_RESERVATIONS = 300000
NUM_PAYMENTS = 300000
NUM_CHARGES = 300000

def generate_parking_data(num_parking=NUM_PARKING):
    data = []
    for _ in range(num_parking):

        # Czas otwarcia parkingu - 50% szansy na parking będący całodobowy, 50% szansy na parking o określonych godzinach otwarcia
        if random.choice([True, False]):
            # Przypadek 1: Losowe godziny otwarcia/zamknięcia
            open_hour = random.choice([6, 7, 8, 9])
            open_time = datetime(2000, 1, 1, open_hour, 0, 0).isoformat()
            
            close_hour = random.choice([19, 20, 21, 22, 23])
            close_time = datetime(2000, 1, 1, close_hour, 59, 59, 999999).isoformat()
        
        else:
            # Przypadek 2: Parking całodobowy
            open_time = datetime(2000, 1, 1, 0, 0, 0).isoformat()
            close_time = datetime(2000, 1, 1, 23, 59, 59, 999999).isoformat()
        
        data.append({
            'id': _ + 1,
            'name': fake.unique.company(),
            'city': fake.city(),
            'street': fake.street_name(),
            'zip_code': str(fake.zipcode()),
            'open_time': open_time,
            'close_time': close_time,
            'cost_rate': round(random.uniform(1.5, 5.0), 2)
        })
    return data


def generate_parking_user_data(num_users=NUM_USERS, num_parking=NUM_PARKING):
    data = []
    for _ in range(num_users):
        data.append({
            'id': _ + 1,
            'email': fake.unique.email(),
            'date_of_birth': fake.date_of_birth(minimum_age=18,
                                                maximum_age=80).isoformat(),
            'firstname': fake.first_name(),
            'lastname': fake.last_name(),
            'password': fake.password(),
            'role': random.choice(['USER', 'PARKING_MANAGER', 'ADMIN']),
            'parking_id': random.randint(1, num_parking)
        })
    return data


def generate_client_car_data(num_cars=NUM_CARS, num_users=NUM_USERS):
    data = []
    for _ in range(num_cars):
        data.append({
            'id': _ + 1,
            'addition_time': datetime.now().isoformat(),
            'client_id': random.randint(1, num_users),
            'active': random.choice(['Y', 'N']),
            'registration_number': fake.unique.license_plate(),
            'brand': fake.company(),
            'color': fake.color_name()
        })
    return data


def generate_parking_spot_data(num_spots=NUM_SPOTS, num_parking=NUM_PARKING):
    data = []
    for _ in range(num_spots):
        data.append({
            'id': _ + 1,
            'parking_id': random.randint(1, num_parking),
            'active': random.choice(['Y', 'N']),
            'spot_number': 'temp'
        })
    # Zmodyfikuj spot number aby odpowiadał A1, A2, ..., B1 itd dla danego parkingu
    # Numer ostatniego numeru i litery miejsca wpisanego do parkingu
    spot_numbers_by_parking = {parking_id: (0, 1) for parking_id in range(1, num_parking + 1)}
    
    # Zamień wpis "temp" na miejsce typu A1, C3
    for entry in data:
        parking_id = entry['parking_id']
        
        letter_index, spot_number = spot_numbers_by_parking[parking_id]
        letter = string.ascii_uppercase[letter_index]
        
        entry['spot_number'] = f"{letter}{spot_number}"
        
        spot_number += 1
        if spot_number > 9:
            spot_number = 1
            letter_index += 1
        
        spot_numbers_by_parking[parking_id] = (letter_index, spot_number)
    
    return data


def generate_reservation_data(num_reservations=NUM_RESERVATIONS, num_spots=NUM_SPOTS,
                              num_users=NUM_USERS):
    data = []
    for _ in range(num_reservations):
        start_date = datetime.now()
        end_date = start_date + timedelta(days=1)
        data.append({
            'id': _ + 1,
            'parking_spot_id': random.randint(1, num_spots),
            'user_id': random.randint(1, num_users),
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'amount': round(random.uniform(10.0, 50.0), 2),
            'active': random.choice(['Y', 'N']),
            'registration_number': fake.unique.license_plate()
        })
    return data


def generate_payment_data(num_payments=NUM_PAYMENTS, num_reservations=NUM_RESERVATIONS):
    data = []
    for _ in range(num_payments):
        exp_date = fake.credit_card_expire().split('/')
        data.append({
            'id': _ + 1,
            'reservation_id': random.randint(1, num_reservations),
            'created_at': datetime.now().isoformat(),
            'card_number': fake.credit_card_number(),
            'cvc': fake.credit_card_security_code(),
            'exp_month': exp_date[0],
            'exp_year': '20' + exp_date[1],
            'token': fake.unique.uuid4()
        })
    return data


def generate_stripe_charge_data(num_charges=300000, num_reservations=NUM_RESERVATIONS,
                                num_payments=NUM_PAYMENTS):
    data = []
    for _ in range(num_charges):
        data.append({
            'id': _ + 1,
            'charge_id': fake.unique.uuid4(),
            'created_at': datetime.now().isoformat(),
            'reservation_id': random.randint(1, num_reservations),
            'payment_id': random.randint(1, num_payments),
            'amount': round(random.uniform(10.0, 50.0), 2),
            'success': random.choice(['true', 'false']),
            'currency': 'USD',
            'message': 'Transaction completed successfully.'
        })
    return data


def save_to_csv(filename, data, fieldnames):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    # Generate data in the correct order
    parking_data = generate_parking_data()
    parking_user_data = generate_parking_user_data()
    client_car_data = generate_client_car_data()
    parking_spot_data = generate_parking_spot_data()
    reservation_data = generate_reservation_data()
    payment_data = generate_payment_data()
    stripe_charge_data = generate_stripe_charge_data()

    # Save to CSV
    save_to_csv('Parking.csv', parking_data, parking_data[0].keys())
    save_to_csv('ParkingUser.csv', parking_user_data,
                parking_user_data[0].keys())
    save_to_csv('ClientCar.csv', client_car_data, client_car_data[0].keys())
    save_to_csv('ParkingSpot.csv', parking_spot_data,
                parking_spot_data[0].keys())
    save_to_csv('Reservation.csv', reservation_data, reservation_data[0].keys())
    save_to_csv('Payment.csv', payment_data, payment_data[0].keys())
    save_to_csv('StripeCharge.csv', stripe_charge_data,
                stripe_charge_data[0].keys())
