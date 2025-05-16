# docpat/docpat/models.py

from . import db
import datetime

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    vorname = db.Column(db.String(100), nullable=False)
    nachname = db.Column(db.String(100), nullable=False)
    # GEÄNDERT: Statt Alter, Geburtsdatum speichern
    geburtsdatum = db.Column(db.Date) # NEU: Geburtsdatum als Datumstyp
    geschlecht = db.Column(db.String(20))
    adresse = db.Column(db.String(200))
    plz = db.Column(db.String(10))
    ort = db.Column(db.String(100))
    # GEÄNDERT: Diese sind jetzt Dropdowns im Formular, aber String in DB
    land = db.Column(db.String(50))
    ethnie = db.Column(db.String(50))
    blutgruppe = db.Column(db.String(10))

    telefon = db.Column(db.String(50))
    email = db.Column(db.String(120))
    krankenkasse = db.Column(db.String(100))


    diagnosen = db.Column(db.Text)
    ernaehrung = db.Column(db.Text)
    medikation = db.Column(db.Text)
    drogen = db.Column(db.Text)
    # NEU: Feld für Raucher
    raucher = db.Column(db.Boolean, default=False)

    # Dieses Feld muss existieren, da es im Formular und im Code verwendet wird
    op_vorgeschichte = db.Column(db.Text)

    allergien = db.Column(db.Text)


    risikogruppe = db.Column(db.Boolean, default=False)

    # Diese Felder werden nicht mehr in der DB gespeichert, da sie dynamisch ermittelt werden
    # letzte_untersuchung = db.Column(db.Date)
    # naechste_untersuchung = db.Column(db.Date)


    vital_signs = db.relationship('VitalSign', backref='patient', lazy=True, order_by='VitalSign.timestamp.desc()')
    vaccinations = db.relationship('Vaccination', backref='patient', lazy=True, order_by='Vaccination.date.desc()')
    injections = db.relationship('Injection', backref='patient', lazy=True, order_by='Injection.date.desc()')

    appointments = db.relationship('Appointment', backref='patient', lazy=True, order_by='Appointment.date_time.desc()')

    visits = db.relationship('Visit', backref='patient', lazy=True, order_by='Visit.date_time.desc()')


    def __repr__(self):
        return f"<Patient {self.nachname}, {self.vorname}>"

class VitalSign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    bmi = db.Column(db.Float)
    puls = db.Column(db.Integer)
    blood_pressure = db.Column(db.String(20))
    temperature_celsius = db.Column(db.Float)
    fev1 = db.Column(db.Float)
    fvc = db.Column(db.Float)

    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)

    def __repr__(self):
        return f"<VitalSign {self.timestamp.strftime('%Y-%m-%d %H:%M')} for Patient ID {self.patient_id}>"

# Modell für Impfungen (unverändert)
class Vaccination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    vaccine_against = db.Column(db.String(100), nullable=False)
    vaccine_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50))
    route = db.Column(db.String(50), nullable=True)
    batch_number = db.Column(db.String(100))
    observations = db.Column(db.Text)
    signed_by = db.Column(db.String(100))
    next_dosage_date = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f"<Vaccination on {self.date} against {self.vaccine_against} for Patient ID {self.patient_id}>"

# Modell für Injektionen (unverändert)
class Injection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    injection_substance = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50))
    route = db.Column(db.String(50), nullable=True)
    batch_number = db.Column(db.String(100))
    observations = db.Column(db.Text)
    signed_by = db.Column(db.String(100))
    next_dosage_date = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f"<Injection on {self.date} with {self.injection_substance} for Patient ID {self.patient_id}>"


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)

    date_time = db.Column(db.DateTime, nullable=False)

    description = db.Column(db.String(200), nullable=False)

    duration_minutes = db.Column(db.Integer, nullable=True)

    notes = db.Column(db.Text, nullable=True)


    def __repr__(self):
        return f"<Appointment on {self.date_time.strftime('%Y-%m-%d %H:%M')} for Patient ID {self.patient_id}>"


class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)

    date_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    subjective = db.Column(db.Text, nullable=True)

    objective = db.Column(db.Text, nullable=True)

    assessment = db.Column(db.Text, nullable=True)

    plan = db.Column(db.Text, nullable=True)

    signed_by = db.Column(db.String(100), nullable=True)


    def __repr__(self):
         return f"<Visit on {self.date_time.strftime('%Y-%m-%d %H:%M')} for Patient ID {self.patient_id}>"
