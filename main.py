import logging
import os

from flask import (
    Flask,
    redirect,
    request,
    url_for,
    session,
    g,
)

from scripts import snapshot_db
from routes.login import login_bp
from routes.user import user_bp
from routes.daily_training import exercise_bp
from routes.expressions import expressions_bp
from routes.expression_recall import expression_recall_bp
from routes.admin import admin_bp
from routes.sentence_training import sentence_training_bp
from extensions import db
from env_manager import load_env
from repository.users_repo import UsersRepo
import filters

logging.basicConfig(
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
)


def set_up_configs(app):
    db_host = os.getenv("LL_DB_HOST")
    db_port = os.getenv("LL_DB_PORT")
    db_name = os.getenv("LL_DB_NAME")
    db_user = os.getenv("LL_DB_USER")
    db_user_psw = os.getenv("LL_DB_USER_PSW")

    app.config["DB_HOST"] = db_host
    app.config["DB_PORT"] = db_port
    app.config["DB_NAME"] = db_name
    app.config["DB_USER"] = db_user
    app.config["DB_USER_PSW"] = db_user_psw

    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"postgresql://{db_user}:{db_user_psw}@{db_host}:{db_port}/{db_name}"

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # app.config['SQLALCHEMY_ECHO'] = True


def init_app():
    load_env()
    app = Flask(__name__)
    set_up_configs(app)
    db.init_app(app)
    return app


def set_globals(user_id: str, user_role: str) -> None:
    g.user_id = user_id
    g.user_role = user_role


app = init_app()

app.register_blueprint(login_bp)
app.register_blueprint(user_bp)
app.register_blueprint(exercise_bp)
app.register_blueprint(expressions_bp)
app.register_blueprint(expression_recall_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(sentence_training_bp)

app.jinja_env.filters["date_filter"] = filters.date_filter
app.jinja_env.filters[
    "knowledge_level_filter"
] = filters.knowledge_level_filter
app.jinja_env.filters["expression_sentence"] = filters.expression_sentence
app.jinja_env.filters["string_array"] = filters.string_array
app.jinja_env.filters["escape_double_quotas"] = filters.escape_double_quotas


@app.before_request
def before_request():
    path = request.path

    if path in [
        "/login",
        "/login/sign-on",
        "/login/logout",
        "/static/css/login-style.css",
        "/static/img/login-background.png",
        "static/js/expression_input.js",
    ]:
        return

    user_id = session.get("user_id")

    if not (user_id and (user := UsersRepo().get_by_id(user_id))):
        return redirect(url_for("login.login"))

    set_globals(user_id, user.role)


if __name__ == "__main__":
    if os.environ.get("LL_ENV") == "prod":
        snapshot_db()
        ...
    app.run(debug=True)
