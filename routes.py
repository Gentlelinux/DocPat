# docpat/docpat/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
# Importiere alle Modelle
from .models import Patient, VitalSign, Vaccination, Injection, Appointment, Visit
# Importiere alle Formulare
from .forms import PatientForm, VitalSignForm, VaccinationForm, InjectionForm, AppointmentForm, VisitForm, ReportDateRangeForm, ReportPatientDateRangeForm, DashboardPatientSearchForm, PatientSelectForm
import datetime
# Importiere func aus sqlalchemy für Datenbankfunktionen wie date(), lower(), or_
from sqlalchemy import func, desc, asc, or_

# Erstelle einen Blueprint.
bp = Blueprint('bp', __name__)

# Hilfsfunktion zur BMI-Berechnung (unverändert)
def calculate_bmi(weight_kg, height_cm):
    """Berechnet den BMI aus Gewicht (kg) und Größe (cm)."""
    if weight_kg is None or height_cm is None or not isinstance(weight_kg, (int, float)) or not isinstance(height_cm, (int, float)) or height_cm <= 0:
        return None
    try:
        height_m = height_cm / 100.0
        bmi = weight_kg / (height_m ** 2)
        return round(bmi, 2)
    except (TypeError, ValueError):
        return None

# Startseite ist das Dashboard - Endpunkt 'bp.index'
@bp.route('/')
def index():
    # Daten für das Dashboard holen
    total_patients = db.session.query(Patient).count()

    # Nächste Termine (z.b. die nächsten 5, beginnend ab heute)
    now = datetime.datetime.now()
    upcoming_appointments = db.session.query(Appointment)\
        .filter(Appointment.date_time >= now)\
        .order_by(asc(Appointment.date_time))\
        .limit(5)\
        .all()

    # Letzte Visiten (z.b. die letzten 5)
    recent_visits = db.session.query(Visit)\
        .filter(Visit.date_time.isnot(None))\
        .order_by(desc(Visit.date_time))\
        .limit(5)\
        .all()

    # Formular für Patientensuche erstellen
    patient_search_form = DashboardPatientSearchForm()


    # Rendere das neue Dashboard-Template und übergib die Daten
    return render_template('dashboard.html',
                           title='Dashboard',
                           total_patients=total_patients,
                           upcoming_appointments=upcoming_appointments,
                           recent_visits=recent_visits,
                           patient_search_form=patient_search_form,
                           current_date=datetime.date.today())


# Seite zum Hinzufügen eines neuen Patienten - Endpunkt 'bp.add_patient'
@bp.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    form = PatientForm()
    if form.validate_on_submit():
        new_patient = Patient(
            vorname=form.vorname.data,
            nachname=form.nachname.data,
            # Geburtsdatum kommt vom Formular
            geburtsdatum=form.geburtsdatum.data,
            geschlecht=form.geschlecht.data,
            adresse=form.adresse.data,
            plz=form.plz.data,
            ort=form.ort.data,
            # Land, Ethnie, Blutgruppe kommen vom Formular
            land=form.land.data,
            ethnie=form.ethnie.data,
            blutgruppe=form.blutgruppe.data,
            telefon=form.telefon.data,
            email=form.email.data,
            krankenkasse=form.krankenkasse.data,
            diagnosen=form.diagnosen.data,
            ernaehrung=form.ernaehrung.data,
            medikation=form.medikation.data,
            drogen=form.drogen.data,
            raucher=form.raucher.data, # Raucher kommt vom Formular
            op_vorgeschichte=form.op_vorgeschichte.data, # OP-Vorgeschichte kommt vom Formular
            allergien=form.allergien.data,
            risikogruppe=form.risikogruppe.data,
            # Die Felder alter, letzte_untersuchung und naechste_untersuchung
            # existieren nicht mehr im Modell oder werden dynamisch angezeigt
        )
        db.session.add(new_patient)
        db.session.commit()
        flash('Patient erfolgreich hinzugefügt!', 'success')
        return redirect(url_for('bp.patient_list')) # Verlinkt zur Patientenliste
    return render_template('add_patient.html', title='Neuer Patient', form=form) # Rendert das Anlegeformular

