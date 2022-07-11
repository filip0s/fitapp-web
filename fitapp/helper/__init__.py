from fitapp.models import User, WeightLog, HeightLog, RunningLog, Exercise, WorkoutLog, WorkoutExercise
from fitapp.calc import calculate_bmi
from sqlalchemy import desc, asc
from math import modf


# Funkce pro získání všech dostupných parametrů uživatele
def get_user_attributes(user):
    current_weight = WeightLog.query.filter_by(user_id=user.id).order_by(desc(WeightLog.date)).first()
    if current_weight is not None:
        current_weight = current_weight.value
    else:
        current_weight = 0.0

    current_height = HeightLog.query.filter_by(user_id=user.id).order_by(desc(HeightLog.date)).first()
    if current_height is not None:
        current_height = current_height.value
    else:
        current_height = 0.0

    current_time_per_km = RunningLog.query.filter_by(user_id=user.id).order_by(desc(RunningLog.date)).first()
    if current_time_per_km is not None:
        current_time_per_km = current_time_per_km.average_time_km
    else:
        current_time_per_km = 0.0

    current_strongest_lift = User.query.filter_by(id=user.id).join(WorkoutLog, User.id == WorkoutLog.user_id).join(
        WorkoutExercise, WorkoutLog.id == WorkoutExercise.workout_id).join(Exercise,
                                                                           WorkoutExercise.exercise_id == Exercise.id).add_columns(
        User.id, User.first_name, WorkoutLog.date, WorkoutExercise.one_rep_max, Exercise.name).order_by(
        desc(WorkoutExercise.one_rep_max)).first()
    if current_strongest_lift is not None:
        one_rep_max = current_strongest_lift.one_rep_max
        exercise_name = current_strongest_lift.name
        current_strongest_lift = {
            "one_rep_max": one_rep_max,
            "exercise": exercise_name
        }
    else:
        current_strongest_lift = {
            "one_rep_max": 0.0,
            "exercise": ""
        }

    user_attributes = {
        "weight": current_weight,
        "height": current_height,
        "bmi": calculate_bmi(current_height, current_weight),
        "time_per_km": human_readable_minutes(current_time_per_km),
        "strongest_lift": current_strongest_lift
    }
    return user_attributes


# Funkce pro navrácení správné hmotnosti podle typu aktivity
# U různých typů aktivit se vypočítává hmotnost různě
def weight_calculator(user, form):
    # Získání typu zadaného cviku z databáze
    exercise_id = form.exercise.data.id
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    exercise_id = exercise.type_id

    if exercise_id == 0:
        # Aktivita je cvik s vlastní vahou
        # Pro tento případ se bere zadaná váha jako přidané závaží a přičte se hmotnost uživatele
        weight_query = WeightLog.query.filter_by(user_id=user.id).order_by(desc(WeightLog.date)).first()
        user_weight = weight_query.value
        return float(user_weight) + float(form.weight.data)
    elif exercise_id == 1:
        # Aktivita je cvik se zátěží
        return float(form.weight.data)
    else:
        return 0.0


# Funkce pro převod minut na lidsky čitelný tvar
# V některých místech v aplikaci se s časem počítá jako s minutami v dekadickém tvaru, což může být pro uživatele
# matoucí. Tato funkce převede minuty na lidsky čitelný tvar ve formátu <minuty>:<sekundy>
def human_readable_minutes(time: float):
    seconds, minutes = modf(time)
    minutes = int(minutes)
    if seconds != 0:
        seconds *= 60
        seconds = int(seconds)
    if seconds < 10:
        seconds = str(int(seconds))
        seconds = "0" + seconds

    return f"{minutes}:{seconds}"


