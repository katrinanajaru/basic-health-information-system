import streamlit as st
import database as db
from patient import Patient
from department import Department
from doctor import Doctor
from prescription import Prescription
from medical_test import Medical_Test
import config
import sqlite3 as sql

# Apply custom blue-themed background
st.markdown(
    """
    <style>
    body, .stApp {
        background: linear-gradient(to bottom right, #1E90FF, #87CEFA);
        color: #ffffff;
    }
    .stTextInput > label, .stTextArea > label, .stSelectbox > label {
        color: white !important;
    }
    .css-18e3th9 {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
    }
    .stButton button {
        background-color: #4682B4;
        color: white;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Edit mode password verification
def verify_edit_mode_password():
    edit_mode_password = st.sidebar.text_input('Edit mode password', type='password')
    if edit_mode_password == config.edit_mode_password:
        st.sidebar.success('Verified')
        return True
    elif edit_mode_password == '':
        st.empty()
    else:
        st.sidebar.error('Invalid edit mode password')
        return False

# Doctor/Medical lab access verification
def verify_dr_mls_access_code():
    dr_mls_access_code = st.sidebar.text_input('Doctor/Lab access code', type='password')
    if dr_mls_access_code == config.dr_mls_access_code:
        st.sidebar.success('Verified')
        return True
    elif dr_mls_access_code == '':
        st.empty()
    else:
        st.sidebar.error('Invalid access code')
        return False

# Patient module
def patients():
    st.header('👨‍⚕️ PATIENTS')
    options = ['', 'Add patient', 'Update patient', 'Delete patient', 'Show complete patient record', 'Search patient']
    selection = st.sidebar.selectbox('Choose an action', options)
    p = Patient()

    if selection in options[1:4] and verify_edit_mode_password():
        if selection == 'Add patient':
            st.subheader('➕ Add Patient')
            p.add_patient()
        elif selection == 'Update patient':
            st.subheader('✏️ Update Patient')
            p.update_patient()
        elif selection == 'Delete patient':
            st.subheader('🗑️ Delete Patient')
            patient_id = st.text_input("Enter Patient ID to delete")
            if st.button("Delete"):
                conn, c = db.connection()
                try:
                    c.execute("DELETE FROM patient_record WHERE id = :id", {'id': patient_id})
                    conn.commit()
                    st.success("Patient deleted successfully")
                except sql.IntegrityError:
                    st.error('Cannot delete: Entry linked to other records.')
                conn.close()

    elif selection == 'Show complete patient record':
        st.subheader('📋 All Patient Records')
        conn, c = db.connection()
        c.execute("SELECT * FROM patient_record")
        patients = c.fetchall()
        conn.close()
        from patient import show_patient_details
        show_patient_details(patients)

    elif selection == 'Search patient':
        st.subheader('🔍 Search Patient')
        search_term = st.text_input("Search term")
        if search_term:
            conn, c = db.connection()
            c.execute("SELECT * FROM patient_record")
            patients = c.fetchall()
            conn.close()
            filtered = [p for p in patients if search_term.lower() in str(p).lower()]
            from patient import show_patient_details
            show_patient_details(filtered)
        else:
            st.info("Enter search term.")

# Doctor module
def doctors():
    st.header('👨‍⚕️ DOCTORS')
    options = ['', 'Add doctor', 'Update doctor', 'Delete doctor', 'Show complete doctor record', 'Search doctor']
    selection = st.sidebar.selectbox('Choose an action', options)
    d = Doctor()

    if selection in options[1:4] and verify_edit_mode_password():
        if selection == 'Add doctor':
            st.subheader('➕ Add Doctor')
            d.add_doctor()
        elif selection == 'Update doctor':
            st.subheader('✏️ Update Doctor')
            d.update_doctor()
        elif selection == 'Delete doctor':
            st.subheader('🗑️ Delete Doctor')
            try:
                d.delete_doctor()
            except sql.IntegrityError:
                st.error('Cannot delete: Entry linked to other records.')

    elif selection == 'Show complete doctor record':
        st.subheader('📋 All Doctor Records')
        d.show_all_doctors()

    elif selection == 'Search doctor':
        st.subheader('🔍 Search Doctor')
        d.search_doctor()

# Prescription module
def prescriptions():
    st.header('💊 PRESCRIPTIONS')
    options = ['', 'Add prescription', 'Update prescription', 'Delete prescription', 'Show prescriptions of a particular patient']
    selection = st.sidebar.selectbox('Choose an action', options)
    p = Prescription()

    if selection in options[1:4] and verify_dr_mls_access_code():
        if selection == 'Add prescription':
            st.subheader('➕ Add Prescription')
            p.add_prescription()
        elif selection == 'Update prescription':
            st.subheader('✏️ Update Prescription')
            p.update_prescription()
        elif selection == 'Delete prescription':
            st.subheader('🗑️ Delete Prescription')
            p.delete_prescription()
    elif selection == 'Show prescriptions of a particular patient':
        st.subheader('📄 Patient Prescriptions')
        p.prescriptions_by_patient()

# Medical test module
def medical_tests():
    st.header('🧪 MEDICAL TESTS')
    options = ['', 'Add medical test', 'Update medical test', 'Delete medical test', 'Show medical tests of a particular patient']
    selection = st.sidebar.selectbox('Choose an action', options)
    m = Medical_Test()

    if selection in options[1:4] and verify_dr_mls_access_code():
        if selection == 'Add medical test':
            st.subheader('➕ Add Medical Test')
            m.add_medical_test()
        elif selection == 'Update medical test':
            st.subheader('✏️ Update Medical Test')
            m.update_medical_test()
        elif selection == 'Delete medical test':
            st.subheader('🗑️ Delete Medical Test')
            m.delete_medical_test()
    elif selection == 'Show medical tests of a particular patient':
        st.subheader('📊 Patient Medical Tests')
        m.medical_tests_by_patient()

# Department module
def departments():
    st.header('🏥 DEPARTMENTS')
    options = ['', 'Add department', 'Update department', 'Delete department', 'Show complete department record', 'Search department', 'Show doctors of a particular department']
    selection = st.sidebar.selectbox('Choose an action', options)
    d = Department()

    if selection in options[1:4] and verify_edit_mode_password():
        if selection == 'Add department':
            st.subheader('➕ Add Department')
            d.add_department()
        elif selection == 'Update department':
            st.subheader('✏️ Update Department')
            d.update_department()
        elif selection == 'Delete department':
            st.subheader('🗑️ Delete Department')
            try:
                d.delete_department()
            except sql.IntegrityError:
                st.error('Cannot delete: Entry linked to other records.')

    elif selection == 'Show complete department record':
        st.subheader('📋 All Departments')
        d.show_all_departments()

    elif selection == 'Search department':
        st.subheader('🔍 Search Department')
        d.search_department()

    elif selection == 'Show doctors of a particular department':
        st.subheader('🧑‍⚕️ Doctors by Department')
        d.list_dept_doctors()

# Health programs module
def health_programs():
    st.header('🌿 HEALTH PROGRAMS')
    if st.sidebar.selectbox('Choose action', ['', 'Add health program']) == 'Add health program' and verify_edit_mode_password():
        st.subheader('➕ Add Health Program')
        name = st.text_input('Program Name')
        description = st.text_area('Program Description')
        if st.button('Save'):
            conn, c = db.connection()
            try:
                c.execute(
                    "INSERT INTO health_programs (name, description) VALUES (?, ?)",
                    (name, description)
                )
                conn.commit()
                st.success('Program added.')
            except sql.IntegrityError:
                st.error('Program already exists.')
            conn.close()

# Home navigation
def home():
    db.db_init()
    module = st.sidebar.selectbox('Select module', ['', 'Patients', 'Doctors', 'Prescriptions', 'Medical Tests', 'Departments', 'Health Programs'])
    if module == 'Patients':
        patients()
    elif module == 'Doctors':
        doctors()
    elif module == 'Prescriptions':
        prescriptions()
    elif module == 'Medical Tests':
        medical_tests()
    elif module == 'Departments':
        departments()
    elif module == 'Health Programs':
        health_programs()

# Entry point
st.title('🏥 HEALTHCARE INFORMATION MANAGEMENT SYSTEM')
password = st.sidebar.text_input('Enter system password', type='password')

if password == config.password:
    st.sidebar.success('Access granted')
    home()
elif password == '':
    st.empty()
else:
    st.sidebar.error('Access denied: Invalid password')
