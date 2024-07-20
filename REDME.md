# LL-Manager

LL-Manager is a helper, allowing you to learn english expressions

It's a Python Flask app, using Postgresql as DB.

## To run locally
1. clone the repo
2. install python 3.8
3. create venv - `python3 -m venv /path/to/new/virtual/environment`
4. [activate venv](https://docs.python.org/3/library/venv.html#how-venvs-work)
5. [install requirements](https://pip.pypa.io/en/stable/user_guide/#requirements-files)
6. install and run Postgresql
7. create DBs:
    ```
    CREATE DATABASE ll_db;
    CREATE DATABASE test_ll_db;
    ```
8. create users:
    ```
    CREATE USER ll_user WITH PASSWORD 'll_user_password';
    GRANT ALL PRIVILEGES ON DATABASE ll_db TO ll_user;

    CREATE USER test_ll_user WITH PASSWORD 'test_ll_user_password';
    GRANT ALL PRIVILEGES ON DATABASE test_ll_db TO test_ll_user;
    ```
9. set up vars:
    ```
    export LL_DB_HOST="localhost"
    export LL_DB_PORT="5432"
    export LL_DB_NAME="ll_db"
    export LL_DB_USER="ll_user"
    export LL_DB_USER_PSW="ll_user_password"
    ```
10. run main.py

## Development
- linter: `python -m black . --exclude venv -l 79`
- test: `python -m unittest -v`
