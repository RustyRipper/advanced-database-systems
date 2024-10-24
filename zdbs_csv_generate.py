import csv
import random
import datetime
from faker import Faker

fake = Faker()

# Polish cities with corresponding registration number prefixes and sample zip codes
polish_cities = [
    {"city": "Warsaw", "registration_prefix": "WA", "zip_code": "00-001"},
    {"city": "Kraków", "registration_prefix": "KR", "zip_code": "30-001"},
    {"city": "Łódź", "registration_prefix": "EL", "zip_code": "90-001"},
    {"city": "Wrocław", "registration_prefix": "DW", "zip_code": "50-001"},
    {"city": "Poznań", "registration_prefix": "PO", "zip_code": "60-001"},
    {"city": "Gdańsk", "registration_prefix": "GD", "zip_code": "80-001"},
    {"city": "Szczecin", "registration_prefix": "ZS", "zip_code": "70-001"},
    {"city": "Bydgoszcz", "registration_prefix": "BY", "zip_code": "85-001"},
    {"city": "Lublin", "registration_prefix": "LU", "zip_code": "20-001"},
    {"city": "Katowice", "registration_prefix": "KA", "zip_code": "40-001"}
]
# Create a lookup dictionary for city and corresponding registration prefix
city_to_prefix = {city['city']: city['registration_prefix'] for city in polish_cities}

# Helper functions
def random_date(start, end):
    return start + (end - start) * random.random()

# Generate Parking data
def generate_parking(num_records):
    parking_data = []
    for i in range(num_records):
        city_data = random.choice(polish_cities)
        parking_data.append({
            'id': i + 1,
            'name': fake.company(),
            'city': city_data['city'],
            'street': fake.street_name(),
            'zip_code': city_data['zip_code'],
            'open_time': datetime.datetime.now() - datetime.timedelta(hours=10),
            'close_time': datetime.datetime.now(),
            'cost_rate': round(random.uniform(10, 50), 2)
        })
    return parking_data

# Generate ParkingSpot data
def generate_parking_spot(num_records, parking_data):
    parking_spot_data = []
    for i in range(num_records):
        parking = random.choice(parking_data)
        parking_spot_data.append({
            'id': i + 1,
            'parking_id': parking['id'],
            'active': random.choice(['Y', 'N']),
            'spot_number': fake.unique.license_plate()
        })
    return parking_spot_data

# Generate ParkingUser data
def generate_parking_user(num_records, parking_data):
    parking_user_data = []
    for i in range(num_records):
        parking = random.choice(parking_data)
        parking_user_data.append({
            'id': i + 1,
            'email': fake.unique.email(),
            'date_of_birth': fake.date_of_birth(minimum_age=18, maximum_age=90),
            'firstname': fake.first_name(),
            'lastname': fake.last_name(),
            'password': fake.phone_number(),
            'role': random.choice(['USER', 'PARKING_MANAGER', 'ADMIN']),
            'parking_id': parking['id'] if random.random() > 0.5 else None
        })
    return parking_user_data

# Generate ClientCar data
def generate_client_car(num_records, parking_user_data, parking_data):
    client_car_data = []
    for i in range(num_records):
        user = random.choice(parking_user_data)
        parking = random.choice(parking_data)  # The car registration matches the city of parking
        
        registration_number = f"{city_to_prefix[parking['city']]}{random.randint(10000, 99999)}"
        client_car_data.append({
            'id': i + 1,
            'addition_time': datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 100)),
            'client_id': user['id'],
            'active': random.choice(['Y', 'N']),
            'registration_number': registration_number,
            'brand': random.choice(['Toyota', 'Ford', 'Honda', 'BMW', 'Tesla']),
            'color': random.choice(['Red', 'Blue', 'Green', 'Black', 'White'])
        })
    return client_car_data

# Generate Reservation data
def generate_reservation(num_records, parking_spot_data, parking_user_data, client_car_data, parking_data):
    reservation_data = []
    
    # Create a mapping of parking_id to city name
    parking_id_to_city = {parking['id']: parking['city'] for parking in parking_data}
    
    for i in range(num_records):
        user = random.choice(parking_user_data)
        car = random.choice(client_car_data)
        
        # Filter spots in the city that match the car's registration prefix
        corresponding_city_parking_spots = [
            spot for spot in parking_spot_data
            if city_to_prefix[parking_id_to_city[spot['parking_id']]] == car['registration_number'][:2]
        ]
        
        # 90% of the time, reserve in the corresponding city, otherwise random
        if random.random() < 0.9 and corresponding_city_parking_spots:
            parking_spot = random.choice(corresponding_city_parking_spots)
        else:
            parking_spot = random.choice(parking_spot_data)
        
        start_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))
        end_date = start_date + datetime.timedelta(hours=random.randint(1, 12))
        reservation_data.append({
            'id': i + 1,
            'parking_spot_id': parking_spot['id'],
            'user_id': user['id'],
            'start_date': start_date,
            'end_date': end_date,
            'amount': round(random.uniform(20, 200), 2),
            'active': random.choice(['Y', 'N']),
            'registration_number': car['registration_number']
        })
    
    return reservation_data

# Generate Payment data
def generate_payment(num_records, reservation_data):
    payment_data = []
    for i in range(num_records):
        reservation = random.choice(reservation_data)
        payment_data.append({
            'id': i + 1,
            'reservation_id': reservation['id'],
            'created_at': datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30)),
            'card_number': fake.credit_card_number(),
            'cvc': fake.credit_card_security_code(),
            'exp_month': f'{random.randint(1, 12):02}',
            'exp_year': f'{random.randint(2023, 2030)}',
            'token': fake.unique.uuid4()
        })
    return payment_data

# Generate StripeCharge data
def generate_stripe_charge(num_records, payment_data, reservation_data):
    stripe_charge_data = []
    for i in range(num_records):
        payment = random.choice(payment_data)
        reservation = random.choice(reservation_data)
        stripe_charge_data.append({
            'id': i + 1,
            'charge_id': fake.unique.uuid4(),
            'created_at': datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30)),
            'reservation_id': reservation['id'],
            'payment_id': payment['id'],
            'amount': reservation['amount'],
            'success': random.choice(['SUCCESS', 'FAILED']),
            'currency': 'PLN',
            'message': fake.sentence()
        })
    return stripe_charge_data

# Write data to CSV files with UTF-8 encoding
def write_csv(filename, data, fieldnames):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Main function to generate data and write to CSVs
def main():
    parking_data = generate_parking(10)
    parking_spot_data = generate_parking_spot(30, parking_data)
    parking_user_data = generate_parking_user(20, parking_data)
    client_car_data = generate_client_car(15, parking_user_data, parking_data)
    reservation_data = generate_reservation(20, parking_spot_data, parking_user_data, client_car_data, parking_data)
    payment_data = generate_payment(20, reservation_data)
    stripe_charge_data = generate_stripe_charge(10, payment_data, reservation_data)

    write_csv('Parking.csv', parking_data, parking_data[0].keys())
    write_csv('ParkingSpot.csv', parking_spot_data, parking_spot_data[0].keys())
    write_csv('ParkingUser.csv', parking_user_data, parking_user_data[0].keys())
    write_csv('ClientCar.csv', client_car_data, client_car_data[0].keys())
    write_csv('Reservation.csv', reservation_data, reservation_data[0].keys())
    write_csv('Payment.csv', payment_data, payment_data[0].keys())
    write_csv('StripeCharge.csv', stripe_charge_data, stripe_charge_data[0].keys())

if __name__ == "__main__":
    main()
