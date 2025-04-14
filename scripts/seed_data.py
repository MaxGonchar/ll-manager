import argparse

from dotenv import dotenv_values

from common.constants import Env, ENV_MAPPING
from common.utils import get_connection, execute_sql

DATA_FILE = "seed_data.sql"


def main():
    parser = argparse.ArgumentParser(
        description="Script to clear db and seed data from seed_data.sql"
    )
    parser.add_argument(
        "-e",
        "--env",
        required=True,
        choices=[Env.DEV.value],
        help="Env name to seed data for. One of: dev",
    )
    args = parser.parse_args()
    configs = dotenv_values(ENV_MAPPING[args.env])

    with open(DATA_FILE, "r") as f:
        print("seed dev data ...")
        connection = get_connection(configs)  # type: ignore
        execute_sql(f.read(), connection)
        print("seed dev data succeed")


if __name__ == "__main__":
    main()
