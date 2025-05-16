# docpat/docpat/forms.py

from flask_wtf import FlaskForm
import datetime
from wtforms import StringField, IntegerField, TextAreaField, BooleanField, DateField, FloatField, SubmitField, SelectField, TimeField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, ValidationError
from wtforms.widgets import DateInput, TimeInput
# Importiere Patient Modell für das SelectField in Reports und PatientSelectForm
from .models import Patient

def is_integer_string(form, field):
    if field.data:
        try:
            value = int(field.data)
            if value < 0:
                 raise ValidationError('Der Wert muss positiv sein.')
        except ValueError:
            raise ValidationError('Bitte geben Sie eine gültige Zahl ein.')

VACCINE_CHOICES = [
    ('', '--- Impfung auswählen ---'),
    ('DTaP-IPV-Hib-HBV', 'Sechsfach-Impfung'),
    ('Pneumokokken', 'Pneumokokken'),
    ('Rotaviren', 'Rotaviren'),
    ('MenB', 'Meningokokken B'),
    ('MenC', 'Meningokokken C'),
    ('MMR-V', 'MMR-Varizellen'),
    ('HPV', 'HPV'),
    ('Influenza', 'Influenza (Grippe)'),
    ('FSME', 'FSME'),
    ('Hepatitis A', 'Hepatitis A'),
    ('Hepatitis B', 'Hepatitis B'),
    ('Tetanus', 'Tetanus'),
    ('Diphtherie', 'Diphtherie'),
    ('Pertussis', 'Pertussis (Keuchhusten)'),
    ('Polio', 'Polio (Kinderlähmung)'),
    ('Zoster', 'Herpes Zoster (Gürtelrose)'),
    ('COVID-19', 'COVID-19'),
    ('Anderer', 'Anderer')
]

INJECTION_CHOICES = [
    ('', '--- Injektionsmittel auswählen ---'),
    ('Vitamin B1', 'Vitamin B1'),
    ('Vitamin B2', 'Vitamin B2'),
    ('Vitamin B6', 'Vitamin B6'),
    ('Vitamin B12', 'Vitamin B12'),
    ('Folsäure', 'Folsäure'),
    ('NaCl', 'NaCl')
]

ROUTE_CHOICES = [
    ('', '--- Weg auswählen ---'),
    ('i.m.', 'intramuskulär (i.m.)'),
    ('s.c.', 'subkutan (s.c.)'),
    ('i.v.', 'intravenös (i.v.)'),
    ('i.d.', 'intradermal (i.d.)'),
    ('oral', 'oral'),
    ('andere', 'andere')
]

# Auswahlmöglichkeiten für Dropdown-Listen (unverändert)
LAND_CHOICES = [
    ('', '--- Land auswählen ---'),
    ('Deutschland', 'Deutschland'),
    ('Österreich', 'Österreich'),
    ('Schweiz', 'Schweiz'),
    ('Anderes', 'Anderes')
]

ETHNIE_CHOICES = [
    ('', '--- Ethnie auswählen ---'),
    ('Kaukasisch', 'Kaukasisch'),
    ('Afroamerikanisch', 'Afroamerikanisch'),
    ('Asiatisch', 'Asiatisch'),
    ('Hispanisch', 'Hispanisch'),
    ('Anderes', 'Anderes')
]

BLUTGRUPPE_CHOICES = [
    ('', '--- Blutgruppe auswählen ---'),
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('0+', '0+'),
    ('0-', '0-'),
    ('Unbekannt', 'Unbekannt')
]


