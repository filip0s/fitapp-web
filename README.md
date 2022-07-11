# FitApp

## Krátce na úvod

FitApp je minimalistická webová aplikace vytvořená pomoci programovacího jazyku Python a mikroframeworku Flask, která
slouží pro zaznamenávání pokroků ve cvičení a zdravém životním stylu obecně.

## Úvodní nastavení

### Flask

Aplikace je postavena v programovacím jazyce [Python v3.9](https://www.python.org/downloads/) a využívá framework
[Flask](https://flask.palletsprojects.com/en/1.1.x/), který lze nainstalovat pomocí příkazu:

```shell
pip install flask
```

Další potřebné knihovny jsou:

- ```Flask-SQLAlchemy```

Na systémech založených na UNIXu, jako je například Linux nebo MacOS, je nejprve potřeba nastavit systémové proměnné
pomocí příkazů:

```shell
export FLASK_APP=fitapp
export FLASK_ENV=development
```

poté by mělo být možné spustit lokální server pomocí příkazu:

```shell
flask run
```

### SCSS

Ke kompilaci SCSS na standardní CSS je potřeba mít nainstalovaný nástroj [Node.js](https://nodejs.org/en/), u kterého
využijeme jeho správce balíčků ```npm```.

Pro doinstalování potřebných závislostí ke kompilování SCSS a provádění dalších úkolů, o které se stadá NPM, stačí zadat
příkaz:

```shell
npm ci
```

Poté lze aktivovat "watcher", který bude překompiluje dané soubory při každé změně

```shell
sass --watch scss/:fitapp/static/css/
```

- ```scss/``` - zdrojová složka
- ```:``` - oddělovač
- ```fitapp/static/css/``` - cílová složka

## Struktura projektu

```
fitapp-web
|- fitapp (balíček)
    |- __init__.py 
    |- /static
        |- /css
            |- main.css
    |- /templates
        |- base_template.html
        |- home.html
|- /scss
|- .GITIGNORE
|- README.md
|- package.json
|- package-lock.json
```

- ```fitapp-web``` - kořenový adresář projektu
- ```fitapp``` - adresář s balíčkem
  - základní soubory, které se dají použít pro deployment
- ```/static/css``` - adresář s kaskádovými styly
  - ```main.css``` - hlavní stylovací soubor
- ```/templates``` - adresář se šablonami pro vykreslování stránek
    - ```base_template.html``` - základní šablona, ze které vychází všechny ostatní šablony
    - ```home.html``` - domovská stránka