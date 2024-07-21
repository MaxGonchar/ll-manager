# LL-Manager

LL-Manager is a helper, allowing you to learn english expressions

It's a Python Flask app, using Postgresql as DB.

## To run locally
1. clone the repo
2. install python 3.11
3. create venv - `python3 -m venv /path/to/new/virtual/environment`
4. [activate venv](https://docs.python.org/3/library/venv.html#how-venvs-work)
5. [install requirements](https://pip.pypa.io/en/stable/user_guide/#requirements-files)
6. install and run Postgresql
   see [postgresql_cheetsheet](documentation/postgresql_cheetsheet.txt)
7. create DBs:
    ```
    CREATE DATABASE ll_db;
    CREATE DATABASE dev_ll_db;
    CREATE DATABASE test_ll_db;
    ```
8. create users:
    ```
    CREATE USER ll_user WITH PASSWORD 'll_user_password';
    GRANT ALL PRIVILEGES ON DATABASE ll_db TO ll_user;

    CREATE USER dev_ll_user WITH PASSWORD 'dev_ll_user_password';
    GRANT ALL PRIVILEGES ON DATABASE dev_ll_db TO dev_ll_user;

    CREATE USER test_ll_user WITH PASSWORD 'test_ll_user_password';
    GRANT ALL PRIVILEGES ON DATABASE test_ll_db TO test_ll_user;
    ```

    if posgres version >= 15:
    ```
    \c ll_db
    GRANT USAGE, CREATE ON SCHEMA public TO ll_user;

    \c dev_ll_db
    GRANT USAGE, CREATE ON SCHEMA public TO dev_ll_user;

    \c test_ll_db
    GRANT USAGE, CREATE ON SCHEMA public TO test_ll_user;
    ```
9.   set up vars:
    create files with env vars like in `.env.sample` for all envs:
    `.env.prod`
    `.env.dev`
    `.env.test`

10. make migrations
    `python -m scripts.db_init -e prod`
    `python -m scripts.db_init -e dev`
    `python -m scripts.db_init -e test`

11. run main.py

## Development
- linter: `python -m black . --exclude venv -l 79`
- test: `./run_tests.sh`
