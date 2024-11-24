import csv
from datetime import datetime

# Function to check if a string is a date in the format YYYY-MM-DD
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Function to check if a string is a timestamp in the format YYYY-MM-DD HH:MI:SS with optional microseconds
def is_valid_timestamp(timestamp_str):
    try:
        # First try to parse with microseconds
        datetime.strptime(timestamp_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        return False

# Function to check if a value is a number
def is_number(value):
    try:
        float(value)  # Try converting to a float (handles both integers and decimals)
        return True
    except ValueError:
        return False

# Function to convert a list of rows to Oracle INSERT ALL statement (with up to 100 rows)
def convert_to_grouped_insert_all(table_name, data_rows, columns):
    col_names = ', '.join(columns)
    
    # Generate the individual INSERT ALL clauses for all rows, handling date and timestamp fields
    values_list = []
    for data in data_rows:
        values = []
        for col, value in zip(columns, data):
            if value is None or value == '':
                values.append('NULL')
            else:
                # Handle date and timestamp fields based on detected format
                if ('date' in col.lower() or 'time' in col.lower() or 'created_at' in col.lower()) and is_valid_timestamp(value):
                    value = value.split('.')[0]  # Remove microseconds
                    values.append(f"TO_TIMESTAMP('{value}', 'YYYY-MM-DD HH24:MI:SS')")
                elif is_number(value):
                    # If the value is a number, don't wrap it in quotes
                    values.append(value)
                else:
                    # For other values, escape single quotes and handle normally
                    values.append("'" + str(value).replace("'", "''") + "'")
        
        values_list.append(f"INTO {table_name} ({col_names}) VALUES ({', '.join(values)})")
    
    # Join all values into a single multi-row INSERT ALL statement
    return f"INSERT ALL\n" + "\n".join(values_list) + "\nSELECT 1 FROM DUAL;"

# Read a CSV file and generate grouped INSERT ALL statements (max 100 rows per statement)
def process_csv_to_grouped_insert_all(csv_file, table_name, max_rows_per_insert=100):
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames
        
        # Collect rows in batches of max_rows_per_insert size
        inserts = []
        batch = []
        for row in reader:
            batch.append(row.values())
            if len(batch) == max_rows_per_insert:
                inserts.append(convert_to_grouped_insert_all(table_name, batch, columns))
                batch = []
        
        # Insert the remaining rows if any
        if batch:
            inserts.append(convert_to_grouped_insert_all(table_name, batch, columns))
        
        return inserts

# Main function to process all CSV files and generate grouped INSERT ALLs
def main():
    # Map of CSV filenames to corresponding Oracle table names
    csv_to_table_map = {
        'Parking.csv': 'Parking',
        'ParkingSpot.csv': 'ParkingSpot',
        'ParkingUser.csv': 'ParkingUser',
        'ClientCar.csv': 'ClientCar',
        'Reservation.csv': 'Reservation',
        'Payment.csv': 'Payment',
        'StripeCharge.csv': 'StripeCharge',
    }
    
    all_inserts = []
    
    # Loop through each CSV file and convert it to grouped INSERT ALL statements
    for csv_file, table_name in csv_to_table_map.items():
        inserts = process_csv_to_grouped_insert_all(csv_file, table_name)
        all_inserts.extend(inserts)
    
    # Write all grouped insert statements to an output file
    with open('oracle_inserts.sql', mode='w', encoding='utf-8') as output_file:
        output_file.write('\n\n'.join(all_inserts))
        print(f"INSERT statements written to 'oracle_inserts.sql'")

if __name__ == "__main__":
    main()
