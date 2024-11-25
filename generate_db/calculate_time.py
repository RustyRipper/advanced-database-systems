import oracledb
import time
import pandas as pd
import subprocess


def reset_database():
    result = subprocess.run(['python', 'insert_to_db.py'],
                            capture_output=True, text=True, check=True)

    if result.returncode != 0:
        print(
            f"Error occurred while running the data insertion script: {result.stderr}")
    else:
        print("Data cleared and inserted successfully.")


def load_sql_script(file_path):
    """Reads the SQL script from a file."""
    with open(file_path, 'r') as file:
        return file.read()


def execute_transaction(sql_script, params=(), is_select=True):
    connection = oracledb.connect(
        user="system",
        password="welcome123",
        dsn="localhost:1521/XE"
    )
    cursor = connection.cursor()

    start_time = time.time()

    cursor.execute(sql_script, params)
    if is_select:
        results = cursor.fetchall()
        for row in results:
            _ = row[0]
    else:
        connection.commit()
    end_time = time.time()
    cursor.close()
    connection.close()

    return end_time - start_time


def run_load_test(iterations=10):
    sql_script_select3 = load_sql_script("../transactions/select3.sql")
    params_select3 = {"PARKING_ID": 10,
                      "START_DATE": "2020-12-12 12:12:12",
                      "END_DATE": "2023-12-12 12:12:12"}
    sql_script_insert = load_sql_script("../transactions/insert_alone.sql")
    params_insert = {"PARKING_ID": 10,
                     "USER_ID": 10,
                     "new_end_date": "2022-12-12 18:12:12",
                     "new_start_date": "2022-12-12 06:12:12",
                     "reference_date": "2020-11-27"}

    execution_times = []
    for i in range(iterations):
        reset_database()

        execution_time = execute_transaction(sql_script_select3, params_select3,
                                             True)
        execution_times.append(execution_time)
        print(f"Iteration {i + 1}: {execution_time:.4f} seconds")

    results_df = pd.DataFrame({
        "Run": list(range(1, iterations + 1)),
        "Execution Time (s)": execution_times
    })

    results_df.to_csv("load_test_results.csv", index=False)
    print("\nResults saved to 'load_test_results.csv'.")

    # Calculate and print summary
    print("\nSummary:")
    print(f"Minimum Time: {min(execution_times):.4f} seconds")
    print(f"Maximum Time: {max(execution_times):.4f} seconds")
    print(
        f"Average Time: {sum(execution_times) / len(execution_times):.4f} seconds")


if __name__ == "__main__":
    run_load_test(iterations=10)