# Seite, die alle Patienten auflistet - Endpunkt 'bp.patient_list' (unverändert)
@bp.route('/patients')
def patient_list():
    search_term = request.args.get('search_term', '').strip()

    query = Patient.query

    if search_term:
        search_pattern = f"%{search_term.lower()}%"
        query = query.filter(or_(
            func.lower(Patient.vorname).like(search_pattern),
            func.lower(Patient.nachname).like(search_pattern)
        ))
        flash(f'Suche nach "{search_term}" ergab {query.count()} Ergebnisse.', 'info')

    patients = query.order_by(Patient.nachname).all()

    return render_template('patient_list.html',
                           title='Patientenliste',
                           patients=patients,
                           search_term=search_term)

# Seite, die die Details eines einzelnen Patienten anzeigt - Endpunkt 'bp.view_patient'
@bp.route('/patient/<int:patient_id>')
def view_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    # Datum der letzten Visite dynamisch ermitteln
    last_visit = db.session.query(Visit)\
        .filter(Visit.patient_id == patient.id)\
        .order_by(desc(Visit.date_time))\
        .first() # Holt die neueste Visite (falls vorhanden)
    last_visit_date = last_visit.date_time.date() if last_visit else None # Extrahiere nur das Datum

    # Datum/Zeit des nächsten Termins dynamisch ermitteln
    now = datetime.datetime.now()
    next_appointment = db.session.query(Appointment)\
        .filter(Appointment.patient_id == patient.id)\
        .filter(Appointment.date_time >= now)\
        .order_by(asc(Appointment.date_time))\
        .first() # Holt den nächsten Termin (falls vorhanden)
    next_appointment_datetime = next_appointment.date_time if next_appointment else None # Hol das ganze datetime Objekt

    # Heutiges Datum holen und an das Template übergeben (für Altersberechnung)
    today_date = datetime.date.today()


    # Vitalwerte, Impfungen, Injektionen, Termine und Visiten sind verfügbar
    return render_template('view_patient.html',
                           title=f'Patient: {patient.nachname}, {patient.vorname}',
                           patient=patient,
                           last_visit_date=last_visit_date, # Letzte Visite Datum übergeben
                           next_appointment_datetime=next_appointment_datetime, # Nächster Termin Datetime übergeben
                           today_date=today_date) # Heutiges Datum übergeben


# Route zum Bearbeiten eines Patienten - Endpunkt 'bp.edit_patient'
@bp.route('/patient/<int:patient_id>/edit', methods=['GET', 'POST'])
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = PatientForm(obj=patient) # Formular mit Patientendaten vorbefüllen

    if form.validate_on_submit():
        # populate_obj() ohne exclude
        form.populate_obj(patient)

        db.session.commit()
        flash('Patientendaten erfolgreich aktualisiert!', 'success')
        return redirect(url_for('bp.view_patient', patient_id=patient.id)) # Zur Patientendetailseite

    # Beim GET-Request oder Validierungsfehler, Template rendern
    return render_template('edit_patient.html', title=f'Patientendaten bearbeiten für {patient.nachname}', form=form, patient=patient)

# Route zum Löschen eines Patienten - Endpunkt 'bp.delete_patient'
@bp.route('/patient/<int:patient_id>/delete', methods=['POST'])
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    # Hinweis: Löschen von Patienten mit verknüpften Einträgen kann zu Problemen führen.
    # In einem echten Projekt müsste man abhängige Einträge kaskadierend löschen,
    # weichlöschen oder das Löschen verhindern. Hier für Einfachheit direkt löschen.

    db.session.delete(patient)
    db.session.commit()
    flash('Patient erfolgreich gelöscht!', 'success')

    return redirect(url_for('bp.patient_list')) # Zurück zur Patientenliste nach dem Löschen


