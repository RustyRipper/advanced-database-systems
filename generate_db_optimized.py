import csv
import random
from datetime import datetime, timedelta
from faker import Faker
import string
from concurrent.futures import ThreadPoolExecutor

fake = Faker()

# Constants
NUM_PARKING = 100
NUM_USERS = 20000
NUM_CARS = 50000
NUM_SPOTS = 10000
NUM_RESERVATIONS = 300000
NUM_PAYMENTS = 290000
NUM_CHARGES = 290000

def generate_random_datetime(max_years_ago=5):
    random_days_ago = random.randint(0, max_years_ago * 365)
    base_date = datetime.now() - timedelta(days=random_days_ago)
    random_time = timedelta(
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
        microseconds=random.randint(0, 999999)
    )
    return base_date - random_time

def generate_parking_data(num_parking=NUM_PARKING):
    data = []
    for _ in range(num_parking):
        if random.choice([True, False]):
            open_hour = random.choice([6, 7, 8, 9])
            open_time = datetime(2000, 1, 1, open_hour, 0, 0).isoformat()
            close_hour = random.choice([19, 20, 21, 22, 23])
            close_time = datetime(2000, 1, 1, close_hour, 59, 59, 999999).isoformat()
        else:
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
    return [{
        'id': _ + 1,
        'email': fake.unique.email(),
        'date_of_birth': fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'password': fake.password(),
        'role': random.choice(['USER', 'PARKING_MANAGER', 'ADMIN']),
        'parking_id': random.randint(1, num_parking)
    } for _ in range(num_users)]

def generate_client_car_data(num_cars=NUM_CARS, num_users=NUM_USERS):
    return [{
        'id': _ + 1,
        'addition_time': generate_random_datetime(max_years_ago=5).isoformat(),
        'client_id': random.randint(1, num_users),
        'active': random.choice(['Y', 'N']),
        'registration_number': fake.unique.license_plate(),
        'brand': fake.company(),
        'color': fake.color_name()
    } for _ in range(num_cars)]

def generate_parking_spot_data(num_spots=NUM_SPOTS, num_parking=NUM_PARKING):
    data = []
    spot_numbers_by_parking = {parking_id: (0, 1) for parking_id in range(1, num_parking + 1)}
    for _ in range(num_spots):
        parking_id = random.randint(1, num_parking)
        letter_index, spot_number = spot_numbers_by_parking[parking_id]
        letter = string.ascii_uppercase[letter_index]
        
        data.append({
            'id': _ + 1,
            'parking_id': parking_id,
            'active': random.choice(['Y', 'N']),
            'spot_number': f"{letter}{spot_number}"
        })
        
        spot_number += 1
        if spot_number > 9:
            spot_number = 1
            letter_index += 1
        spot_numbers_by_parking[parking_id] = (letter_index, spot_number)
    return data

def generate_reservation_data(num_reservations=NUM_RESERVATIONS, client_cars=None, parking_spot_data=None, parking_data=None):
    cars_by_user = {car['client_id']: [] for car in client_cars}
    for car in client_cars:
        cars_by_user[car['client_id']].append(car)
    spot_to_parking_map = {spot['id']: spot['parking_id'] for spot in parking_spot_data}
    parking_times = {p['id']: (p['open_time'], p['close_time']) for p in parking_data}
    
    data = []
    for _ in range(num_reservations):
        user_id = random.choice(list(cars_by_user.keys()))
        selected_car = random.choice(cars_by_user[user_id])
        registration_number = selected_car['registration_number']
        addition_time = datetime.fromisoformat(selected_car['addition_time'])
        active_spots = [spot for spot in parking_spot_data if spot['active'] == 'Y']
        selected_spot = random.choice(active_spots)
        parking_spot_id = selected_spot['id']
        parking_id = spot_to_parking_map[parking_spot_id]
        open_time_str, close_time_str = parking_times.get(parking_id, (None, None))
        open_time = datetime.fromisoformat(open_time_str) if open_time_str else datetime.min
        close_time = datetime.fromisoformat(close_time_str) if close_time_str else datetime.max
        
        start_time_delta = timedelta(
            hours=random.randint(open_time.hour, close_time.hour),
            minutes=random.randint(open_time.minute, close_time.minute),
            seconds=random.randint(open_time.second, close_time.second)
        )
        start_date = datetime(addition_time.year, addition_time.month, addition_time.day) + timedelta(days=random.randint(0, 31)) + start_time_delta
        end_time_delta = timedelta(
            hours=random.randint(0, close_time.hour - start_date.hour),
            minutes=random.randint(0, close_time.minute - start_date.minute),
            seconds=random.randint(0, close_time.second - start_date.second)
        )
        end_date = start_date + end_time_delta
        
        if start_date.time() >= open_time.time() and end_date.time() <= close_time.time():
            data.append({
                'id': _ + 1,
                'parking_spot_id': parking_spot_id,
                'user_id': user_id,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'amount': round(random.uniform(10.0, 50.0), 2),
                'active': random.choice(['Y', 'N']),
                'registration_number': registration_number
            })
    return data

def generate_payment_data(num_payments=NUM_PAYMENTS, reservations=None):
    return [{
        'id': _ + 1,
        'reservation_id': random.choice(reservations)['id'],
        'amount': round(random.uniform(10.0, 50.0), 2),
        'timestamp': generate_random_datetime(max_years_ago=2).isoformat(),
        'status': random.choice(['COMPLETED', 'PENDING', 'FAILED'])
    } for _ in range(num_payments)]

def generate_stripe_charge_data(num_charges=NUM_CHARGES, payments=None):
    return [{
        'id': _ + 1,
        'payment_id': random.choice(payments)['id'],
        'stripe_charge_id': fake.uuid4(),
        'amount': random.choice(payments)['amount'],
        'status': random.choice(['SUCCEEDED', 'FAILED'])
    } for _ in range(num_charges)]

def save_to_csv(filename, data, fieldnames):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def main():
    with ThreadPoolExecutor() as executor:
        # Generate essential data in sequence
        parking_data = generate_parking_data()
        parking_user_data = generate_parking_user_data()
        client_car_data = generate_client_car_data()
        parking_spot_data = generate_parking_spot_data()

        # Verify essential data
        if not (parking_data and parking_user_data and client_car_data and parking_spot_data):
            raise ValueError("Essential data generation failed.")

        # Generate reservation data
        reservation_data = generate_reservation_data(NUM_RESERVATIONS, client_car_data, parking_spot_data, parking_data)

        # Generate payment and charge data concurrently
        future_payment = executor.submit(generate_payment_data, NUM_PAYMENTS, reservation_data)
        payment_data = future_payment.result()

        future_charge = executor.submit(generate_stripe_charge_data, NUM_CHARGES, payment_data)
        stripe_charge_data = future_charge.result()

        # Save data to CSV files
        save_to_csv('Parking.csv', parking_data, parking_data[0].keys())
        save_to_csv('ParkingUser.csv', parking_user_data, parking_user_data[0].keys())
        save_to_csv('ClientCar.csv', client_car_data, client_car_data[0].keys())
        save_to_csv('ParkingSpot.csv', parking_spot_data, parking_spot_data[0].keys())
        save_to_csv('Reservation.csv', reservation_data, reservation_data[0].keys())
        save_to_csv('Payment.csv', payment_data, payment_data[0].keys())
        save_to_csv('StripeCharge.csv', stripe_charge_data, stripe_charge_data[0].keys())

if __name__ == "__main__":
    main()
