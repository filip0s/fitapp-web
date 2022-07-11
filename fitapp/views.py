# Importy
from flask import render_template, redirect, url_for, flash, abort, Markup, request
from flask_login import login_user, logout_user, current_user, login_required
from fitapp import app, db
from fitapp.models import User, WeightLog, HeightLog, WorkoutLog, Exercise, ExerciseType, WorkoutExercise, RunningLog
from fitapp.forms import RegisterForm, LoginForm, LogWeight, LogHeight, LogWorkout, LogExercise, LogRunning, \
    SettingForm, ChangePasswordForm
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc, asc
from fitapp.calc import calculate_bmi, one_rep_max, average_time_km
from fitapp.helper import weight_calculator, human_readable_minutes, get_user_attributes, get_logs_by_name
from matplotlib import pyplot as plt
from datetime import datetime
import io, base64


# Přesměrování indexové stránky na domovskou stránku /home
@app.route("/")
def index():
    return redirect(url_for("home_page"))


# Domovská stránka
@app.route("/home")
def home_page():
    return render_template("pages/home.html", title="Domovská stránka")


# Přihlašovací stránka
@app.route("/login", methods=["GET", "POST"])
def login_page():
    # Přesměrování přihlášeného uživatele
    if current_user.is_authenticated:
        return redirect(url_for("home_page"))

    form = LoginForm()
    if form.validate_on_submit():
        # Přiřazení dat z formuláře
        username = form.username.data
        password = form.password.data
        remember_user = form.remember_user.data

        # Porovnání s databází
        user = User.query.filter_by(username=username).first()

        # Ověření existence uživatele podle username
        if user:
            # Porovnání hashe z databáze s heslem z formuláře
            if check_password_hash(user.password_hash, password):
                # Úspěšné porovnání hesel
                login_user(user, remember=remember_user)
                flash(f"Uživatel {user.username} úspěšně přihlášen", "success")
                return redirect(url_for("dashboard_page"))
            else:
                # Heslo a hash nejsou stejné
                flash("Špatné heslo", "danger")
        else:
            # Uživatel neexistuje v dataázi
            flash("Neexistující uživatelské jméno", "danger")
    return render_template("pages/login.html", title="Přihlášení", form=form)


# Registrační stránka
@app.route("/register", methods=["GET", "POST"])
def register_page():
    # Přesměrování přihlášeného uživatele
    if current_user.is_authenticated:
        return redirect(url_for("home_page"))

    form = RegisterForm()
    if form.validate_on_submit():
        # Přiřazení dat z formuláře
        username = form.username.data
        email = form.email.data
        password_hash = generate_password_hash(form.password.data)
        date_of_birth = form.date_of_birth.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        public_profile = form.public_profile.data

        # Tvorba instance uživatele
        temp_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            public_profile=public_profile
        )
        # Nahrání instance uživatele do databáze
        db.session.add(temp_user)
        db.session.commit()

        # Najití záznamu o právě vytvořeném uživateli
        temp_user = User.query.filter_by(username=username).first()

        # Tvorba prvních záznamů o uživateli
        weight_log = WeightLog(
            user_id=temp_user.id,
            value=form.weight.data,
        )
        height_log = HeightLog(
            user_id=temp_user.id,
            value=form.height.data,
        )
        db.session.add(weight_log)
        db.session.add(height_log)
        db.session.commit()
        flash("Účet vytvořen! Nyní se můžete přihlásit!", "success")
        return redirect(url_for("login_page"))
    return render_template("pages/register.html", title="Registrace", form=form)


# Odhlášení uživatele
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home_page"))


# Profilová stránka uživatele
@app.route("/profile/<username>")
def profile_page(username):
    user = User.query.filter_by(username=username).first()
    if user:
        user_attributes = get_user_attributes(user)
        return render_template("pages/profile.html", title=user.username, user=user, user_attributes=user_attributes)
    return abort(404)


# Uživatelský dashboard
@app.route("/user/dashboard")
@login_required
def dashboard_page():
    user_attributes = get_user_attributes(current_user)
    return render_template("pages/dashboard.html", title=f"Přehled uživatele {current_user.username}",
                           user_attributes=user_attributes)


@app.route("/user/settings", methods=["GET", "POST"])
@login_required
def settings_page():
    form = SettingForm()
    user = User.query.filter_by(id=current_user.id).first()

    if form.validate_on_submit():
        # Načtení údajů z formulářů
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.date_of_birth = form.date_of_birth.data
        user.public_profile = form.public_profile.data
        # Aktualizace v databázi
        db.session.commit()
        flash("Informace úspěšně aktualizovány", "success")
        return redirect(url_for("dashboard_page"))
    elif request.method == "GET":
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.date_of_birth.data = user.date_of_birth
        form.public_profile.data = user.public_profile
    return render_template("pages/settings.html", title="Nastavení účtu", form=form)


@app.route("/user/change-password", methods=["GET", "POST"])
@login_required
def change_password_page():
    form = ChangePasswordForm()
    user = User.query.filter_by(id=current_user.id).first()

    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash("Heslo úspěšně změněnno", "success")
        return redirect(url_for("dashboard_page"))
    return render_template("pages/change_password.html", title="Změna hesla", form=form)