class PatientForm(FlaskForm):
    vorname = StringField('Vorname', validators=[DataRequired()])
    nachname = StringField('Nachname', validators=[DataRequired()])
    # GEÄNDERT: Alter entfernt, Geburtsdatum hinzugefügt
    # alter = IntegerField('Alter', validators=[Optional(), NumberRange(min=0)])
    geburtsdatum = DateField('Geburtsdatum', validators=[Optional()], widget=DateInput())

    geschlecht = StringField('Geschlecht', validators=[Optional()])

    adresse = StringField('Adresse', validators=[Optional()])
    plz = StringField('PLZ', validators=[Optional()])
    ort = StringField('Ort', validators=[Optional()])

    # GEÄNDERT: Land, Ethnie, Blutgruppe als SelectFields mit Choices
    land = SelectField('Land', choices=LAND_CHOICES, validators=[Optional()])
    ethnie = SelectField('Ethnie', choices=ETHNIE_CHOICES, validators=[Optional()])
    blutgruppe = SelectField('Blutgruppe', choices=BLUTGRUPPE_CHOICES, validators=[Optional()])

    telefon = StringField('Telefon', validators=[Optional()])
    email = StringField('E-Mail', validators=[Optional(), Email()])
    krankenkasse = StringField('Krankenkasse', validators=[Optional()])


    diagnosen = TextAreaField('Diagnosen', validators=[Optional()])
    ernaehrung = TextAreaField('Ernährungsgewohnheiten', validators=[Optional()])
    medikation = TextAreaField('Medikation', validators=[Optional()])
    drogen = TextAreaField('Drogenanamnese', validators=[Optional()])

    # NEU: Feld für Raucher
    raucher = BooleanField('Raucher')

    # Feld OP-Vorgeschichte, muss hier sein, da es im Modell ist
    op_vorgeschichte = TextAreaField('OP-Vorgeschichte', validators=[Optional()])


    allergien = TextAreaField('Allergien', validators=[Optional()])

    risikogruppe = BooleanField('Risikogruppe')

    # Diese Felder werden im Formular nicht mehr benötigt, da sie dynamisch berechnet werden
    # letzte_untersuchung = DateField('Letzte Untersuchung', validators=[Optional()], widget=DateInput())
    # naechste_untersuchung = DateField('Nächste Untersuchung', validators=[Optional()], widget=DateInput())

    submit = SubmitField('Patient speichern')


class VitalSignForm(FlaskForm):
    height_cm = FloatField('Größe (cm)', validators=[Optional(), NumberRange(min=0)])
    weight_kg = FloatField('Gewicht (kg)', validators=[Optional(), NumberRange(min=0)])
    puls = StringField('Puls (bpm)', validators=[Optional(), is_integer_string])
    blood_pressure = StringField('Blutdruck (mmHg)', validators=[Optional()])
    temperature_celsius = FloatField('Temperatur (°C)', validators=[Optional()])
    fev1 = FloatField('FEV1 (Liter)', validators=[Optional(), NumberRange(min=0)])
    fvc = FloatField('FVC (Liter)', validators=[Optional(), NumberRange(min=0)])
    timestamp = DateField('Datum der Messung', validators=[DataRequired()], widget=DateInput())
    submit = SubmitField('Vitalwerte speichern')

class VaccinationForm(FlaskForm):
    date = DateField('Datum der Impfung', validators=[DataRequired()], widget=DateInput())
    vaccine_against = SelectField('Impfung gegen', choices=VACCINE_CHOICES, validators=[DataRequired()])
    vaccine_name = StringField('Impfstoff', validators=[DataRequired()])
    dosage = StringField('Dosis/Menge (ml)', validators=[Optional()])
    route = SelectField('Verabreichungsform', choices=ROUTE_CHOICES, validators=[Optional()])
    batch_number = StringField('Chargen-Nr.', validators=[Optional()])
    observations = TextAreaField('Beobachtungen', validators=[Optional()])
    signed_by = StringField('Unterzeichnet von', validators=[Optional()])
    next_dosage_date = DateField('Datum nächste Dosis', validators=[Optional()], widget=DateInput())
    submit = SubmitField('Impfung speichern')

class InjectionForm(FlaskForm):
    date = DateField('Datum der Injektion', validators=[DataRequired()], widget=DateInput())
    injection_substance = SelectField('Injektionsmittel', choices=INJECTION_CHOICES, validators=[DataRequired()])
    dosage = StringField('Dosis/Menge (ml)', validators=[Optional()])
    route = SelectField('Verabreichungsform', choices=ROUTE_CHOICES, validators=[Optional()])
    batch_number = StringField('Chargen-Nr.', validators=[Optional()])
    observations = TextAreaField('Beobachtungen', validators=[Optional()])
    signed_by = StringField('Unterzeichnet von', validators=[Optional()])
    next_dosage_date = DateField('Datum nächste Dosis', validators=[Optional()], widget=DateInput())
    submit = SubmitField('Injektion speichern')


