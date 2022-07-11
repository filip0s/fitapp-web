from math import e


# funkce pro výpočet body mass index
def calculate_bmi(height: float, weight: float):
    try:
        # bmi = výška v m ^2 / hmotnost
        bmi = round(weight / ((height / 100) ** 2), 2)
    except ZeroDivisionError:
        # Navrátí hodnotu nula při dělení nulou, tedy pokud je nulová výška
        bmi = 0.0
    finally:
        return bmi


# Funkce pro výpočet 1RM (1 Rep max = odhadovaná váha pro jedno opakování)
def one_rep_max(reps: int, weight: float):
    try:
        rep_max = (100 * weight) / (48.8 + (53.8 * pow(e, (-0.075 * reps))))
    except ZeroDivisionError:
        rep_max = 0.0
    finally:
        return round(rep_max, 2)


# Funkce pro výpočet průměrného času pro uběhnutí 1 km (1000 m)
# Parametry:
#   - time: čas v minutách
#   - distance: uběhnutá vzdálenost v kilometrech
# Výstup:
#   - time_per_km: počet minut za kterých uživatel v průměru uběhl 1 Km
def average_time_km(time: int, distance: float):
    try:
        time_per_km = float(time / distance)
    except ZeroDivisionError:
        time_per_km = 0.0
    finally:
        return round(time_per_km, 2)