# Chyba HTTP 404 - Stránka nenalezena
@app.errorhandler(404)
def error_404(e):
    return render_template("errors/404.html", title="Stránka nenalezena"), 404


# Chyba HTTP 403 - Zapovězený přístup
@app.errorhandler(403)
def error_403(e):
    return render_template("errors/403.html", title="Přístup zapovězen"), 403


# Chyba HTTP 500 - Chyba serveru
@app.errorhandler(500)
def error_500(e):
    return render_template("errors/500.html", title="Chyba serveru"), 500


# Formulář pro zadání hmotnosti uživatele
@app.route("/log/weight", methods=["GET", "POST"])
@login_required
def weight_log_page():
    form = LogWeight()
    if form.validate_on_submit():
        flash("Záznam úspěšně přidán", "success")
        weight_log = WeightLog(
            user_id=current_user.id,
            value=form.value.data
        )
        db.session.add(weight_log)
        db.session.commit()
        return redirect(url_for("dashboard_page"))
    return render_template("logging_pages/log_weight.html", title="Přidat záznam hmotnosti", form=form)


@app.route("/log/height", methods=["GET", "POST"])
@login_required
def height_log_page():
    form = LogHeight()
    if form.validate_on_submit():
        flash("Záznam úspěšně přidán", "success")
        height_log = HeightLog(
            user_id=current_user.id,
            value=form.value.data
        )
        db.session.add(height_log)
        db.session.commit()
        return redirect(url_for("dashboard_page"))
    return render_template("logging_pages/log_height.html", title="Přidat záznam výšky", form=form)


@app.route("/log/workout", methods=["GET", "POST"])
@login_required
def workout_log_page():
    form = LogWorkout()
    if form.validate_on_submit():
        flash("Trénink úspěšně přidán", "success")
        workout_log = WorkoutLog(
            user_id=current_user.id,
            date=form.date.data
        )
        db.session.add(workout_log)
        db.session.commit()
        return redirect(url_for("activity_log_page"))
    return render_template("logging_pages/log_workout.html", title="Přidat trénink", form=form)


@app.route("/log/workout/activity", methods=["GET", "POST"])
@login_required
def activity_log_page():
    form = LogExercise()
    current_workout = WorkoutLog.query.filter_by(user_id=current_user.id).order_by(desc(WorkoutLog.id)).first()
    if current_workout is None:
        flash("Je potřeba přidat trénink pro přidání cviků", "warning")
        return redirect(url_for("workout_log_page"))
    if form.validate_on_submit():
        # Výpočet dodatečných údajů podle zadaných dat
        weight = weight_calculator(current_user, form)
        orm = one_rep_max(int(form.repetitions.data), float(weight))
        # Tvorba objektu k nahrání do databáze
        exercise_log = WorkoutExercise(
            workout_id=current_workout.id,
            exercise_id=form.exercise.data.id,
            reps=form.repetitions.data,
            weight=weight,
            one_rep_max=orm
        )
        db.session.add(exercise_log)
        db.session.commit()
        flash("Cvik úspěšně přidán!", "success")
        return redirect(url_for("activity_log_page"))
    return render_template("logging_pages/log_activity.html", title="Zaznamenat aktivity", form=form,
                           current_workout=current_workout)


@app.route("/log/run", methods=["GET", "POST"])
@login_required
def run_log_page():
    form = LogRunning()
    if form.validate_on_submit():
        flash("Běh úspěšně přidán", "success")
        run_log = RunningLog(
            user_id=current_user.id,
            date=form.date.data,
            time=form.time.data,
            distance=form.distance.data,
            average_time_km=average_time_km(float(form.time.data), float(form.distance.data))
        )
        db.session.add(run_log)
        db.session.commit()
        return redirect(url_for("dashboard_page"))
    return render_template("logging_pages/log_run.html", title="Zaznamenat běh", form=form)


@app.route("/logs/<string:stat>", methods=["GET", "POST"])
@login_required
def show_logs_page(stat):
    log_dates, log_values, title, label, unit = get_logs_by_name(stat, current_user)
    logs = list(zip(log_dates, log_values))

    # tvorba grafu
    plt.xlabel("Datum")
    plt.xticks(rotation=30, ha='right')
    plt.ylabel(f"{label} [{unit}]")
    plt.plot(log_dates, log_values, color="green", marker=".")
    plt.tight_layout()
    # Převod grafu do binárního tvaru a vložení do html tagu
    # https://www.viralml.com/video-content.html?fm=yt&v=Z-um0QoVy18
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plot_src = base64.b64encode(img.getvalue()).decode()
    plot_tag = Markup(f"<img src='data:image/png;base64,{plot_src}' class='img-fluid mx-auto d-block'>")
    plt.clf()
    logs.reverse()

    return render_template("logging_pages/show_logs.html", title=title, label=label, unit=unit, logs=logs,
                           plot_tag=plot_tag)