def get_logs_by_name(name, user):
    values = list()
    dates = list()

    if name == "weight":
        query = WeightLog.query.filter_by(user_id=user.id).order_by(asc(WeightLog.date)).all()
        if len(query) > 0:
            for item in query:
                dates.append(item.date.strftime("%d. %m. %Y %H:%M"))
                values.append(item.value)
        return dates, values, "Záznamy hmotnosti", "Hmotnost", "kg"

    elif name == "height":
        query = HeightLog.query.filter_by(user_id=user.id).order_by(asc(HeightLog.date)).all()
        if len(query) > 0:
            for item in query:
                dates.append(item.date.strftime("%d. %m. %Y %H:%M"))
                values.append(item.value)
        return dates, values, "Záznamy výšky", "Výška", "cm"

    elif name == "running":
        query = RunningLog.query.filter_by(user_id=user.id).order_by(asc(RunningLog.date)).all()
        if len(query) > 0:
            for item in query:
                dates.append(item.date.strftime("%d. %m. %Y"))
                values.append(item.average_time_km)
        return dates, values, "Záznamy běhů", "Průměrný čas na 1 km", "min/1 km"

    elif name == "squat":
        # exercise_id = 5
        query = User.query.filter_by(id=user.id).join(WorkoutLog, User.id == WorkoutLog.user_id).join(
            WorkoutExercise,
            WorkoutLog.id == WorkoutExercise.workout_id).join(
            Exercise, WorkoutExercise.exercise_id == Exercise.id).add_columns(User.id, User.first_name, WorkoutLog.date,
                                                                              WorkoutExercise.one_rep_max,
                                                                              Exercise.name).filter_by(id=5).all()
        if len(query) > 0:
            for item in query:
                dates.append(item.date.strftime("%d. %m. %Y"))
                values.append(item.one_rep_max)
        return dates, values, "Záznamy maximálních vah pro dřep", "Maximální váha", "kg"

    elif name == "bench":
        # exercise_id =  8
        query = User.query.filter_by(id=user.id).join(WorkoutLog, User.id == WorkoutLog.user_id).join(
            WorkoutExercise,
            WorkoutLog.id == WorkoutExercise.workout_id).join(
            Exercise, WorkoutExercise.exercise_id == Exercise.id).add_columns(User.id, User.first_name, WorkoutLog.date,
                                                                              WorkoutExercise.one_rep_max,
                                                                              Exercise.name).filter_by(id=8).all()
        if len(query) > 0:
            for item in query:
                dates.append(item.date.strftime("%d. %m. %Y"))
                values.append(item.one_rep_max)
        return dates, values, "Záznamy maximálních vah pro benchpress", "Maximální váha", "Kg"

    elif name == "deadlift":
        # exercise_id = 6
        query = User.query.filter_by(id=user.id).join(WorkoutLog, User.id == WorkoutLog.user_id).join(
            WorkoutExercise,
            WorkoutLog.id == WorkoutExercise.workout_id).join(
            Exercise, WorkoutExercise.exercise_id == Exercise.id).add_columns(User.id, User.first_name, WorkoutLog.date,
                                                                              WorkoutExercise.one_rep_max,
                                                                              Exercise.name).filter_by(id=6).all()
        if len(query) > 0:
            for item in query:
                dates.append(item.date.strftime("%d. %m. %Y"))
                values.append(item.one_rep_max)
        return dates, values, "Záznamy maximálních vah pro mrtvý tah", "Maximální váha", "kg"

    elif name == "overheadpress":
        # exercise_id = 7
        query = User.query.filter_by(id=user.id).join(WorkoutLog, User.id == WorkoutLog.user_id).join(
            WorkoutExercise,
            WorkoutLog.id == WorkoutExercise.workout_id).join(
            Exercise, WorkoutExercise.exercise_id == Exercise.id).add_columns(User.id, User.first_name, WorkoutLog.date,
                                                                              WorkoutExercise.one_rep_max,
                                                                              Exercise.name).filter_by(id=7).all()
        if len(query) > 0:
            for item in query:
                dates.append(item.date.strftime("%d. %m. %Y"))
                values.append(item.one_rep_max)
        return dates, values, "Záznamy maximálních vah pro overhead press", "Maximální váha", "kg"

    elif name == "pullup":
        query = User.query.filter_by(id=user.id).join(WorkoutLog, User.id == WorkoutLog.user_id).join(
            WorkoutExercise,
            WorkoutLog.id == WorkoutExercise.workout_id).join(
            Exercise, WorkoutExercise.exercise_id == Exercise.id).add_columns(User.id, User.first_name, WorkoutLog.date,
                                                                              WorkoutExercise.one_rep_max,
                                                                              Exercise.name).filter_by(id=0).all()
        if len(query) > 0:
            for item in query:
                dates.append(item.date.strftime("%d. %m. %Y"))
                values.append(item.one_rep_max)
        return dates, values, "Záznamy maximálních vah pro shyb (úchop nadhmatem)", "Maximální váha", "kg"
