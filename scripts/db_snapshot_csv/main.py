import json
from typing import Dict, Optional
from datetime import date, timedelta, datetime

from scripts.db_snapshot_csv.db_snapshot import do_snapshot

SNAPSHOT_DATE_DELTA = timedelta(days=1)


class AppStateRW:
    def __init__(self):
        self.state_file = "app_state.json"

    def _get_app_state(self) -> Dict[str, str]:
        print("Get app state data")
        try:
            with open(self.state_file, "r") as file:
                state = file.read()
            return json.loads(state)
        except FileNotFoundError:
            print("File not found:", self.state_file)
            return {}

    def _update_app_state(self, data: Dict[str, str]) -> None:
        print("Update app state data")
        with open(self.state_file, "w") as file:
            file.write(json.dumps(data, indent=4))  # type: ignore


class AppState:
    def __init__(self):
        self.state_rw = AppStateRW()

    @property
    def last_db_snapshot_date(self) -> Optional[date]:
        state = self.state_rw._get_app_state()
        date_str = state.get("last_db_snapshot_date", "")

        if not date_str:
            return None

        year, month, day = map(int, date_str.split("-"))

        return date(year, month, day)

    @last_db_snapshot_date.setter
    def last_db_snapshot_date(self, date_: date) -> None:
        app_state = self.state_rw._get_app_state()
        last_db_snapshot_date = date_.strftime("%Y-%m-%d")
        print("Set app state data:", last_db_snapshot_date)
        app_state["last_db_snapshot_date"] = last_db_snapshot_date
        self.state_rw._update_app_state(app_state)


def snapshot_db():
    app_state = AppState()
    today = datetime.now().date()
    if last_snapshot_date := app_state.last_db_snapshot_date:
        if today - last_snapshot_date >= SNAPSHOT_DATE_DELTA:
            do_snapshot()
            app_state.last_db_snapshot_date = today
    else:
        do_snapshot()
        app_state.last_db_snapshot_date = today
