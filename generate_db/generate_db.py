import csv
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()


def generate_parking_data(num_parking=100):
    data = []
    for _ in range(num_parking):
        data.append({
            'id': _ + 1,
            'name': fake.unique.company(),
            'city': fake.city(),
            'street': fake.street_name(),
            'zip_code': str(fake.zipcode()),
            'open_time': datetime.now().isoformat(),
            'close_time': (datetime.now() + timedelta(hours=8)).isoformat(),
            'cost_rate': round(random.uniform(1.5, 5.0), 2)
        })
    return data


def generate_parking_user_data(num_users=20000, num_parking=100):
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


def generate_client_car_data(num_cars=50000, num_users=20000):
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


def generate_parking_spot_data(num_spots=10000, num_parking=100):
    data = []
    for _ in range(num_spots):
        data.append({
            'id': _ + 1,
            'parking_id': random.randint(1, num_parking),
            'active': random.choice(['Y', 'N']),
            'spot_number': fake.unique.uuid4()
        })
    return data


def generate_reservation_data(num_reservations=300000, num_spots=10000,
                              num_users=20000):
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


def generate_payment_data(num_payments=300000, num_reservations=300000):
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


def generate_stripe_charge_data(num_charges=300000, num_reservations=300000,
                                num_payments=300000):
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
