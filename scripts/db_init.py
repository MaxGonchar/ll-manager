# Run "python -m scripts.db_init -e dev" from ll-manager dir
# or
# "python scripts/db_init.py -e dev" with fallowing imports
# import os, sys
# sys.path.append(os.getcwd())

import argparse
from uuid import uuid4

from dotenv import dotenv_values

from scripts.common.constants import Env, ENV_MAPPING
from scripts.common.utils import (
    get_connection,
    execute_sql,
    get_current_utc_time,
)

from constants import Tags

DATA_FILE = "scripts/db_init.sql"
CHOICES = [Env.DEV.value, Env.PROD.value, Env.TEST.value]


def apply_migrations(configs):
    print("apply migrations ...")
    with open(DATA_FILE, "r") as f:
        execute_sql(f.read(), get_connection(configs))
    print("succeed")


def seed_mandatory_tags(configs):
    tags = Tags.list_()
    print("seed tags ...")
    for tag in set(tags):
        sql = f"""
            INSERT INTO tags (id, tag, added, updated) VALUES (
                '{str(uuid4())}',
                '{tag}',
                '{get_current_utc_time()}',
                '{get_current_utc_time()}'
            )
            ON CONFLICT (tag) DO NOTHING
        """
        execute_sql(sql, get_connection(configs))

    print("succeed")


def main():
    parser = argparse.ArgumentParser(
        description="Script to create db tables and run migrations from seed_data.sql"
    )
    parser.add_argument(
        "-e",
        "--env",
        required=True,
        choices=CHOICES,
        help=f'Env name to seed data for. One of: {", ".join(CHOICES)}',
    )
    args = parser.parse_args()
    configs = dotenv_values(ENV_MAPPING[args.env])

    print("init db ...")
    apply_migrations(configs)
    seed_mandatory_tags(configs)
    print("db is initialized")


if __name__ == "__main__":
    main()
