from functools import partial
import json
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(
    engine_options={"json_serializer": partial(json.dumps, ensure_ascii=False)}
)
