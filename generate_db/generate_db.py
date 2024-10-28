import csv
import random
from datetime import datetime, timedelta
from faker import Faker
import string
import copy

fake = Faker()

NUM_PARKING = 100
NUM_USERS = 20000
NUM_CARS = 50000
NUM_SPOTS = 10000
NUM_RESERVATIONS = 300000
NUM_PAYMENTS = 290000
NUM_CHARGES = 290000

def generate_random_datetime(max_years_ago=5):
    # Wygeneruj losową datę sprzed maksymalnie 5 lat
    random_days_ago = random.randint(0, max_years_ago * 365)
    base_date = datetime.now() - timedelta(days=random_days_ago)
    random_time = timedelta(
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
        microseconds=random.randint(0, 999999)
    )
    
    random_datetime = base_date - random_time
    return random_datetime

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
            # Wygeneruj datę dodania samochodu sprzed maksymalnie 5 lat
            'addition_time': generate_random_datetime(max_years_ago=5).isoformat(), 
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


def generate_reservation_data(num_reservations=NUM_RESERVATIONS, client_cars=None, parking_spot_data=None, parking_data=None):
    if client_cars is None:
        raise ValueError("Client cars data must be provided.")
    if parking_spot_data is None:
        raise ValueError("Parking spot data must be provided.")
    if parking_data is None:
        raise ValueError("Parking data must be provided.")

    # Upewnij się że początek i koniec rezerwacji mieszczą się w godzinach otwarcia/zamknięcia parkingu
    cars_by_user = {}
    for car in client_cars:
        user_id = car['client_id']
        if user_id not in cars_by_user:
            cars_by_user[user_id] = []
        cars_by_user[user_id].append(car)

    # Słownik mapującym parking spot ID do parking ID
    spot_to_parking_map = {spot['id']: spot['parking_id'] for spot in parking_spot_data}

    # Słownik mapujący godziny odtwarcia parkingu
    parking_times = {p['id']: (p['open_time'], p['close_time']) for p in parking_data}

    data = []
    for _ in range(num_reservations):
        # Wybierz samochód jednego z userów
        user_id = random.choice(list(cars_by_user.keys()))
        user_cars = cars_by_user[user_id]
        selected_car = random.choice(user_cars)
        registration_number = selected_car['registration_number']
        
        addition_time = datetime.fromisoformat(selected_car['addition_time'])
        min_start_date = addition_time

        # Wybierz Parking Spot usera
        active_spots = [spot for spot in parking_spot_data if spot['active'] == 'Y']
        selected_spot = random.choice(active_spots)
        parking_spot_id = selected_spot['id']
        parking_id = spot_to_parking_map[parking_spot_id]
        
        open_time_str, close_time_str = parking_times.get(parking_id, (None, None))
        open_time = datetime.fromisoformat(open_time_str) if open_time_str else datetime.min
        close_time = datetime.fromisoformat(close_time_str) if close_time_str else datetime.max

        # Rozpoczęcie jest między otwarciem a zamknięciem
        start_time_delta = timedelta(
            hours=random.randint(open_time.hour, close_time.hour),
            minutes=random.randint(open_time.minute, close_time.minute),
            seconds=random.randint(open_time.second, close_time.second)
        )
        start_date = datetime(min_start_date.year, min_start_date.month, min_start_date.day) + timedelta(days=random.randint(0, 31)) + start_time_delta

        # Koniec rezerwacji przed zamknięciem parkingu
        end_time_delta = timedelta(
            hours=random.randint(0, close_time.hour - start_date.hour),
            minutes=random.randint(0, close_time.minute - start_date.minute),
            seconds=random.randint(0, close_time.second - start_date.second)
        )
        end_date = start_date + end_time_delta

        # Upewnij się że start rezerwacji jest po otwarciu, a koniec przed zamknięciem
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
        else:
            print("RESRVATION ERROR")
    
    return data


def generate_payment_data(num_payments=NUM_PAYMENTS, reservations=None):
    if reservations is None:
        raise ValueError("Reservations data must be provided.")

    # Nie może być więcej płatności niż rezerwacji
    num_payments = min(num_payments, len(reservations))
    
     # Create a copy of the reservations to avoid modifying the original list
    reservations_copy = copy.deepcopy(reservations)
    
    # Potasuj rezerwacje
    random.shuffle(reservations_copy)
    selected_reservations = reservations_copy[:num_payments]

    data = []
    for i, reservation in enumerate(selected_reservations):
        # Dla wybranych rezerwacji wygeneruj płatność
        reservation_id = reservation['id']
        start_date = datetime.fromisoformat(reservation['start_date'])
        
        # Data płatności jest max 7 dni przed datą rezerwacji start_date
        payment_date = start_date - timedelta(
            days=random.randint(0, 6),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
            microseconds=random.randint(0, 999999)
        )
        
        exp_date = fake.credit_card_expire().split('/')
        data.append({
            'id': i + 1,
            'reservation_id': reservation_id,
            'created_at': payment_date.isoformat(),
            'card_number': fake.credit_card_number(),
            'cvc': fake.credit_card_security_code(),
            'exp_month': exp_date[0],
            'exp_year': '20' + exp_date[1],
            'token': fake.unique.uuid4()
        })
    
    return data

def generate_stripe_charge_data(payments=None):
    if payments is None:
        raise ValueError("Payments data must be provided.")

    data = []
    for payment in payments:
        # Data stripe charge pojawia się maksymalnie minutę przed payment
        payment_date = datetime.fromisoformat(payment['created_at'])
        charge_date = payment_date - timedelta(
            seconds=random.randint(0, 59),
            microseconds=random.randint(0, 999999)
        )
        
        data.append({
            'id': payment['id'],
            'charge_id': fake.unique.uuid4(),
            'created_at': charge_date.isoformat(),
            'reservation_id': payment['reservation_id'],
            'payment_id': payment['id'],
            'amount': round(random.uniform(10.0, 50.0), 2),
            'success': random.choice(['SUCCESS', 'FAILURE']),
            'currency': 'USD',
            'message': 'test message'
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
    reservation_data = generate_reservation_data(client_cars=client_car_data, parking_data=parking_data, parking_spot_data=parking_spot_data)
    payment_data = generate_payment_data(reservations=reservation_data)
    stripe_charge_data = generate_stripe_charge_data(payments=payment_data)

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
