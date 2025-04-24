from fastapi import FastAPI, HTTPException
from typing import List, Dict
import database as db

app = FastAPI()

@app.get("/patients/{patient_id}")
async def get_patient_profile(patient_id: str):
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT *
            FROM patient_record
            WHERE id = :patient_id;
            """,
            {'patient_id': patient_id}
        )
        patient = c.fetchone()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        c.execute(
            """
            SELECT hp.name
            FROM health_programs hp
            INNER JOIN patient_programs pp ON hp.id = pp.program_id
            WHERE pp.patient_id = :patient_id;
            """,
            {'patient_id': patient_id}
        )
        enrolled_programs = [program[0] for program in c.fetchall()]
    conn.close()

    patient_data = {
        "id": patient[0],
        "name": patient[1],
        "age": patient[2],
        "gender": patient[3],
        "date_of_birth": patient[4],
        "blood_group": patient[5],
        "contact_number_1": patient[6],
        "contact_number_2": patient[7],
        "aadhar_or_voter_id": patient[8],
        "weight": patient[9],
        "height": patient[10],
        "address": patient[11],
        "city": patient[12],
        "state": patient[13],
        "pin_code": patient[14],
        "next_of_kin_name": patient[15],
        "next_of_kin_relation_to_patient": patient[16],
        "next_of_kin_contact_number": patient[17],
        "email_id": patient[18],
        "date_of_registration": patient[19],
        "time_of_registration": patient[20],
        "enrolled_programs": enrolled_programs
    }
    return patient_data