# Seite zum Hinzufügen von Vitalwerten - Endpunkt 'bp.add_vital_sign' (unverändert)
@bp.route('/patient/<int:patient_id>/add_vital_sign', methods=['GET', 'POST'])
def add_vital_sign(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = VitalSignForm()

    if form.validate_on_submit():
        height = form.height_cm.data
        weight = form.weight_kg.data
        measurement_date = form.timestamp.data
        calculated_bmi = calculate_bmi(weight, height)

        new_vital_sign = VitalSign(
            height_cm=height,
            weight_kg=weight,
            bmi=calculated_bmi,
            puls=int(form.puls.data) if form.puls.data else None,
            blood_pressure=form.blood_pressure.data,
            temperature_celsius=form.temperature_celsius.data,
            fev1=form.fev1.data,
            fvc=form.fvc.data,
            timestamp=form.timestamp.data,
            patient_id=patient.id
        )
        db.session.add(new_vital_sign)
        db.session.commit()
        flash('Vitalwerte erfolgreich hinzugefügt!', 'success')
        return redirect(url_for('bp.view_patient', patient_id=patient.id))
    return render_template('add_vital_sign.html', title=f'Vitalwerte für {patient.nachname}', form=form, patient=patient)


# Route zum Bearbeiten von Vitalwerten - Endpunkt 'bp.edit_vital_sign' (unverändert)
@bp.route('/vitalsign/<int:vital_sign_id>/edit', methods=['GET', 'POST'])
def edit_vital_sign(vital_sign_id):
    vital_sign = VitalSign.query.get_or_404(vital_sign_id)
     # Patient Objekt holen
    patient = Patient.query.get_or_404(vital_sign.patient_id)
    form = VitalSignForm(obj=vital_sign)

    if form.validate_on_submit():
        height = form.height_cm.data
        weight = form.weight_kg.data
        measurement_date = form.timestamp.data

        calculated_bmi = calculate_bmi(weight, height)

        form.populate_obj(vital_sign)
        vital_sign.bmi = calculated_bmi

        db.session.commit()
        flash('Vitalwerte erfolgreich aktualisiert!', 'success')
        return redirect(url_for('bp.view_patient', patient_id=vital_sign.patient_id))

    # patient Objekt an das Template übergeben
    return render_template('edit_vital_sign.html', title=f'Vitalwerte bearbeiten für {patient.nachname}', form=form, vital_sign=vital_sign, patient=patient)


# Route zum Löschen von Vitalwerten - Endpunkt 'bp.delete_vital_sign' (unverändert)
@bp.route('/vitalsign/<int:vital_sign_id>/delete', methods=['POST'])
def delete_vital_sign(vital_sign_id):
    vital_sign = VitalSign.query.get_or_404(vital_sign_id)
    patient_id = vital_sign.patient_id

    db.session.delete(vital_sign)
    db.session.commit()
    flash('Vitalwerte erfolgreich gelöscht!', 'success')

    return redirect(url_for('bp.view_patient', patient_id=patient_id))


# Route zum Hinzufügen einer Impfung (unverändert)
@bp.route("/patient/<int:patient_id>/add_vaccination", methods=['GET', 'POST'])
def add_vaccination(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = VaccinationForm()
    if form.validate_on_submit():
        new_vaccination = Vaccination(
            date=form.date.data,
            vaccine_against=form.vaccine_against.data,
            vaccine_name=form.vaccine_name.data,
            dosage=form.dosage.data,
            route=form.route.data,
            batch_number=form.batch_number.data,
            observations=form.observations.data,
            signed_by=form.signed_by.data,
            next_dosage_date=form.next_dosage_date.data,
            patient_id=patient.id
        )
        db.session.add(new_vaccination)
        db.session.commit()
        flash('Impfung erfolgreich hinzugefüht!', 'success')
        return redirect(url_for('bp.view_patient', patient_id=patient.id))
    return render_template('add_vaccination.html', title=f'Neue Impfung für {patient.nachname}', form=form, patient=patient)

# Route zum Bearbeiten einer Impfung - Endpunkt 'bp.edit_vaccination' (unverändert)
@bp.route("/vaccination/<int:vaccination_id>/edit", methods=['GET', 'POST'])
def edit_vaccination(vaccination_id):
    vaccination = Vaccination.query.get_or_404(vaccination_id)
     # Patient Objekt holen
    patient = Patient.query.get_or_404(vaccination.patient_id)
    form = VaccinationForm(obj=vaccination)

    if form.validate_on_submit():
        form.populate_obj(vaccination)
        db.session.commit()
        flash('Impfung erfolgreich aktualisiert!', 'success')
        return redirect(url_for('bp.view_patient', patient_id=vaccination.patient_id))
    # patient Objekt an das Template übergeben
    return render_template('edit_vaccination.html', title=f'Impfung bearbeiten für {patient.nachname}', form=form, vaccination=vaccination, patient=patient)

# Route zum Löschen einer Impfung - Endpunkt 'bp.delete_vaccination' (unverändert)
@bp.route("/vaccination/<int:vaccination_id>/delete", methods=['POST'])
def delete_vaccination(vaccination_id):
    vaccination = Vaccination.query.get_or_404(vaccination_id)
    patient_id = vaccination.patient_id
    db.session.delete(vaccination)
    db.session.commit()
    flash('Impfung erfolgreich gelöscht!', 'success')
    return redirect(url_for('bp.view_patient', patient_id=patient_id))

# Route zum Hinzufügen einer Injektion (unverändert)
@bp.route("/patient/<int:patient_id>/add_injection", methods=['GET', 'POST'])
def add_injection(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = InjectionForm()
    if form.validate_on_submit():
        new_injection = Injection(
            date=form.date.data,
            injection_substance=form.injection_substance.data,
            dosage=form.dosage.data,
            route=form.route.data,
            batch_number=form.batch_number.data,
            observations=form.observations.data,
            signed_by=form.signed_by.data,
            next_dosage_date=form.next_dosage_date.data,
            patient_id=patient.id
        )
        db.session.add(new_injection)
        db.session.commit()
        flash('Injektion erfolgreich hinzugefügt!', 'success')
        return redirect(url_for('bp.view_patient', patient_id=patient.id))
    return render_template('add_injection.html', title=f'Neue Injektion für {patient.nachname}', form=form, patient=patient)

# Route zum Bearbeiten einer Injektion - Endpunkt 'bp.edit_injection' (unverändert)
@bp.route("/injection/<int:injection_id>/edit", methods=['GET', 'POST'])
def edit_injection(injection_id):
    injection = Injection.query.get_or_404(injection_id)
     # Patient Objekt holen
    patient = Patient.query.get_or_404(injection.patient_id)
    form = InjectionForm(obj=injection)

    if form.validate_on_submit():
        form.populate_obj(injection)
        db.session.commit()
        flash('Injektion erfolgreich aktualisiert!', 'success')
        return redirect(url_for('bp.view_patient', patient_id=injection.patient_id))
    # patient Objekt an das Template übergeben
    return render_template('edit_injection.html', title=f'Injektion bearbeiten für {patient.nachname}', form=form, injection=injection, patient=patient)


# Route zum Löschen einer Injektion - Endpunkt 'bp.delete_injection' (unverändert)
@bp.route("/injection/<int:injection_id>/delete", methods=['POST'])
def delete_injection(injection_id):
    injection = Injection.query.get_or_404(injection_id)
    patient_id = injection.patient_id
    db.session.delete(injection)
    db.session.commit()
    flash('Injektion erfolgreich gelöscht!', 'success')
    return redirect(url_for('bp.view_patient', patient_id=patient_id))


# Route zum Hinzufügen eines Termins für einen bestimmten Patienten (unverändert)
@bp.route("/patient/<int:patient_id>/add_appointment", methods=['GET', 'POST'])
def add_appointment_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = AppointmentForm()
    patients = Patient.query.order_by(Patient.nachname).all()
    form.patient_id.choices = [('', '--- Patient auswählen ---')] + [(str(p.id), f"{p.nachname}, {p.vorname}") for p in patients]

    if request.method == 'GET':
        form.patient_id.data = str(patient_id)

    if form.validate_on_submit():
        selected_patient_id = form.patient_id.data
        combined_date_time = datetime.datetime.combine(form.date.data, form.time.data)
        new_appointment = Appointment(
            date_time=combined_date_time,
            description=form.description.data,
            duration_minutes=form.duration_minutes.data,
            notes=form.notes.data,
            patient_id=selected_patient_id
        )
        db.session.add(new_appointment)
        db.session.commit()
        flash('Termin erfolgreich hinzugefügt!', 'success')
        return redirect(url_for('bp.view_patient', patient_id=selected_patient_id))

    try:
        patient = Patient.query.get_or_404(patient_id)
    except:
        patient = None
    return render_template('add_appointment.html', title='Neuer Termin', form=form, patient=patient)


# NEU: Route zum Hinzufügen eines Termins (allgemein, von der Terminübersicht) (unverändert)
@bp.route("/add_appointment", methods=['GET', 'POST'])
def add_appointment_general():
    form = AppointmentForm()
    patients = Patient.query.order_by(Patient.nachname).all()
    form.patient_id.choices = [('', '--- Patient auswählen ---')] + [(str(p.id), f"{p.nachname}, {p.vorname}") for p in patients]

    if form.validate_on_submit():
        selected_patient_id = form.patient_id.data
        combined_date_time = datetime.datetime.combine(form.date.data, form.time.data)
        new_appointment = Appointment(
            date_time=combined_date_time,
            description=form.description.data,
            duration_minutes=form.duration_minutes.data,
            notes=form.notes.data,
            patient_id=selected_patient_id
        )
        db.session.add(new_appointment)
        db.session.commit()
        flash('Termin erfolgreich hinzugefügt!', 'success')
        return redirect(url_for('bp.list_appointments'))
    return render_template('add_appointment.html', title='Neuen Termin', form=form)


# Route zum Bearbeiten eines spezifischen Termins - Endpunkt 'bp.edit_appointment' (unverändert)
@bp.route("/appointment/<int:appointment_id>/edit", methods=['GET', 'POST'])
def edit_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
     # Patient Objekt holen
    patient = Patient.query.get_or_404(appointment.patient_id)
    form = AppointmentForm(obj=appointment)
    patients = Patient.query.order_by(Patient.nachname).all()
    form.patient_id.choices = [('', '--- Patient auswählen ---')] + [(str(p.id), f"{p.nachname}, {p.vorname}") for p in patients]

    if request.method == 'GET':
        if appointment.date_time:
            form.date.data = appointment.date_time.date()
            form.time.data = appointment.date_time.time()
        form.patient_id.data = str(appointment.patient_id)

    if form.validate_on_submit():
        combined_date_time = datetime.datetime.combine(form.date.data, form.time.data)
        selected_patient_id = form.patient_id.data

        form.populate_obj(appointment)
        appointment.date_time = combined_date_time
        appointment.patient_id = selected_patient_id

        db.session.commit()
        flash('Termin erfolgreich aktualisiert!', 'success')
        return redirect(url_for('bp.list_appointments'))

    # patient Objekt an das Template übergeben
    return render_template('edit_appointment.html', title=f'Termin bearbeiten', form=form, appointment=appointment, patient=patient)

# Route zum Löschen eines Termins - Endpunkt 'bp.delete_appointment' (unverändert)
@bp.route("/appointment/<int:appointment_id>/delete", methods=['POST'])
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    patient_id = appointment.patient_id
    db.session.delete(appointment)
    db.session.commit()
    flash('Termin erfolgreich gelöscht!', 'success')
    return redirect(url_for('bp.list_appointments'))


# Route zum Hinzufügen einer Visite für einen bestimmten Patienten (unverändert)
@bp.route("/patient/<int:patient_id>/add_visit", methods=['GET', 'POST'])
def add_visit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = VisitForm()
    patients = Patient.query.order_by(Patient.nachname).all()
    form.patient_id.choices = [('', '--- Patient auswählen ---')] + [(str(p.id), f"{p.nachname}, {p.vorname}") for p in patients]

    if request.method == 'GET':
        form.patient_id.data = str(patient_id)

    if form.validate_on_submit():
        selected_patient_id = form.patient_id.data
        combined_date_time = datetime.datetime.combine(form.date.data, form.time.data)
        new_visit = Visit(
            date_time=combined_date_time,
            subjective=form.subjective.data,
            objective=form.objective.data,
            assessment=form.assessment.data,
            plan=form.plan.data,
            signed_by=form.signed_by.data,
            patient_id=selected_patient_id
        )
        db.session.add(new_visit)
        db.session.commit()
        flash('Visite erfolgreich hinzugefügt!', 'success')
        return redirect(url_for('bp.view_patient', patient_id=selected_patient_id))

    try:
        patient = Patient.query.get_or_404(patient_id)
    except:
        patient = None
    return render_template('add_visit.html', title='Neue Visite', form=form, patient=patient)


# NEU: Route zum Hinzufügen einer Visite (allgemein, von der Visitenübersicht) (unverändert)
@bp.route("/add_visit", methods=['GET', 'POST'])
def add_visit_general():
    form = VisitForm()
    patients = Patient.query.order_by(Patient.nachname).all()
    form.patient_id.choices = [('', '--- Patient auswählen ---')] + [(str(p.id), f"{p.nachname}, {p.vorname}") for p in patients]

    if form.validate_on_submit():
        selected_patient_id = form.patient_id.data
        combined_date_time = datetime.datetime.combine(form.date.data, form.time.data)
        new_visit = Visit(
            date_time=combined_date_time,
            subjective=form.subjective.data,
            objective=form.objective.data,
            assessment=form.assessment.data,
            plan=form.plan.data,
            signed_by=form.signed_by.data,
            patient_id=selected_patient_id
        )
        db.session.add(new_visit)
        db.session.commit()
        flash('Visite erfolgreich hinzugefügt!', 'success')
        return redirect(url_for('bp.list_visits'))
    return render_template('add_visit.html', title='Neue Visite', form=form)


# Route zum Bearbeiten einer Visite - Endpunkt 'bp.edit_visit' (unverändert)
@bp.route("/visit/<int:visit_id>/edit", methods=['GET', 'POST'])
def edit_visit(visit_id):
    visit = Visit.query.get_or_404(visit_id)
     # Patient Objekt holen
    patient = Patient.query.get_or_404(visit.patient_id)
    form = VisitForm(obj=visit)
    patients = Patient.query.order_by(Patient.nachname).all()
    form.patient_id.choices = [('', '--- Patient auswählen ---')] + [(str(p.id), f"{p.nachname}, {p.vorname}") for p in patients]

    if request.method == 'GET':
        if visit.date_time:
            form.date.data = visit.date_time.date()
            form.time.data = visit.date_time.time()
        form.patient_id.data = str(visit.patient_id)

    if form.validate_on_submit():
        combined_date_time = datetime.datetime.combine(form.date.data, form.time.data)
        selected_patient_id = form.patient_id.data

        form.populate_obj(visit)
        visit.date_time = combined_date_time
        visit.patient_id = selected_patient_id

        db.session.commit()
        flash('Visite erfolgreich aktualisiert!', 'success')
        return redirect(url_for('bp.list_visits'))

    # patient Objekt an das Template übergeben
    return render_template('edit_visit.html', title=f'Visite bearbeiten', form=form, visit=visit, patient=patient)


# Route zum Löschen einer Visite - Endpunkt 'bp.delete_visit' (unverändert)
@bp.route("/visit/<int:visit_id>/delete", methods=['POST'])
def delete_visit(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    patient_id = visit.patient_id
    db.session.delete(visit)
    db.session.commit()
    flash('Visite erfolgreich gelöscht!', 'success')
    return redirect(url_for('bp.list_visits'))


# Reports Bereich (unverändert)
@bp.route("/reports")
def reports_index():
    return render_template('reports_index.html', title='Reports')

# Route für die Übersicht aller Termine (unverändert)
@bp.route("/appointments")
def list_appointments():
    appointments = Appointment.query.order_by(Appointment.date_time.desc()).all()
    return render_template('appointment_list.html', title='Alle Termine', appointments=appointments)

# Route für die Übersicht aller Visiten (unverändert)
@bp.route("/visits")
def list_visits():
    visits = Visit.query.order_by(Visit.date_time.desc()).all()
    return render_template('visit_list.html', title='Alle Visiten/Behandlungen', visits=visits)


# Report: Termine nach Datum (verwendet ReportDateRangeForm) (unverändert)
@bp.route("/reports/appointments_by_date", methods=['GET', 'POST'])
def report_appointments_by_date():
    form = ReportDateRangeForm()

    appointments = []
    start_date = None
    end_date = None

    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data

        query = Appointment.query

        if start_date:
             query = query.filter(func.date(Appointment.date_time) >= start_date)
        if end_date:
             query = query.filter(func.date(Appointment.date_time) <= end_date)

        appointments = query.order_by(Appointment.date_time.asc()).all()

        return render_template('report_appointments_by_date.html',
                               title='Report: Termine nach Datum',
                               form=form,
                               appointments=appointments,
                               start_date=start_date,
                               end_date=end_date)

    return render_template('report_appointments_by_date.html', title='Report: Termine nach Datum', form=form, appointments=[], start_date=None, end_date=None)


# Report: Visiten nach Datum (verwendet ReportDateRangeForm) (unverändert)
@bp.route("/reports/visits_by_date", methods=['GET', 'POST'])
def report_visits_by_date():
    form = ReportDateRangeForm()

    visits = []
    start_date = None
    end_date = None

    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data

        query = Visit.query

        if start_date:
             query = query.filter(func.date(Visit.date_time) >= start_date)
        if end_date:
             query = query.filter(func.date(Visit.date_time) <= end_date)

        visits = query.order_by(Visit.date_time.asc()).all()

        return render_template('report_visits_by_date.html',
                               title='Report: Visiten nach Datum',
                               form=form,
                               visits=visits,
                               start_date=start_date,
                               end_date=end_date)


    return render_template('report_visits_by_date.html', title='Report: Visiten nach Datum', form=form, visits=[], start_date=None, end_date=None)

# Report: Impfungen nach Patient und Datum (verwendet ReportPatientDateRangeForm) (unverändert)
@bp.route("/reports/vaccinations_by_patient_date", methods=['GET', 'POST'])
def report_vaccinations_by_patient_date():
    form = ReportPatientDateRangeForm()

    patients_all = Patient.query.order_by(Patient.nachname).all()
    form.patient_id.choices = [('', 'Alle Patienten')] + [(str(p.id), f"{p.nachname}, {p.vorname}") for p in patients_all]


    vaccinations = []
    selected_patient = None
    start_date = None
    end_date = None


    if form.validate_on_submit():
        patient_id = form.patient_id.data
        start_date = form.start_date.data
        end_date = form.end_date.data

        query = Vaccination.query

        if patient_id:
            query = query.filter(Vaccination.patient_id == patient_id)
            selected_patient = Patient.query.get(patient_id)

        if start_date:
             query = query.filter(func.date(Vaccination.date) >= start_date)
        if end_date:
             query = query.filter(func.date(Vaccination.date) <= end_date)


        vaccinations = query.order_by(Vaccination.date.asc()).all()


        return render_template('report_vaccinations_by_patient_date.html',
                               title='Report: Impfungen nach Patient und Datum',
                               form=form,
                               vaccinations=vaccinations,
                               selected_patient=selected_patient,
                               start_date=start_date,
                               end_date=end_date)


    # Beim GET oder Validierungsfehler, Formular ohne Ergebnisse anzeigen
    return render_template('report_vaccinations_by_patient_date.html', title='Report: Impfungen nach Patient und Datum', form=form, vaccinations=[], selected_patient=None, start_date=None, end_date=None)


# Report: Injektionen nach Patient und Datum (verwendet ReportPatientDateRangeForm) (unverändert)
@bp.route("/reports/injections_by_patient_date", methods=['GET', 'POST'])
def report_injections_by_patient_date():
    form = ReportPatientDateRangeForm()

    patients_all = Patient.query.order_by(Patient.nachname).all()
    form.patient_id.choices = [('', 'Alle Patienten')] + [(str(p.id), f"{p.nachname}, {p.vorname}") for p in patients_all]

    injections = []
    selected_patient = None
    start_date = None
    end_date = None


    if form.validate_on_submit():
        patient_id = form.patient_id.data
        start_date = form.start_date.data
        end_date = form.end_date.data

        query = Injection.query

        if patient_id:
            query = query.filter(Injection.patient_id == patient_id)
            selected_patient = Patient.query.get(patient_id)

        if start_date:
             query = query.filter(func.date(Injection.date) >= start_date)
        if end_date:
             query = query.filter(func.date(Injection.date) <= end_date)


        injections = query.order_by(Injection.date.asc()).all()


        return render_template('report_injections_by_patient_date.html',
                               title='Report: Injektionen nach Patient und Datum',
                               form=form,
                               injections=injections,
                               selected_patient=selected_patient,
                               start_date=start_date,
                               end_date=end_date)


    # Beim GET oder Validierungsfehler, Formular ohne Ergebnisse anzeigen
    return render_template('report_injections_by_patient_date.html', title='Report: Injektionen nach Patient und Datum', form=form, injections=[], selected_patient=None, start_date=None, end_date=None)

# Report: Vitalwerte nach Patient und Datum (verwendet ReportPatientDateRangeForm) (unverändert)
@bp.route("/reports/vital_signs_by_patient_date", methods=['GET', 'POST'])
def report_vital_signs_by_patient_date():
    form = ReportPatientDateRangeForm()

    patients_all = Patient.query.order_by(Patient.nachname).all()
    form.patient_id.choices = [('', 'Alle Patienten')] + [(str(p.id), f"{p.nachname}, {p.vorname}") for p in patients_all]

    vital_signs = []
    selected_patient = None
    start_date = None
    end_date = None


    if form.validate_on_submit():
        patient_id = form.patient_id.data
        start_date = form.start_date.data
        end_date = form.end_date.data

        query = VitalSign.query

        if patient_id:
            query = query.filter(VitalSign.patient_id == patient_id)
            selected_patient = Patient.query.get(patient_id)

        if start_date:
             query = query.filter(func.date(VitalSign.timestamp) >= start_date)
        if end_date:
             query = query.filter(func.date(VitalSign.timestamp) <= end_date)


        vital_signs = query.order_by(VitalSign.timestamp.asc()).all()


        return render_template('report_vital_signs_by_patient_date.html',
                               title='Report: Vitalwerte nach Patient und Datum',
                               form=form,
                               vital_signs=vital_signs,
                               selected_patient=selected_patient,
                               start_date=start_date,
                               end_date=end_date)


    # Beim GET oder Validierungsfehler, Formular ohne Ergebnisse anzeigen
    return render_template('report_vital_signs_by_patient_date.html', title='Report: Vitalwerte nach Patient und Datum', form=form, vital_signs=[], selected_patient=None, start_date=None, end_date=None)


# Route zur Auswahl eines Patienten vor dem Anlegen einer Impfung - Endpunkt 'bp.add_vaccination_select_patient' (unverändert)
@bp.route("/add_vaccination_select_patient", methods=['GET', 'POST'])
def add_vaccination_select_patient():
    form = PatientSelectForm()
    patients = Patient.query.order_by(Patient.nachname).all()
    form.patient_id.choices = [('', '--- Patient auswählen ---')] + [(str(p.id), f"{p.nachname}, {p.vorname}") for p in patients]

    if form.validate_on_submit():
        selected_patient_id = form.patient_id.data
        return redirect(url_for('bp.add_vaccination', patient_id=selected_patient_id))

    # Rendere das Patientenauswahl-Formular, übergebe die Action-URL explizit
    return render_template('select_patient_vaccination.html',
                           title='Patient für neue Impfung auswählen',
                           form=form,
                           form_action=url_for('bp.add_vaccination_select_patient'))


# Route zur Auswahl eines Patienten vor dem Anlegen einer Injektion - Endpunkt 'bp.add_injection_select_patient' (unverändert)
@bp.route("/add_injection_select_patient", methods=['GET', 'POST'])
def add_injection_select_patient():
    form = PatientSelectForm()
    patients = Patient.query.order_by(Patient.nachname).all()
    form.patient_id.choices = [('', '--- Patient auswählen ---')] + [(str(p.id), f"{p.nachname}, {p.vorname}") for p in patients]

    if form.validate_on_submit():
        selected_patient_id = form.patient_id.data
        return redirect(url_for('bp.add_injection', patient_id=selected_patient_id))

    # Rendere das Patientenauswahl-Formular, übergebe die Action-URL explizit
    return render_template('select_patient_injection.html',
                           title='Patient für neue Injektion auswählen',
                           form=form,
                           form_action=url_for('bp.add_injection_select_patient'))

# NEU: Route zur Auswahl eines Patienten vor dem Anlegen von Vitalwerten - Endpunkt 'bp.add_vital_sign_select_patient' (unverändert)
@bp.route("/add_vital_sign_select_patient", methods=['GET', 'POST'])
def add_vital_sign_select_patient():
    form = PatientSelectForm()
    patients = Patient.query.order_by(Patient.nachname).all()
    form.patient_id.choices = [('', '--- Patient auswählen ---')] + [(str(p.id), f"{p.nachname}, {p.vorname}") for p in patients]

    if form.validate_on_submit():
        selected_patient_id = form.patient_id.data
        return redirect(url_for('bp.add_vital_sign', patient_id=selected_patient_id))

    # Rendere das Patientenauswahl-Formular, übergebe die Action-URL explizit
    return render_template('select_patient_vital_sign.html',
                           title='Patient für neue Vitalwerte auswählen',
                           form=form,
                           form_action=url_for('bp.add_vital_sign_select_patient'))

