import os
from dotenv import load_dotenv
import pandas as pd
import oracledb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Set up environment variables for user credentials
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DATABASE_URL = f'oracle+oracledb://{DB_USER}:{DB_PASSWORD}@localhost:1521'

import os

# get the current working directory
current_working_directory = os.getcwd()

# print output to the console
print(current_working_directory)


ddl_file_path = './db.ddl'
db_remove_file_path = './remove_db.ddl'

# Establish Oracle 19c connection
connection = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn="localhost:1521/ORCLPDB1")
cursor = connection.cursor()


def execute_ddl(file_path):
    with open(file_path, 'r') as ddl_file:
        ddl_statements = ddl_file.read().split(';')
        for statement in ddl_statements:
            if statement.strip():
                print(f"Executing: {statement.strip()}")
                cursor.execute(statement)
    connection.commit()
    print(f"Executed DDL statements from {file_path} successfully.")


# SQLAlchemy engine and session setup
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


def insert_data_from_csv(table_name, csv_file, encoding='utf-8'):
    try:
        data = pd.read_csv(csv_file, encoding=encoding)
        data.columns = [col.upper() for col in data.columns]

        # Drop any "ID" column if present
        if 'ID' in data.columns:
            data.drop(columns=['ID'], inplace=True)

        # Define datetime columns
        timestamp_columns = ['OPEN_TIME', 'CLOSE_TIME', 'START_DATE', 'END_DATE', 'CREATED_AT', 'ADDITION_TIME']
        date_columns = ['DATE_OF_BIRTH', 'ADDITION_TIME']

        columns = ', '.join(data.columns)
        placeholders = []

        # Prepare placeholder formatting based on column type
        for i, col in enumerate(data.columns):
            if col in timestamp_columns:
                placeholders.append(f"TO_TIMESTAMP(:{i + 1}, 'YYYY-MM-DD HH24:MI:SS')")
            elif col in date_columns:
                placeholders.append(f"TO_DATE(:{i + 1}, 'YYYY-MM-DD')")
            else:
                placeholders.append(f":{i + 1}")

        sql = f"INSERT INTO {table_name.upper()} ({columns}) VALUES ({', '.join(placeholders)})"

        # Convert relevant columns to the appropriate datetime format
        for col in timestamp_columns:
            if col in data.columns:
                data[col] = pd.to_datetime(data[col], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')

        print(sql)
        rows = [tuple(row) for row in data.to_numpy()]

        cursor.executemany(sql, rows)
        connection.commit()
        print(f"Data from {csv_file} inserted successfully into {table_name}.")
    except UnicodeDecodeError as e:
        print(f"Encoding error: {e}. Trying with a different encoding.")
        insert_data_from_csv(table_name, csv_file, encoding='ISO-8859-1')


if __name__ == "__main__":
    try:
        # Execute DDL statements for removal and creation
        try:
            execute_ddl(db_remove_file_path)
        except Exception as e:
            print(f"Error in removal DDL execution: {e}")

        execute_ddl(ddl_file_path)
        
        # Insert data from CSV files
        insert_data_from_csv("Parking", 'Parking.csv')
        insert_data_from_csv("ParkingUser", 'ParkingUser.csv')
        insert_data_from_csv("ClientCar", 'ClientCar.csv')
        insert_data_from_csv("ParkingSpot", 'ParkingSpot.csv')
        insert_data_from_csv("Reservation", 'Reservation.csv')
        insert_data_from_csv("Payment", 'Payment.csv')
        insert_data_from_csv("StripeCharge", 'StripeCharge.csv')

        print("All data inserted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()
        cursor.close()
        connection.close()
