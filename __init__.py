# docpat/docpat/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect # Für sichere Formulare
from flask_migrate import Migrate # Flask-Migrate importieren

# Initialisiere SQLAlchemy
db = SQLAlchemy()
# Initialisiere CSRF-Schutz für Formulare
csrf = CSRFProtect()
# Initialisiere Flask-Migrate
migrate = Migrate()


def create_app():
    # Erstelle eine Flask-Instanz
    app = Flask(__name__)

    # Konfiguration
    # Ein geheimer Schlüssel ist WICHTIG für die Sicherheit (z.B. für Session-Management und CSRF)
    # Ändere 'dein_eigener_sehr_geheimer_schluessel' in eine lange, zufällige Kette
    app.config['SECRET_KEY'] = 'tma2pR6Ei8wSEPgmKreGz09Nrphd9ao2' # Nutze deinen geheimen Schlüssel hier
    # Konfiguration für die Datenbank: SQLite-Datei im Hauptordner des Projekts
    # Stelle sicher, dass der Pfad korrekt ist (relativ zur root des Projekts)
    # Wenn __init__.py in docpat/docpat liegt, sollte 'sqlite:///../site.db' passen,
    # um die DB eine Ebene über dem docpat-Ordner zu speichern.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../site.db'
    # Deaktiviert eine unnötige Warnung von SQLAlchemy
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Binde SQLAlchemy, CSRF und Flask-Migrate an die App
    db.init_app(app)
    csrf.init_app(app) # CSRF-Schutz aktivieren
    migrate.init_app(app, db) # Flask-Migrate an App und DB binden

    # Importiere und registriere Blueprints (unsere Module)
    # Wir nutzen einen Blueprint für unsere Routen, das hält es modular
    from . import routes
    app.register_blueprint(routes.bp) # STELL SICHER, DIESE ZEILE IST DA!

    # Stelle sicher, dass die Datenbanktabellen existieren
    # Muss im App-Kontext aufgerufen werden
    # Wenn du Flask-Migrate benutzt, brauchst du db.create_all() normalerweise nur einmal
    # zum Initialisieren. Später macht migrate/upgrade die Schema-Änderungen.
    # Du könntest diese Zeile auskommentieren, sobald du mit migrate arbeitest,
    # um sicherzustellen, dass nur migrate die DB-Struktur verwaltet.
    # with app.app_context():
    #     db.create_all() # Erstellt alle in models.py definierten Tabellen, falls sie noch nicht existieren

    # Gib die erstellte App-Instanz zurück
    return app
