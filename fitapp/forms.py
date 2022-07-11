from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, IntegerField
from wtforms.fields import DateField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from fitapp.models import User, Exercise
from wtforms_sqlalchemy.fields import QuerySelectField


class RegisterForm(FlaskForm):
    username = StringField("Uživatelské jméno", validators=[
        DataRequired(message="Uživatelské jméno je povinné"),
        Length(min=3,
               max=64,
               message="Uživatelské jméno musí mít 3-64 znaků"),
    ])
    first_name = StringField("Jméno", validators=[
        Length(
            max=32,
            message="Jméno musí mít méně než 32 znaků"
        )
    ])
    last_name = StringField("Příjmení", validators=[
        Length(
            max=32,
            message="Příjmení musí mít méně než 32 znaků"
        )
    ])
    email = EmailField("E-mail", validators=[
        DataRequired(message="Email je vyžadován")
    ])
    password = PasswordField("Heslo", validators=[
        DataRequired(message="Heslo je povinný údaj"),
        EqualTo("repeat_password", message="Hesla se musí shodovat")
    ])
    repeat_password = PasswordField("Heslo znovu", validators=[
        DataRequired(message="Potvrďte prosím heslo")
    ])
    date_of_birth = DateField("Datum narození", validators=[
        DataRequired(message="Datum narození je vyžadováno")
    ])
    height = FloatField("Výška [cm]", validators=[
        DataRequired(message="Výška je povinný údaj")
    ])
    weight = FloatField("Hmotnost [kg]", validators=[
        DataRequired(message="Hmotnost je povinný údaj")
    ])
    public_profile = BooleanField("Veřejný profil")
    submit = SubmitField("Registrovat se")

    # Ověřuje unikátnost uživatelského jména
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            # pokud je navrácen objekt vyhovující dotazu, pak už je uživatelské jméno použito a je
            # vyvolán ValidationError
            raise ValidationError("Již existuje uživatel s tímto uživatelským jménem, zvolte prosím jiné.")

    # Ověří, zda se email nevyskytuje v databázi
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            # pokud v databázi existuje uživatel, který má zadaný email, aplikace vyvolá ValidationError
            raise ValidationError("E-mail je již použitý, zvolte prosím jíný.")


class LoginForm(FlaskForm):
    username = StringField("Uživatelské jméno", validators=[
        DataRequired(message="Uživatelské jméno je povinné"),
        Length(min=3,
               max=64,
               message="Uživatelské jméno musí mít 3-64 znaků"),
    ])
    password = PasswordField("Heslo", validators=[
        DataRequired("Heslo je povinný údaj")
    ])
    remember_user = BooleanField("Zapamatovat si přihlášení")
    submit = SubmitField("Přihlásit se")


class LogWeight(FlaskForm):
    value = FloatField("Hmotnost [kg]", validators=[
        DataRequired(message="Hodnota hmotnosti je vyžadována")
    ])
    submit = SubmitField("Přidat")


class LogHeight(FlaskForm):
    value = FloatField("Výška [cm]", validators=[
        DataRequired(message="Hodnota výšky je vyžadována")
    ])
    submit = SubmitField("Přidat")


class LogWorkout(FlaskForm):
    date = DateField("Datum", validators=[
        DataRequired(message="Datum tréninku je povinné")
    ])
    submit = SubmitField("Přidat")


def exercise_query():
    return Exercise.query


class LogExercise(FlaskForm):
    exercise = QuerySelectField("Cvik", validators=[
        DataRequired(message="Je nutné vybrat cvik")
    ], query_factory=exercise_query, allow_blank=False, get_label="name")
    weight = FloatField("Hmotnost [kg]")
    repetitions = FloatField("Počet opakování", validators=[
        DataRequired(message="Tento údaj je povinný")
    ])
    submit = SubmitField("Potvrdit a přidat další")


class LogRunning(FlaskForm):
    date = DateField("Datum", validators=[
        DataRequired(message="Je nutné zvolit datum")
    ])
    time = IntegerField("Doba běhu [min]", validators=[
        DataRequired(message="Je nutné zadat dobu běhu")
    ])
    distance = FloatField("Uběhnutá vzdálenost [km]", validators=[
        DataRequired(message="Je nutné zadata uběhnutou vzdálenost")
    ])
    submit = SubmitField("Přidat záznam")


class SettingForm(FlaskForm):
    first_name = StringField("Jméno", validators=[
        Length(
            max=32,
            message="Jméno musí mít méně než 32 znaků"
        )
    ])
    last_name = StringField("Příjmení", validators=[
        Length(
            max=32,
            message="Příjmení musí mít méně než 32 znaků"
        )
    ])
    date_of_birth = DateField("Datum narození", validators=[
        DataRequired(message="Datum narození je vyžadováno")
    ])
    public_profile = BooleanField("Veřejný profil")
    submit = SubmitField("Potvrdit")


class ChangePasswordForm(FlaskForm):
    password = PasswordField("Heslo", validators=[
        DataRequired(message="Heslo je povinný údaj"),
        EqualTo("repeat_password", message="Hesla se musí shodovat")
    ])
    repeat_password = PasswordField("Heslo znovu", validators=[
        DataRequired(message="Potvrďte prosím heslo")
    ])
    submit = SubmitField("Potvrdit")
