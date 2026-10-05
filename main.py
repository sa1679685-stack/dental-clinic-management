import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from database import DB_PATH, get_connection


class ClinicModels:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _today(self):
        return datetime.now().strftime("%Y-%m-%d")

    def _week_start(self):
        today = datetime.now()
        return (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")

    def _month_start(self):
        return datetime.now().strftime("%Y-%m-01")

    def _year_start(self):
        return datetime.now().strftime("%Y-01-01")

    # SETTINGS
    def get_settings(self) -> Dict[str, Any]:
        conn = self._connect()
        try:
            row = conn.execute("SELECT * FROM settings WHERE id = 1").fetchone()
            return dict(row) if row else {
                "clinic_name": "Cabinet Dentaire",
                "address": "",
                "phone": "",
                "email": "",
                "doctor_name": "",
                "logo_path": "",
            }
        finally:
            conn.close()

    def save_settings(self, data: Dict[str, Any]) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                UPDATE settings
                SET clinic_name = ?, address = ?, phone = ?, email = ?, doctor_name = ?, logo_path = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
                """,
                [data.get("clinic_name", ""), data.get("address", ""), data.get("phone", ""), data.get("email", ""), data.get("doctor_name", ""), data.get("logo_path", "")],
            )
            if conn.total_changes == 0:
                conn.execute(
                    "INSERT INTO settings (id, clinic_name, address, phone, email, doctor_name, logo_path) VALUES (1, ?, ?, ?, ?, ?, ?)",
                    [data.get("clinic_name", ""), data.get("address", ""), data.get("phone", ""), data.get("email", ""), data.get("doctor_name", ""), data.get("logo_path", "")],
                )
            conn.commit()
        finally:
            conn.close()

    # PATIENTS
    def create_patient(self, data: Dict[str, Any]) -> int:
        conn = self._connect()
        try:
            cur = conn.execute(
                """
                INSERT INTO patients (
                    first_name, last_name, birth_date, sex, phone, email, address,
                    blood_group, allergies, medical_history, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                [
                    data.get("first_name", "").strip(),
                    data.get("last_name", "").strip(),
                    data.get("birth_date", ""),
                    data.get("sex", ""),
                    data.get("phone", ""),
                    data.get("email", ""),
                    data.get("address", ""),
                    data.get("blood_group", ""),
                    data.get("allergies", ""),
                    data.get("medical_history", ""),
                    data.get("notes", ""),
                ],
            )
            conn.commit()
            return int(cur.lastrowid)
        finally:
            conn.close()

    def get_patient(self, patient_id: int) -> Optional[Dict[str, Any]]:
        conn = self._connect()
        try:
            row = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def list_patients(self, search: str = "") -> List[Dict[str, Any]]:
        conn = self._connect()
        try:
            if search:
                term = f"%{search.lower()}%"
                rows = conn.execute(
                    """
                    SELECT * FROM patients
                    WHERE lower(first_name) LIKE ? OR lower(last_name) LIKE ? OR lower(phone) LIKE ?
                    ORDER BY last_name, first_name
                    """,
                    (term, term, term),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM patients ORDER BY last_name, first_name").fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def update_patient(self, patient_id: int, data: Dict[str, Any]) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                UPDATE patients
                SET first_name = ?, last_name = ?, birth_date = ?, sex = ?, phone = ?, email = ?, address = ?,
                    blood_group = ?, allergies = ?, medical_history = ?, notes = ?
                WHERE id = ?
                """,
                [
                    data.get("first_name", "").strip(),
                    data.get("last_name", "").strip(),
                    data.get("birth_date", ""),
                    data.get("sex", ""),
                    data.get("phone", ""),
                    data.get("email", ""),
                    data.get("address", ""),
                    data.get("blood_group", ""),
                    data.get("allergies", ""),
                    data.get("medical_history", ""),
                    data.get("notes", ""),
                    patient_id,
                ],
            )
            conn.commit()
        finally:
            conn.close()

    def delete_patient(self, patient_id: int) -> None:
        conn = self._connect()
        try:
            conn.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
            conn.commit()
        finally:
            conn.close()

    def patient_history(self, patient_id: int) -> Dict[str, List[Dict[str, Any]]]:
        conn = self._connect()
        try:
            consultations = conn.execute(
                "SELECT * FROM consultations WHERE patient_id = ? ORDER BY consultation_date DESC, id DESC",
                (patient_id,),
            ).fetchall()
            treatments = conn.execute(
                "SELECT * FROM treatments WHERE patient_id = ? ORDER BY treatment_date DESC, id DESC",
                (patient_id,),
            ).fetchall()
            appointments = conn.execute(
                "SELECT * FROM appointments WHERE patient_id = ? ORDER BY appointment_date DESC, appointment_time DESC, id DESC",
                (patient_id,),
            ).fetchall()
            payments = conn.execute(
                "SELECT * FROM payments WHERE patient_id = ? ORDER BY payment_date DESC, id DESC",
                (patient_id,),
            ).fetchall()
            return {
                "consultations": [dict(r) for r in consultations],
                "treatments": [dict(r) for r in treatments],
                "appointments": [dict(r) for r in appointments],
                "payments": [dict(r) for r in payments],
            }
        finally:
            conn.close()

    # APPOINTMENTS
    def create_appointment(self, data: Dict[str, Any]) -> int:
        conn = self._connect()
        try:
            cur = conn.execute(
                """
                INSERT INTO appointments (patient_id, appointment_date, appointment_time, reason, notes, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    data.get("patient_id"),
                    data.get("appointment_date", ""),
                    data.get("appointment_time", ""),
                    data.get("reason", ""),
                    data.get("notes", ""),
                    data.get("status", "Planifié"),
                ],
            )
            conn.commit()
            return int(cur.lastrowid)
        finally:
            conn.close()

    def list_appointments(self, search: str = "", status: str = "") -> List[Dict[str, Any]]:
        conn = self._connect()
        try:
            query = """
                SELECT a.*, p.first_name, p.last_name
                FROM appointments a
                JOIN patients p ON p.id = a.patient_id
            """
            params: List[Any] = []
            clauses = []
            if search:
                clauses.append("(lower(p.first_name) LIKE ? OR lower(p.last_name) LIKE ? OR lower(a.reason) LIKE ?)")
                term = f"%{search.lower()}%"
                params.extend([term, term, term])
            if status:
                clauses.append("a.status = ?")
                params.append(status)
            if clauses:
                query += " WHERE " + " AND ".join(clauses)
            query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC"
            rows = conn.execute(query, params).fetchall()
            result = []
            for row in rows:
                item = dict(row)
                item["patient_name"] = f"{row['first_name']} {row['last_name']}"
                result.append(item)
            return result
        finally:
            conn.close()

    def get_appointment(self, appointment_id: int) -> Optional[Dict[str, Any]]:
        conn = self._connect()
        try:
            row = conn.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def update_appointment(self, appointment_id: int, data: Dict[str, Any]) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                UPDATE appointments
                SET patient_id = ?, appointment_date = ?, appointment_time = ?, reason = ?, notes = ?, status = ?
                WHERE id = ?
                """,
                [
                    data.get("patient_id"),
                    data.get("appointment_date", ""),
                    data.get("appointment_time", ""),
                    data.get("reason", ""),
                    data.get("notes", ""),
                    data.get("status", "Planifié"),
                    appointment_id,
                ],
            )
            conn.commit()
        finally:
            conn.close()

    def delete_appointment(self, appointment_id: int) -> None:
        conn = self._connect()
        try:
            conn.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
            conn.commit()
        finally:
            conn.close()

    # CONSULTATIONS
    def create_consultation(self, data: Dict[str, Any]) -> int:
        conn = self._connect()
        try:
            cur = conn.execute(
                """
                INSERT INTO consultations (patient_id, consultation_date, reason, diagnosis, observations, recommended_treatment, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    data.get("patient_id"),
                    data.get("consultation_date", ""),
                    data.get("reason", ""),
                    data.get("diagnosis", ""),
                    data.get("observations", ""),
                    data.get("recommended_treatment", ""),
                    data.get("notes", ""),
                ],
            )
            conn.commit()
            return int(cur.lastrowid)
        finally:
            conn.close()

    def list_consultations(self, search: str = "") -> List[Dict[str, Any]]:
        conn = self._connect()
        try:
            if search:
                term = f"%{search.lower()}%"
                rows = conn.execute(
                    """
                    SELECT c.*, p.first_name, p.last_name
                    FROM consultations c
                    JOIN patients p ON p.id = c.patient_id
                    WHERE lower(p.first_name) LIKE ? OR lower(p.last_name) LIKE ? OR lower(c.diagnosis) LIKE ? OR lower(c.reason) LIKE ?
                    ORDER BY c.consultation_date DESC, c.id DESC
                    """,
                    (term, term, term, term),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT c.*, p.first_name, p.last_name
                    FROM consultations c
                    JOIN patients p ON p.id = c.patient_id
                    ORDER BY c.consultation_date DESC, c.id DESC
                    """
                ).fetchall()
            result = []
            for row in rows:
                item = dict(row)
                item["patient_name"] = f"{row['first_name']} {row['last_name']}"
                result.append(item)
            return result
        finally:
            conn.close()

    def update_consultation(self, consultation_id: int, data: Dict[str, Any]) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                UPDATE consultations
                SET patient_id = ?, consultation_date = ?, reason = ?, diagnosis = ?, observations = ?, recommended_treatment = ?, notes = ?
                WHERE id = ?
                """,
                [
                    data.get("patient_id"),
                    data.get("consultation_date", ""),
                    data.get("reason", ""),
                    data.get("diagnosis", ""),
                    data.get("observations", ""),
                    data.get("recommended_treatment", ""),
                    data.get("notes", ""),
                    consultation_id,
                ],
            )
            conn.commit()
        finally:
            conn.close()

    def delete_consultation(self, consultation_id: int) -> None:
        conn = self._connect()
        try:
            conn.execute("DELETE FROM consultations WHERE id = ?", (consultation_id,))
            conn.commit()
        finally:
            conn.close()

    # TREATMENTS
    def create_treatment(self, data: Dict[str, Any]) -> int:
        conn = self._connect()
        try:
            cur = conn.execute(
                """
                INSERT INTO treatments (patient_id, treatment_type, tooth_number, diagnosis, description, treatment_date, price, notes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    data.get("patient_id"),
                    data.get("treatment_type", ""),
                    data.get("tooth_number"),
                    data.get("diagnosis", ""),
                    data.get("description", ""),
                    data.get("treatment_date", ""),
                    float(data.get("price") or 0),
                    data.get("notes", ""),
                    data.get("status", "Prévu"),
                ],
            )
            conn.commit()
            return int(cur.lastrowid)
        finally:
            conn.close()

    def list_treatments(self, search: str = "") -> List[Dict[str, Any]]:
        conn = self._connect()
        try:
            if search:
                term = f"%{search.lower()}%"
                rows = conn.execute(
                    """
                    SELECT t.*, p.first_name, p.last_name
                    FROM treatments t
                    JOIN patients p ON p.id = t.patient_id
                    WHERE lower(p.first_name) LIKE ? OR lower(p.last_name) LIKE ? OR lower(t.treatment_type) LIKE ? OR lower(t.diagnosis) LIKE ?
                    ORDER BY t.treatment_date DESC, t.id DESC
                    """,
                    (term, term, term, term),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT t.*, p.first_name, p.last_name
                    FROM treatments t
                    JOIN patients p ON p.id = t.patient_id
                    ORDER BY t.treatment_date DESC, t.id DESC
                    """
                ).fetchall()
            result = []
            for row in rows:
                item = dict(row)
                item["patient_name"] = f"{row['first_name']} {row['last_name']}"
                result.append(item)
            return result
        finally:
            conn.close()

    def update_treatment(self, treatment_id: int, data: Dict[str, Any]) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                UPDATE treatments
                SET patient_id = ?, treatment_type = ?, tooth_number = ?, diagnosis = ?, description = ?, treatment_date = ?, price = ?, notes = ?, status = ?
                WHERE id = ?
                """,
                [
                    data.get("patient_id"),
                    data.get("treatment_type", ""),
                    data.get("tooth_number"),
                    data.get("diagnosis", ""),
                    data.get("description", ""),
                    data.get("treatment_date", ""),
                    float(data.get("price") or 0),
                    data.get("notes", ""),
                    data.get("status", "Prévu"),
                    treatment_id,
                ],
            )
            conn.commit()
        finally:
            conn.close()

    def delete_treatment(self, treatment_id: int) -> None:
        conn = self._connect()
        try:
            conn.execute("DELETE FROM treatments WHERE id = ?", (treatment_id,))
            conn.commit()
        finally:
            conn.close()

    # TEETH
    def create_tooth_record(self, data: Dict[str, Any]) -> int:
        conn = self._connect()
        try:
            cur = conn.execute(
                """
                INSERT INTO teeth (patient_id, tooth_number, state, diagnosis, treatment, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    data.get("patient_id"),
                    data.get("tooth_number"),
                    data.get("state", ""),
                    data.get("diagnosis", ""),
                    data.get("treatment", ""),
                    data.get("notes", ""),
                ],
            )
            conn.commit()
            return int(cur.lastrowid)
        finally:
            conn.close()

    def list_teeth(self, patient_id: int = 0) -> List[Dict[str, Any]]:
        conn = self._connect()
        try:
            if patient_id:
                rows = conn.execute(
                    "SELECT t.*, p.first_name, p.last_name FROM teeth t JOIN patients p ON p.id = t.patient_id WHERE t.patient_id = ? ORDER BY t.tooth_number",
                    (patient_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT t.*, p.first_name, p.last_name FROM teeth t JOIN patients p ON p.id = t.patient_id ORDER BY t.tooth_number"
                ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def update_tooth_record(self, tooth_id: int, data: Dict[str, Any]) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                UPDATE teeth
                SET patient_id = ?, tooth_number = ?, state = ?, diagnosis = ?, treatment = ?, notes = ?
                WHERE id = ?
                """,
                [
                    data.get("patient_id"),
                    data.get("tooth_number"),
                    data.get("state", ""),
                    data.get("diagnosis", ""),
                    data.get("treatment", ""),
                    data.get("notes", ""),
                    tooth_id,
                ],
            )
            conn.commit()
        finally:
            conn.close()

    def delete_tooth_record(self, tooth_id: int) -> None:
        conn = self._connect()
        try:
            conn.execute("DELETE FROM teeth WHERE id = ?", (tooth_id,))
            conn.commit()
        finally:
            conn.close()

    # PAYMENTS
    def create_payment(self, data: Dict[str, Any]) -> int:
        conn = self._connect()
        try:
            cur = conn.execute(
                """
                INSERT INTO payments (patient_id, payment_date, amount, payment_method, reason, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    data.get("patient_id"),
                    data.get("payment_date", ""),
                    float(data.get("amount") or 0),
                    data.get("payment_method", "Espèces"),
                    data.get("reason", ""),
                    data.get("notes", ""),
                ],
            )
            conn.commit()
            return int(cur.lastrowid)
        finally:
            conn.close()

    def list_payments(self, search: str = "") -> List[Dict[str, Any]]:
        conn = self._connect()
        try:
            if search:
                term = f"%{search.lower()}%"
                rows = conn.execute(
                    """
                    SELECT p.*, pa.first_name, pa.last_name
                    FROM payments p
                    JOIN patients pa ON pa.id = p.patient_id
                    WHERE lower(pa.first_name) LIKE ? OR lower(pa.last_name) LIKE ? OR lower(p.reason) LIKE ?
                    ORDER BY p.payment_date DESC, p.id DESC
                    """,
                    (term, term, term),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT p.*, pa.first_name, pa.last_name
                    FROM payments p
                    JOIN patients pa ON pa.id = p.patient_id
                    ORDER BY p.payment_date DESC, p.id DESC
                    """
                ).fetchall()
            result = []
            for row in rows:
                item = dict(row)
                item["patient_name"] = f"{row['first_name']} {row['last_name']}"
                result.append(item)
            return result
        finally:
            conn.close()

    def update_payment(self, payment_id: int, data: Dict[str, Any]) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                UPDATE payments
                SET patient_id = ?, payment_date = ?, amount = ?, payment_method = ?, reason = ?, notes = ?
                WHERE id = ?
                """,
                [
                    data.get("patient_id"),
                    data.get("payment_date", ""),
                    float(data.get("amount") or 0),
                    data.get("payment_method", "Espèces"),
                    data.get("reason", ""),
                    data.get("notes", ""),
                    payment_id,
                ],
            )
            conn.commit()
        finally:
            conn.close()

    def delete_payment(self, payment_id: int) -> None:
        conn = self._connect()
        try:
            conn.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
            conn.commit()
        finally:
            conn.close()

    # INVOICES
    def create_invoice(self, data: Dict[str, Any]) -> int:
        conn = self._connect()
        try:
            total = float(data.get("total") or 0)
            amount_paid = float(data.get("amount_paid") or 0)
            remaining = max(total - amount_paid, 0)
            cur = conn.execute(
                """
                INSERT INTO invoices (invoice_number, patient_id, invoice_date, treatment_id, quantity, unit_price, total, amount_paid, remaining, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    data.get("invoice_number", "INV-0000"),
                    data.get("patient_id"),
                    data.get("invoice_date", ""),
                    data.get("treatment_id"),
                    int(data.get("quantity") or 1),
                    float(data.get("unit_price") or 0),
                    total,
                    amount_paid,
                    remaining,
                    data.get("status", "Ouverte"),
                    data.get("notes", ""),
                ],
            )
            invoice_id = int(cur.lastrowid)
            conn.execute(
                "INSERT INTO invoice_details (invoice_id, description, quantity, unit_price, total) VALUES (?, ?, ?, ?, ?)",
                [invoice_id, data.get("treatment_name", "Traitement"), int(data.get("quantity") or 1), float(data.get("unit_price") or 0), total],
            )
            conn.commit()
            return invoice_id
        finally:
            conn.close()

    def list_invoices(self, search: str = "") -> List[Dict[str, Any]]:
        conn = self._connect()
        try:
            if search:
                term = f"%{search.lower()}%"
                rows = conn.execute(
                    """
                    SELECT i.*, p.first_name, p.last_name, t.treatment_type
                    FROM invoices i
                    JOIN patients p ON p.id = i.patient_id
                    LEFT JOIN treatments t ON t.id = i.treatment_id
                    WHERE lower(p.first_name) LIKE ? OR lower(p.last_name) LIKE ? OR lower(i.invoice_number) LIKE ?
                    ORDER BY i.invoice_date DESC, i.id DESC
                    """,
                    (term, term, term),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT i.*, p.first_name, p.last_name, t.treatment_type
                    FROM invoices i
                    JOIN patients p ON p.id = i.patient_id
                    LEFT JOIN treatments t ON t.id = i.treatment_id
                    ORDER BY i.invoice_date DESC, i.id DESC
                    """
                ).fetchall()
            result = []
            for row in rows:
                item = dict(row)
                item["patient_name"] = f"{row['first_name']} {row['last_name']}"
                result.append(item)
            return result
        finally:
            conn.close()

    def update_invoice(self, invoice_id: int, data: Dict[str, Any]) -> None:
        conn = self._connect()
        try:
            total = float(data.get("total") or 0)
            amount_paid = float(data.get("amount_paid") or 0)
            remaining = max(total - amount_paid, 0)
            conn.execute(
                """
                UPDATE invoices
                SET invoice_number = ?, patient_id = ?, invoice_date = ?, treatment_id = ?, quantity = ?, unit_price = ?, total = ?, amount_paid = ?, remaining = ?, status = ?, notes = ?
                WHERE id = ?
                """,
                [
                    data.get("invoice_number", "INV-0000"),
                    data.get("patient_id"),
                    data.get("invoice_date", ""),
                    data.get("treatment_id"),
                    int(data.get("quantity") or 1),
                    float(data.get("unit_price") or 0),
                    total,
                    amount_paid,
                    remaining,
                    data.get("status", "Ouverte"),
                    data.get("notes", ""),
                    invoice_id,
                ],
            )
            conn.execute(
                "UPDATE invoice_details SET description = ?, quantity = ?, unit_price = ?, total = ? WHERE invoice_id = ?",
                [data.get("treatment_name", "Traitement"), int(data.get("quantity") or 1), float(data.get("unit_price") or 0), total, invoice_id],
            )
            conn.commit()
        finally:
            conn.close()

    def delete_invoice(self, invoice_id: int) -> None:
        conn = self._connect()
        try:
            conn.execute("DELETE FROM invoice_details WHERE invoice_id = ?", (invoice_id,))
            conn.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
            conn.commit()
        finally:
            conn.close()

    def get_invoice(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT i.*, p.first_name, p.last_name, p.phone, p.address, t.treatment_type FROM invoices i JOIN patients p ON p.id = i.patient_id LEFT JOIN treatments t ON t.id = i.treatment_id WHERE i.id = ?",
                (invoice_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    # DASHBOARD / REPORTS
    def dashboard_stats(self) -> Dict[str, Any]:
        conn = self._connect()
        try:
            patient_count = conn.execute("SELECT COUNT(*) AS count FROM patients").fetchone()["count"]
            appointments_today = conn.execute("SELECT COUNT(*) AS count FROM appointments WHERE appointment_date = ?", (self._today(),)).fetchone()["count"]
            consultations_today = conn.execute("SELECT COUNT(*) AS count FROM consultations WHERE consultation_date = ?", (self._today(),)).fetchone()["count"]
            payments_today = conn.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE payment_date = ?", (self._today(),)).fetchone()["total"]
            payments_month = conn.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE payment_date >= ? AND payment_date <= ?", (self._month_start(), self._today())).fetchone()["total"]
            unpaid_invoices = conn.execute("SELECT COALESCE(SUM(remaining), 0) AS total FROM invoices WHERE remaining > 0").fetchone()["total"]
            total_patients = patient_count
            total_treatments = conn.execute("SELECT COALESCE(SUM(price), 0) AS total FROM treatments").fetchone()["total"]
            return {
                "patients": total_patients,
                "appointments_today": appointments_today,
                "consultations_today": consultations_today,
                "payments_today": payments_today,
                "payments_month": payments_month,
                "unpaid_invoices": unpaid_invoices,
                "total_treatments": total_treatments,
            }
        finally:
            conn.close()

    def reports(self, start_date: str, end_date: str) -> Dict[str, Any]:
        conn = self._connect()
        try:
            patient_count = conn.execute("SELECT COUNT(*) AS count FROM patients").fetchone()["count"]
            consultation_count = conn.execute(
                "SELECT COUNT(*) AS count FROM consultations WHERE consultation_date BETWEEN ? AND ?",
                (start_date, end_date),
            ).fetchone()["count"]
            appointment_count = conn.execute(
                "SELECT COUNT(*) AS count FROM appointments WHERE appointment_date BETWEEN ? AND ?",
                (start_date, end_date),
            ).fetchone()["count"]
            revenue = conn.execute(
                "SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE payment_date BETWEEN ? AND ?",
                (start_date, end_date),
            ).fetchone()["total"]
            due = conn.execute(
                "SELECT COALESCE(SUM(remaining), 0) AS total FROM invoices WHERE invoice_date BETWEEN ? AND ?",
                (start_date, end_date),
            ).fetchone()["total"]
            return {
                "patients": patient_count,
                "consultations": consultation_count,
                "appointments": appointment_count,
                "revenue": revenue,
                "payments": revenue,
                "due": due,
            }
        finally:
            conn.close()

    # UTILS
    def get_patient_combo(self) -> List[Dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute("SELECT id, first_name, last_name FROM patients ORDER BY last_name, first_name").fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_treatment_combo(self) -> List[Dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute("SELECT id, treatment_type, diagnosis, price FROM treatments ORDER BY treatment_date DESC").fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def generate_invoice_number(self) -> str:
        conn = self._connect()
        try:
            row = conn.execute("SELECT COALESCE(MAX(CAST(substr(invoice_number, 4) AS INTEGER)), 0) + 1 AS next_num FROM invoices").fetchone()
            return f"INV-{int(row['next_num']):04d}"
        finally:
            conn.close()

    def get_total_for_patient(self, patient_id: int) -> float:
        conn = self._connect()
        try:
            total_treatments = conn.execute("SELECT COALESCE(SUM(price), 0) AS total FROM treatments WHERE patient_id = ?", (patient_id,)).fetchone()["total"]
            total_paid = conn.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE patient_id = ?", (patient_id,)).fetchone()["total"]
            total_invoices = conn.execute("SELECT COALESCE(SUM(total), 0) AS total FROM invoices WHERE patient_id = ?", (patient_id,)).fetchone()["total"]
            return float(total_treatments + total_invoices - total_paid)
        finally:
            conn.close()


models = ClinicModels()
