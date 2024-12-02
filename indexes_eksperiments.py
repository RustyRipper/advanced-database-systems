import os
import time
import pandas as pd
import oracledb
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection details
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DSN = "localhost:1521/ORCLPDB1"
# Establish connection to the database
connection = oracledb.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    dsn=DSN
)


def create_btree_index(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE INDEX idx_reservation_parking_id ON Reservation(PARKING_ID)")
    connection.commit()
    cursor.close()

def create_bitmap_index(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE BITMAP INDEX idx_parkingspot_is_occupied ON ParkingSpot(IS_OCCUPIED)")
    connection.commit()
    cursor.close()

def create_functional_index(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE INDEX idx_clientcar_lower_car_model ON ClientCar(LOWER(CAR_MODEL))")
    connection.commit()
    cursor.close()

def drop_index(connection, index_name):
    cursor = connection.cursor()
    cursor.execute(f"DROP INDEX {index_name}")
    connection.commit()
    cursor.close()

def measure_query_time(connection, query, params):
    start_time = time.time()
    cursor = connection.cursor()
    cursor.execute(query, params)
    cursor.fetchall()
    end_time = time.time()
    cursor.close()
    return end_time - start_time

def run_index_experiments(connection, queries, iterations=10):
    results = []

    # No index
    for query_name, query_data in queries.items():
        for i in range(iterations):
            execution_time = measure_query_time(connection, query_data["script"], query_data["params"])
            results.append((query_name, "no_index", i + 1, execution_time))
            print(f"{query_name} - No Index - Iteration {i + 1}: {execution_time:.4f} seconds")

    # B-tree index
    create_btree_index(connection)
    for query_name, query_data in queries.items():
        for i in range(iterations):
            execution_time = measure_query_time(connection, query_data["script"], query_data["params"])
            results.append((query_name, "btree_index", i + 1, execution_time))
            print(f"{query_name} - B-tree Index - Iteration {i + 1}: {execution_time:.4f} seconds")
    drop_index(connection, "idx_reservation_parking_id")

    # Bitmap index
    create_bitmap_index(connection)
    for query_name, query_data in queries.items():
        for i in range(iterations):
            execution_time = measure_query_time(connection, query_data["script"], query_data["params"])
            results.append((query_name, "bitmap_index", i + 1, execution_time))
            print(f"{query_name} - Bitmap Index - Iteration {i + 1}: {execution_time:.4f} seconds")
    drop_index(connection, "idx_parkingspot_is_occupied")

    # Functional index
    create_functional_index(connection)
    for query_name, query_data in queries.items():
        for i in range(iterations):
            execution_time = measure_query_time(connection, query_data["script"], query_data["params"])
            results.append((query_name, "functional_index", i + 1, execution_time))
            print(f"{query_name} - Functional Index - Iteration {i + 1}: {execution_time:.4f} seconds")
    drop_index(connection, "idx_clientcar_lower_car_model")

    return results

def save_results_to_file(results, file_path):
    with open(file_path, 'w') as file:
        file.write("Query,IndexType,Iteration,ExecutionTime\n")
        for result in results:
            file.write(f"{result[0]},{result[1]},{result[2]},{result[3]:.4f}\n")

# Example usage
test_queries = {
    "select1": {
        "script": "SELECT * FROM Reservation WHERE PARKING_ID = :parking_id",
        "params": {"parking_id": 1}
    },
    "select2": {
        "script": "SELECT * FROM ParkingSpot WHERE IS_OCCUPIED = 'N'",
        "params": {}
    },
    "select3": {
        "script": "SELECT * FROM ClientCar WHERE LOWER(CAR_MODEL) = :car_model",
        "params": {"car_model": "toyota"}
    }
}

results = run_index_experiments(connection, test_queries)
save_results_to_file(results, "index_experiment_results.csv")

connection.close()