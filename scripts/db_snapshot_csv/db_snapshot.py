# https://www.postgresqltutorial.com/postgresql-tutorial/import-csv-file-into-posgresql-table/
import os
import os.path
import subprocess
import psycopg2
from datetime import datetime
import shutil

from scripts.db_snapshot_csv.google_client import GoogleClient

GOOGLE_SNAPSHOTS_FOLDER_ID = "1xQifcwcOQgLFIwtPOM7sgZehjGeTy-Ov"

host = "localhost"
user = "mhonc"
dbname = "ll_db"

connection = psycopg2.connect(
    host=host,
    port="5432",
    database=dbname,
    user="ll_user",
    password="ll_user_password",
)


def _get_tables():
    cursor = connection.cursor()
    sql = """
        SELECT
            tablename
        FROM
            pg_catalog.pg_tables
        WHERE
            schemaname != 'pg_catalog'
            AND schemaname != 'information_schema';
    """
    cursor.execute(sql)
    return [row[0] for row in cursor.fetchall()]


def _create_dir():
    datetime_suffix = datetime.utcnow().strftime("%Y-%m-%dT%H%M%S")
    snapshot_folder = f"db_snapshot_{datetime_suffix}"
    os.mkdir(snapshot_folder)
    snapshot_path = os.path.join(os.getcwd(), snapshot_folder)
    return snapshot_folder, snapshot_path


def _snapshot_tables(tables, snapshot_path):
    for table in tables:
        full_file = os.path.join(snapshot_path, f"{table}.csv")
        print(f"Copy {table} data to {full_file}")
        open(full_file, "w").close()
        command = f"COPY {table} TO '{full_file}' DELIMITER ',' CSV HEADER;"
        psql_args = [
            "psql",
            "-h",
            host,
            "-U",
            user,
            "-d",
            dbname,
            "-c",
            command,
        ]
        subprocess.run(psql_args, shell=False, check=True)


def _zip_files(snapshot_path, snapshot_folder):
    shutil.make_archive(snapshot_path, "zip", snapshot_path)
    shutil.rmtree(snapshot_folder)


def do_snapshot():
    snapshot_folder_name, snapshot_folder_path = _create_dir()
    _snapshot_tables(_get_tables(), snapshot_folder_path)
    _zip_files(snapshot_folder_path, snapshot_folder_name)

    client = GoogleClient(GOOGLE_SNAPSHOTS_FOLDER_ID)

    saved_snapshots = client.get_saved_snapshots() or []
    to_delete = []

    if len(saved_snapshots) >= 5:
        saved_snapshots.sort(key=lambda x: x["name"], reverse=True)
        to_delete = saved_snapshots[4:]

    if to_delete:
        file_ids_to_delete = [item["id"] for item in to_delete]
        client.delete_extra_snapshots(file_ids_to_delete)

    client.upload_with_conversion(f"{snapshot_folder_name}.zip")
    os.remove(f"{snapshot_folder_name}.zip")