class AppointmentForm(FlaskForm):
    patient_id = SelectField('Patient', validators=[DataRequired()], choices=[])

    date = DateField('Datum', validators=[DataRequired()], widget=DateInput())
    time = TimeField('Uhrzeit', validators=[DataRequired()], widget=TimeInput())

    description = StringField('Beschreibung', validators=[DataRequired()])
    duration_minutes = IntegerField('Dauer (Minuten)', validators=[Optional(), NumberRange(min=1)])
    notes = TextAreaField('Notizen', validators=[Optional()])

    submit = SubmitField('Termin speichern')


class VisitForm(FlaskForm):
    patient_id = SelectField('Patient', validators=[DataRequired()], choices=[])

    date = DateField('Datum der Visite', validators=[DataRequired()], widget=DateInput(), default=datetime.date.today)
    time = TimeField('Uhrzeit der Visite', validators=[DataRequired()], widget=TimeInput(), default=datetime.datetime.now().time())

    subjective = TextAreaField('Subjektiv (Patientenangaben)', validators=[Optional()])
    objective = TextAreaField('Objektiv (Befunde)', validators=[Optional()])
    assessment = TextAreaField('Beurteilung/Diagnose', validators=[Optional()])
    plan = TextAreaField('Plan/Empfehlungen', validators=[Optional()])
    signed_by = StringField('Unterzeichnet von', validators=[Optional()])

    submit = SubmitField('Visite speichern')

# Formular für Reports nach Datumsbereich (Termine, Visiten) (unverändert)
class ReportDateRangeForm(FlaskForm):
    start_date = DateField('Startdatum', validators=[Optional()], widget=DateInput())
    end_date = DateField('Enddatum', validators=[Optional()], widget=DateInput())
    submit = SubmitField('Report generieren')

    def validate(self, extra_validators=None):
        check_validators = super().validate(extra_validators=extra_validators)
        if not check_validators:
            return False

        if self.end_date.data and not self.start_date.data:
            self.start_date.errors.append('Wenn ein Enddatum angegeben ist, muss auch ein Startdatum angegeben werden.')
            return False
        if self.start_date.data and self.end_date.data and self.start_date.data > self.end_date.data:
             self.end_date.errors.append('Das Enddatum kann nicht vor dem Startdatum liegen.')
             return False
        return True

# Formular für Reports nach Patient und Datumsbereich (Impfungen, Injektionen, Vitalwerte) (unverändert)
class ReportPatientDateRangeForm(FlaskForm):
    patient_id = SelectField('Patient', validators=[Optional()], choices=[])

    start_date = DateField('Startdatum', validators=[Optional()], widget=DateInput())
    end_date = DateField('Enddatum', validators=[Optional()], widget=DateInput())

    submit = SubmitField('Report generieren')

    def validate(self, extra_validators=None):
        check_validators = super().validate(extra_validators=extra_validators)
        if not check_validators:
            return False

        if self.end_date.data and not self.start_date.data:
            self.start_date.errors.append('Wenn ein Enddatum angegeben ist, muss auch ein Startdatum angegeben werden.')
            return False
        if self.start_date.data and self.end_date.data and self.start_date.data > self.end_date.data:
             self.end_date.errors.append('Das Enddatum kann nicht vor dem Startdatum liegen.')
             return False
        return True

# Formular für einfache Patientensuche (Für Dashboard) (unverändert)
class DashboardPatientSearchForm(FlaskForm):
    search_term = StringField('Patient suchen', validators=[Optional()])
    submit = SubmitField('Suchen')

# Formular zur Auswahl eines Patienten (unverändert)
class PatientSelectForm(FlaskForm):
     patient_id = SelectField('Patient auswählen', validators=[DataRequired()], choices=[])
     submit = SubmitField('Weiter')

