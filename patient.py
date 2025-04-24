import streamlit as st
from datetime import datetime, date
import database as db
import pandas as pd
import sqlite3 as sql


def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def generate_patient_id(reg_date, reg_time):
    time_part = ''.join(reg_time.split(':')[::-1])
    date_part = ''.join(reg_date.split('-')[::-1])[2:]
    return f'P-{time_part}-{date_part}'


def verify_patient_id(patient_id):
    conn, c = db.connection()
    c.execute("SELECT id FROM patient_record;")
    patient_ids = [row[0] for row in c.fetchall()]
    conn.close()
    return patient_id in patient_ids


def show_patient_details(patients):
    titles = ['Patient ID', 'Name', 'Age', 'Gender', 'Date of birth (DD-MM-YYYY)',
              'Blood group', 'Contact number', 'Alternate contact number',
              'Aadhar ID / Voter ID', 'Weight (kg)', 'Height (cm)', 'Address',
              'City', 'State', 'PIN code', "Next of kin's name",
              "Next of kin's relation to patient", "Next of kin's contact number",
              'Email ID', 'Date of registration (DD-MM-YYYY)', 'Time of registration (hh:mm:ss)',
              'Enrolled Programs']

    if not patients:
        st.warning('No patient data found.')
        return

    conn, c = db.connection()

    data = []
    for patient in patients:
        patient_id = patient[0]
        c.execute("""
            SELECT hp.name FROM health_programs hp
            INNER JOIN patient_programs pp ON hp.id = pp.program_id
            WHERE pp.patient_id = ?;
        """, (patient_id,))
        programs = [row[0] for row in c.fetchall()]
        programs_display = ', '.join(programs) if programs else 'None'
        full_data = list(patient) + [programs_display]
        data.append(full_data)

    conn.close()

    df = pd.DataFrame(data, columns=titles)
    st.dataframe(df)


class Patient:
    def __init__(self):
        self.reset()

    def reset(self):
        self.name = self.gender = self.contact_number_1 = self.contact_number_2 = ""
        self.date_of_birth = self.blood_group = self.aadhar_or_voter_id = ""
        self.address = self.city = self.state = self.pin_code = ""
        self.next_of_kin_name = self.next_of_kin_relation_to_patient = self.next_of_kin_contact_number = ""
        self.email_id = ""
        self.age = self.height = self.weight = 0
        self.date_of_registration = self.time_of_registration = ""
        self.id = ""
        self.selected_program_ids = []

    def add_patient(self):
        st.header("Add New Patient")

        self.name = st.text_input("Full Name")
        gender = st.radio("Gender", ["Female", "Male", "Other"])
        if gender == "Other":
            gender = st.text_input("Please specify gender")
        self.gender = gender

        dob = st.date_input("Date of Birth (YYYY-MM-DD)")
        self.date_of_birth = dob.strftime('%d-%m-%Y')
        self.age = calculate_age(dob)

        self.blood_group = st.text_input("Blood Group")
        self.contact_number_1 = st.text_input("Primary Contact Number")
        self.contact_number_2 = st.text_input("Alternate Contact Number (Optional)")

        self.aadhar_or_voter_id = st.text_input("Aadhar/Voter ID")
        self.weight = st.number_input("Weight (kg)", min_value=0, max_value=400)
        self.height = st.number_input("Height (cm)", min_value=0, max_value=275)

        self.address = st.text_area("Address")
        self.city = st.text_input("City")
        self.state = st.text_input("State")
        self.pin_code = st.text_input("PIN Code")

        self.next_of_kin_name = st.text_input("Next of Kin Name")
        self.next_of_kin_relation_to_patient = st.text_input("Relationship with Patient")
        self.next_of_kin_contact_number = st.text_input("Next of Kin Contact Number")
        self.email_id = st.text_input("Email (Optional)")

        self.date_of_registration = datetime.now().strftime('%d-%m-%Y')
        self.time_of_registration = datetime.now().strftime('%H:%M:%S')
        self.id = generate_patient_id(self.date_of_registration, self.time_of_registration)

        # Fetch programs
        conn, c = db.connection()
        c.execute("SELECT id, name FROM health_programs;")
        programs = c.fetchall()
        conn.close()

        if programs:
            selected_programs = st.multiselect("Select health programs", [p[1] for p in programs], key="add_patient_programs")
            self.selected_program_ids = [p[0] for p in programs if p[1] in selected_programs]
        else:
            st.warning("No health programs found.")

        if st.button("Save Patient"):
            conn, c = db.connection()
            c.execute("SELECT id FROM patient_record WHERE aadhar_or_voter_id = :uid", {'uid': self.aadhar_or_voter_id})
            if c.fetchone():
                st.error("A patient with this ID already exists.")
                conn.close()
                return

            try:
                # Insert patient
                c.execute("""
                    INSERT INTO patient_record (
                        id, name, age, gender, date_of_birth, blood_group,
                        contact_number_1, contact_number_2, aadhar_or_voter_id,
                        weight, height, address, city, state, pin_code,
                        next_of_kin_name, next_of_kin_relation_to_patient,
                        next_of_kin_contact_number, email_id,
                        date_of_registration, time_of_registration
                    )
                    VALUES (
                        :id, :name, :age, :gender, :dob, :blood_group,
                        :phone1, :phone2, :uid, :weight, :height,
                        :address, :city, :state, :pin,
                        :kin_name, :kin_relation, :kin_contact,
                        :email, :reg_date, :reg_time
                    );
                """, {
                    'id': self.id, 'name': self.name, 'age': self.age,
                    'gender': self.gender, 'dob': self.date_of_birth,
                    'blood_group': self.blood_group, 'phone1': self.contact_number_1,
                    'phone2': self.contact_number_2, 'uid': self.aadhar_or_voter_id,
                    'weight': self.weight, 'height': self.height,
                    'address': self.address, 'city': self.city, 'state': self.state,
                    'pin': self.pin_code, 'kin_name': self.next_of_kin_name,
                    'kin_relation': self.next_of_kin_relation_to_patient,
                    'kin_contact': self.next_of_kin_contact_number,
                    'email': self.email_id, 'reg_date': self.date_of_registration,
                    'reg_time': self.time_of_registration
                })

                # Insert selected programs
                for pid in self.selected_program_ids:
                    c.execute("""
                        INSERT INTO patient_programs (patient_id, program_id)
                        VALUES (:pid, :prid);
                    """, {'pid': self.id, 'prid': pid})

                conn.commit()
                st.success(f"Patient added successfully! ID: {self.id}")
            except sql.IntegrityError as e:
                st.error(f"Integrity Error: {e}")
            conn.close()
