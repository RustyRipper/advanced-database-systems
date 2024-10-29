# Oracle Docker Container Setup and Database Initialization

Follow these steps to set up an Oracle Database container, initialize the database schema, and populate it with initial data.

## Step 1: Create and Start the Oracle Docker Container

Run the following command to create a Docker container for Oracle Database Express Edition. Adjust the `ORACLE_PWD` environment variable as needed.

```bash
docker run `
    -it `
    --name oracle-test `
    -p 1521:1521 `
    -e ORACLE_PWD=welcome123 container-registry.oracle.com/database/express:21.3.0-xe
```

```bash
cd generate_db
python generate_db.py
python insert_to_db.py