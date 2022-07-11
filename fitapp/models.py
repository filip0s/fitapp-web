from fitapp import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Tabulka uživatele "user"
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.Integer, nullable=False, default=0)  # TODO: Prozkoumat možnost typu ENUM pro role
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    date_of_birth = db.Column(db.DateTime, nullable=False)
    date_of_registration = db.Column(db.DateTime, default=datetime.utcnow)
    public_profile = db.Column(db.Boolean, default=False)
    weight_logs = db.relationship("WeightLog", backref="user")
    height_logs = db.relationship("HeightLog", backref="user")
    workout_logs = db.relationship("WorkoutLog", backref="user")
    running_logs = db.relationship("RunningLog", backref="user")

    # informace navrácené při printování objektu
    def __repr__(self):
        return f"<User: {self.username}; id: {self.id}>"

    # Při převedení na integer navrátí primární klíč - id
    def __int__(self):
        return self.id


# Tabulka záznamů hmotnosti uživatelů
class WeightLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    value = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<User: {self.user_id}: {self.value} kg on {self.date}>"


# Tabulka záznamů výšky uživatelů
class HeightLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    value = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<User: {self.user_id}: {self.value} cm on {self.date}>"


# Třída pro modelování tabulky "workout" v databázi
# Tabulka záznamů tréninků
class WorkoutLog(db.Model):
    __tablename__ = "workout_log"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    activities_in_workout = db.relationship("WorkoutExercise", backref="workout")

    def __repr__(self):
        return f"<User: {self.user_id} worked out at {self.date}>"


# Tabulka záznamů aktivit v jednom tréninku
class WorkoutExercise(db.Model):
    __tablename__ = "exercise_log"
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workout_log.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercise.id"), nullable=False)
    reps = db.Column(db.Integer, nullable=False, default=1)
    weight = db.Column(db.Integer, default=0)
    one_rep_max = db.Column(db.Float, default=0)


# Třída pro tabulku "exercise"
# Tabulka uchovává jednotlivé aktivity
class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    bio = db.Column(db.Text)
    type_id = db.Column(db.Integer, db.ForeignKey("exercise_type.id"), nullable=False)
    exercise_in_workouts = db.relationship("WorkoutExercise", backref="exercise")


# Třída pro tabulku "activity_type"
# Tabulka uchovává různé druhy aktivit
# Podle toho ke kterému typu náleží daná aktivita se mění aplikují na aktivitu různé výpočty či se aplikace k dané
# aktivitě obecně chová jinak
class ExerciseType(db.Model):
    __tablename__ = "exercise_type"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    bio = db.Column(db.Text)
    exercises_of_type = db.relationship("Exercise", backref="exercise_type")

    def __repr__(self):
        return f"<Typ {self.id}: {self.name}>"


class RunningLog(db.Model):
    __tablename__ = "running_log"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    time = db.Column(db.Integer, nullable=False, default=1)
    distance = db.Column(db.Integer, nullable=False, default=1)
    average_time_km = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Běh: uživatel {self.user_id} uběhl {self.distance} Km za {self.time} min>"
