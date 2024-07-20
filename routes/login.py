from flask import Blueprint, render_template, redirect, url_for, flash

from forms.login_forms import LoginForm, SignOnForm
from helpers.session_helper import start_session, clear_session
from services.exceptions import (
    UserNotFoundException,
    PasswordDoesntMatchException,
)
from services.users_service import UsersService
from repository.exceptions import UserAlreadyExistsException
from constants import MessageStatus

login_bp = Blueprint("login", __name__, url_prefix="/login")


@login_bp.route("", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = UsersService().login(form.email.data, form.password.data)  # type: ignore
        except (UserNotFoundException, PasswordDoesntMatchException):
            flash("email or password is not correct")
            return render_template("login/login.html", form=form)

        start_session(user)
        return redirect(url_for("user.index"))

    return render_template("login/login.html", form=form)


@login_bp.route("/sign-on", methods=["GET", "POST"])
def sign_on():
    form = SignOnForm()
    if form.validate_on_submit():
        user_email = form.email.data
        try:
            user = UsersService().create_user(
                email=user_email,  # type: ignore
                password=form.password.data,  # type: ignore
                first=form.first.data,
                last=form.last.data,
            )
        except UserAlreadyExistsException:
            flash(
                f"user with email {user_email} already exists",
                MessageStatus.ERROR.value,
            )
            return render_template("login/sign_on.html", form=form)

        start_session(user)

        return redirect(url_for("user.index"))

    return render_template("login/sign_on.html", form=form)


@login_bp.route("/logout")
def log_out():
    clear_session()
    return redirect(url_for("login.login"))
