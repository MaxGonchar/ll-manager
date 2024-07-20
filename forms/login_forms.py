from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError, Length


class LoginForm(FlaskForm):
    email = StringField("email", validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired()])


class SignOnForm(FlaskForm):
    first = StringField("first name", validators=[Length(max=20)])
    last = StringField("last name", validators=[Length(max=20)])
    email = StringField(
        "email", validators=[DataRequired(), Length(max=50), Email()]
    )
    password = PasswordField("password", validators=[DataRequired()])
    password_repeat = PasswordField(
        "confirm password", validators=[DataRequired()]
    )

    def validate_password_repeat(self, field):
        if field.data != self.password.data:
            field.errors += (ValidationError("passwords do not match"),)
