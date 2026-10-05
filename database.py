import os
import sqlite3

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "clinic.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _ensure_table(conn, sql):
    conn.execute(sql)


def migrate_missing_columns(conn, table_name, expected_columns):
    existing = {row[1] for row in conn.execute(f'PRAGMA table_info({table_name})').fetchall()}
    for column_name, column_sql in expected_columns.items():
        if column_name not in existing:
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}")


def ensure_database():
    conn = get_connection()
    try:
        # settings
        _ensure_table(
            conn,
            """
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                clinic_name TEXT NOT NULL DEFAULT 'Cabinet Dentaire',
                address TEXT,
                phone TEXT,
                email TEXT,
                doctor_name TEXT,
                logo_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
        )
        conn.execute(
            "INSERT OR IGNORE INTO settings (id, clinic_name, address, phone, email, doctor_name, logo_path) VALUES (1, 'Cabinet Dentaire', '', '', '', '', '')"
        )

        _ensure_table(
            conn,
            """
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                birth_date TEXT,
                sex TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                blood_group TEXT,
                allergies TEXT,
                medical_history TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
        )
        migrate_missing_columns(
            conn,
            "patients",
            {
                "first_name": "TEXT",
                "last_name": "TEXT",
                "birth_date": "TEXT",
                "sex": "TEXT",
                "phone": "TEXT",
                "email": "TEXT",
                "address": "TEXT",
                "blood_group": "TEXT",
                "allergies": "TEXT",
                "medical_history": "TEXT",
                "notes": "TEXT",
                "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
            },
        )

        _ensure_table(
            conn,
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                reason TEXT,
                notes TEXT,
                status TEXT NOT NULL DEFAULT 'Planifié',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
            )
            """,
        )
        migrate_missing_columns(
            conn,
            "appointments",
            {
                "patient_id": "INTEGER NOT NULL DEFAULT 0",
                "appointment_date": "TEXT",
                "appointment_time": "TEXT",
                "reason": "TEXT",
                "notes": "TEXT",
                "status": "TEXT DEFAULT 'Planifié'",
                "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
            },
        )

        _ensure_table(
            conn,
            """
            CREATE TABLE IF NOT EXISTS consultations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                consultation_date TEXT NOT NULL,
                reason TEXT,
                diagnosis TEXT,
                observations TEXT,
                recommended_treatment TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
            )
            """,
        )
        migrate_missing_columns(
            conn,
            "consultations",
            {
                "patient_id": "INTEGER NOT NULL DEFAULT 0",
                "consultation_date": "TEXT",
                "reason": "TEXT",
                "diagnosis": "TEXT",
                "observations": "TEXT",
                "recommended_treatment": "TEXT",
                "notes": "TEXT",
                "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
            },
        )

        _ensure_table(
            conn,
            """
            CREATE TABLE IF NOT EXISTS treatments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                treatment_type TEXT NOT NULL,
                tooth_number INTEGER,
                diagnosis TEXT,
                description TEXT,
                treatment_date TEXT,
                price REAL DEFAULT 0,
                notes TEXT,
                status TEXT NOT NULL DEFAULT 'Prévu',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
            )
            """,
        )
        migrate_missing_columns(
            conn,
            "treatments",
            {
                "patient_id": "INTEGER NOT NULL DEFAULT 0",
                "treatment_type": "TEXT",
                "tooth_number": "INTEGER",
                "diagnosis": "TEXT",
                "description": "TEXT",
                "treatment_date": "TEXT",
                "price": "REAL DEFAULT 0",
                "notes": "TEXT",
                "status": "TEXT DEFAULT 'Prévu'",
                "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
            },
        )

        _ensure_table(
            conn,
            """
            CREATE TABLE IF NOT EXISTS teeth (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                tooth_number INTEGER NOT NULL,
                state TEXT,
                diagnosis TEXT,
                treatment TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
            )
            """,
        )
        migrate_missing_columns(
            conn,
            "teeth",
            {
                "patient_id": "INTEGER NOT NULL DEFAULT 0",
                "tooth_number": "INTEGER",
                "state": "TEXT",
                "diagnosis": "TEXT",
                "treatment": "TEXT",
                "notes": "TEXT",
                "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
            },
        )

        _ensure_table(
            conn,
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                payment_date TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                reason TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
            )
            """,
        )
        migrate_missing_columns(
            conn,
            "payments",
            {
                "patient_id": "INTEGER NOT NULL DEFAULT 0",
                "payment_date": "TEXT",
                "amount": "REAL",
                "payment_method": "TEXT",
                "reason": "TEXT",
                "notes": "TEXT",
                "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
            },
        )

        _ensure_table(
            conn,
            """
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT NOT NULL UNIQUE,
                patient_id INTEGER NOT NULL,
                invoice_date TEXT NOT NULL,
                treatment_id INTEGER,
                quantity INTEGER DEFAULT 1,
                unit_price REAL NOT NULL,
                total REAL NOT NULL,
                amount_paid REAL DEFAULT 0,
                remaining REAL DEFAULT 0,
                status TEXT DEFAULT 'Ouverte',
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
                FOREIGN KEY (treatment_id) REFERENCES treatments(id) ON DELETE SET NULL
            )
            """,
        )
        migrate_missing_columns(
            conn,
            "invoices",
            {
                "invoice_number": "TEXT UNIQUE",
                "patient_id": "INTEGER NOT NULL DEFAULT 0",
                "invoice_date": "TEXT",
                "treatment_id": "INTEGER",
                "quantity": "INTEGER DEFAULT 1",
                "unit_price": "REAL",
                "total": "REAL",
                "amount_paid": "REAL DEFAULT 0",
                "remaining": "REAL DEFAULT 0",
                "status": "TEXT DEFAULT 'Ouverte'",
                "notes": "TEXT",
                "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
            },
        )

        _ensure_table(
            conn,
            """
            CREATE TABLE IF NOT EXISTS invoice_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                unit_price REAL NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
            )
            """,
        )

        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    ensure_database()
    print(f"Base de données initialisée : {DB_PATH}")
