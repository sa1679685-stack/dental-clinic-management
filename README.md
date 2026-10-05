import os
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from database import ensure_database
from models import models


class DentalClinicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cabinet Dentaire - Gestion Clinique")
        self.root.geometry("1600x900")
        self.root.minsize(1200, 700)
        self.root.configure(bg="#f3f6fb")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Sidebar.TFrame", background="#153b5c")
        self.style.configure("Sidebar.TButton", background="#204d79", foreground="white", font=("Segoe UI", 10, "bold"))
        self.style.map("Sidebar.TButton", background=[("active", "#1f5a8b")])
        self.style.configure("Card.TFrame", background="#ffffff")
        self.style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground="#1b2d3f")
        self.style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground="#1b2d3f")
        self.style.configure("Body.TLabel", font=("Segoe UI", 10), foreground="#374151")

        self.sidebar = ttk.Frame(self.root, style="Sidebar.TFrame", padding=(10, 15))
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        self.sidebar.configure(width=220)

        self.main = ttk.Frame(self.root, padding=(16, 16))
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(0, weight=1)

        self.pages = {}
        self.build_sidebar()
        self.build_pages()
        self.show_page("dashboard")

    def build_sidebar(self):
        title = ttk.Label(self.sidebar, text="Cabinet Dentaire", background="#153b5c", foreground="white", font=("Segoe UI", 18, "bold"), anchor="w")
        title.grid(row=0, column=0, sticky="ew", padx=8, pady=(0, 18))

        nav_items = [
            ("dashboard", "🏠 Dashboard"),
            ("patients", "👤 Patients"),
            ("appointments", "📅 Rendez-vous"),
            ("consultations", "🦷 Consultations"),
            ("treatments", "💊 Traitements"),
            ("teeth", "🦷 Dents"),
            ("payments", "💰 Paiements"),
            ("invoices", "🧾 Factures"),
            ("reports", "📊 Rapports"),
            ("settings", "⚙️ Paramètres"),
        ]

        for idx, (key, text) in enumerate(nav_items, start=1):
            btn = ttk.Button(self.sidebar, text=text, style="Sidebar.TButton", command=lambda k=key: self.show_page(k))
            btn.grid(row=idx, column=0, sticky="ew", padx=8, pady=4)
            btn.configure(width=18)

    def build_pages(self):
        self.pages["dashboard"] = self.build_dashboard_page()
        self.pages["patients"] = self.build_patients_page()
        self.pages["appointments"] = self.build_appointments_page()
        self.pages["consultations"] = self.build_consultations_page()
        self.pages["treatments"] = self.build_treatments_page()
        self.pages["teeth"] = self.build_teeth_page()
        self.pages["payments"] = self.build_payments_page()
        self.pages["invoices"] = self.build_invoices_page()
        self.pages["reports"] = self.build_reports_page()
        self.pages["settings"] = self.build_settings_page()

        for frame in self.pages.values():
            frame.grid(row=0, column=0, sticky="nsew")
            frame.grid_remove()

    def show_page(self, key):
        for page_key, frame in self.pages.items():
            if page_key == key:
                frame.grid()
                frame.tkraise()
            else:
                frame.grid_remove()

    def card(self, parent, title, value, accent="#5c8ef5"):
        frame = ttk.Frame(parent, padding=18)
        frame.grid_columnconfigure(0, weight=1)
        ttk.Label(frame, text=title, foreground="#64748b", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text=value, foreground=accent, font=("Segoe UI", 22, "bold")).grid(row=1, column=0, sticky="w", pady=(8, 0))
        return frame

    def build_dashboard_page(self):
        page = ttk.Frame(self.main)
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        title = ttk.Label(page, text="Dashboard", style="Title.TLabel")
        title.grid(row=0, column=0, sticky="w", pady=(0, 12))

        cards = ttk.Frame(page)
        cards.grid(row=1, column=0, sticky="nsew")
        cards.grid_columnconfigure(0, weight=1)
        cards.grid_columnconfigure(1, weight=1)
        cards.grid_columnconfigure(2, weight=1)
        cards.grid_columnconfigure(3, weight=1)
        cards.grid_columnconfigure(4, weight=1)
        cards.grid_columnconfigure(5, weight=1)

        stats = models.dashboard_stats()
        values = [
            ("Nombre de patients", stats.get("patients", 0), "#3b82f6"),
            ("Rendez-vous aujourd'hui", stats.get("appointments_today", 0), "#10b981"),
            ("Consultations aujourd'hui", stats.get("consultations_today", 0), "#8b5cf6"),
            ("Paiements du jour", f"{stats.get('payments_today', 0):.2f} €", "#f59e0b"),
            ("Paiements du mois", f"{stats.get('payments_month', 0):.2f} €", "#14b8a6"),
            ("Factures impayées", f"{stats.get('unpaid_invoices', 0):.2f} €", "#ef4444"),
        ]

        for idx, (label, value, color) in enumerate(values):
            card = ttk.Frame(cards, padding=18, relief="solid", borderwidth=1)
            card.grid(row=0, column=idx, sticky="nsew", padx=8, pady=6)
            card.grid_columnconfigure(0, weight=1)
            ttk.Label(card, text=label, foreground="#64748b", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
            ttk.Label(card, text=str(value), foreground=color, font=("Segoe UI", 22, "bold")).grid(row=1, column=0, sticky="w", pady=(8, 0))

        panels = ttk.Frame(page)
        panels.grid(row=2, column=0, sticky="nsew", pady=(14, 0))
        panels.grid_columnconfigure(0, weight=1)
        panels.grid_columnconfigure(1, weight=1)

        left = ttk.LabelFrame(panels, text="Activité récente")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(0, weight=1)

        recent = ttk.Treeview(left, columns=("type", "detail"), show="headings", height=10)
        recent.heading("type", text="Type")
        recent.heading("detail", text="Détail")
        recent.column("type", width=160)
        recent.column("detail", width=320)
        recent.grid(row=0, column=0, sticky="nsew", padx=8, pady=10)

        scroll = ttk.Scrollbar(left, orient="vertical", command=recent.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        recent.configure(yscrollcommand=scroll.set)

        recent.insert("", "end", values=("Patients", f"{stats.get('patients', 0)} patients enregistrés"))
        recent.insert("", "end", values=("Rendez-vous", f"{stats.get('appointments_today', 0)} aujourd'hui"))
        recent.insert("", "end", values=("Consultations", f"{stats.get('consultations_today', 0)} aujourd'hui"))
        recent.insert("", "end", values=("Paiements", f"{stats.get('payments_month', 0):.2f} € ce mois"))
        recent.insert("", "end", values=("Factures", f"{stats.get('unpaid_invoices', 0):.2f} € impayées"))

        right = ttk.LabelFrame(panels, text="Statistiques")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        stats_vals = [
            ("Chiffre d'affaires total", f"{models.dashboard_stats().get('total_treatments', 0):.2f} €"),
            ("Paiements du mois", f"{stats.get('payments_month', 0):.2f} €"),
            ("Factures impayées", f"{stats.get('unpaid_invoices', 0):.2f} €"),
            ("Consultations aujourd'hui", str(stats.get('consultations_today', 0))),
        ]
        for i, (label, value) in enumerate(stats_vals):
            ttk.Label(right, text=f"{label}: {value}", font=("Segoe UI", 11), foreground="#1f2937").grid(row=i, column=0, sticky="w", padx=12, pady=8)

        return page

    def build_patients_page(self):
        page = ttk.Frame(self.main)
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=2)
        page.grid_rowconfigure(0, weight=1)

        left = ttk.Frame(page)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.grid_columnconfigure(0, weight=1)

        search_frame = ttk.Frame(left)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(search_frame, text="Recherche patient", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.patient_search = ttk.Entry(search_frame)
        self.patient_search.grid(row=1, column=0, sticky="ew")
        ttk.Button(search_frame, text="Rechercher", command=self.refresh_patient_table).grid(row=1, column=1, padx=(8, 0))

        self.patient_tree = ttk.Treeview(left, columns=("id", "nom", "prenom", "tel"), show="headings", height=18)
        self.patient_tree.heading("id", text="ID")
        self.patient_tree.heading("nom", text="Nom")
        self.patient_tree.heading("prenom", text="Prénom")
        self.patient_tree.heading("tel", text="Téléphone")
        self.patient_tree.column("id", width=50)
        self.patient_tree.column("nom", width=140)
        self.patient_tree.column("prenom", width=120)
        self.patient_tree.column("tel", width=130)
        self.patient_tree.grid(row=1, column=0, sticky="nsew")
        self.patient_tree.bind("<<TreeviewSelect>>", self.on_patient_select)

        tree_scroll = ttk.Scrollbar(left, orient="vertical", command=self.patient_tree.yview)
        tree_scroll.grid(row=1, column=1, sticky="ns")
        self.patient_tree.configure(yscrollcommand=tree_scroll.set)

        actions = ttk.Frame(left)
        actions.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(actions, text="Ajouter", command=self.add_patient).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(actions, text="Modifier", command=self.update_patient).grid(row=0, column=1, padx=5)
        ttk.Button(actions, text="Supprimer", command=self.delete_patient).grid(row=0, column=2, padx=5)
        ttk.Button(actions, text="Historique", command=self.open_patient_history).grid(row=0, column=3, padx=5)

        right = ttk.LabelFrame(page, text="Fiche patient")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_columnconfigure(1, weight=1)

        form_fields = [
            ("first_name", "Prénom", 0, 0),
            ("last_name", "Nom", 0, 1),
            ("birth_date", "Date de naissance", 1, 0),
            ("sex", "Sexe", 1, 1),
            ("phone", "Téléphone", 2, 0),
            ("email", "Email", 2, 1),
            ("address", "Adresse", 3, 0, 2),
            ("blood_group", "Groupe sanguin", 4, 0),
            ("allergies", "Allergies", 5, 0, 2),
            ("medical_history", "Antécédents médicaux", 6, 0, 2),
            ("notes", "Notes", 7, 0, 2),
        ]
        self.patient_form = {}
        for item in form_fields:
            field_name = item[0]
            label_text = item[1]
            row = item[2]
            col = item[3]
            if len(item) == 5:
                colspan = item[4]
            else:
                colspan = 1
            ttk.Label(right, text=f"{label_text}:").grid(row=row, column=col, sticky="w", padx=10, pady=6)
            if field_name == "sex":
                combo = ttk.Combobox(right, values=["Masculin", "Féminin", "Autre"], state="readonly")
                combo.grid(row=row, column=col + 1 if colspan == 1 else col + 1, sticky="ew", padx=10, pady=6, columnspan=colspan)
                self.patient_form[field_name] = combo
            else:
                entry = ttk.Entry(right)
                entry.grid(row=row, column=col + 1 if colspan == 1 else col + 1, sticky="ew", padx=10, pady=6, columnspan=colspan)
                self.patient_form[field_name] = entry

        for i in range(8):
            right.grid_rowconfigure(i, weight=1)

        self.patient_current_id = tk.StringVar(value="")
        ttk.Label(right, text="ID patient:", font=("Segoe UI", 9, "bold")).grid(row=9, column=0, sticky="w", padx=10, pady=(12, 0))
        ttk.Label(right, textvariable=self.patient_current_id, foreground="#2563eb", font=("Segoe UI", 11, "bold")).grid(row=9, column=1, sticky="w", padx=10, pady=(12, 0))

        self.refresh_patient_table()
        return page

    def build_appointments_page(self):
        page = ttk.Frame(self.main)
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=1)
        page.grid_rowconfigure(0, weight=1)

        left = ttk.Frame(page)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.grid_columnconfigure(0, weight=1)

        search_frame = ttk.Frame(left)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(search_frame, text="Recherche rendez-vous").grid(row=0, column=0, sticky="w")
        self.appointment_search = ttk.Entry(search_frame)
        self.appointment_search.grid(row=1, column=0, sticky="ew")
        ttk.Button(search_frame, text="Rechercher", command=self.refresh_appointment_table).grid(row=1, column=1, padx=(8, 0))

        self.appointment_tree = ttk.Treeview(left, columns=("id", "patient", "date", "heure", "motif", "statut"), show="headings", height=18)
        self.appointment_tree.heading("id", text="ID")
        self.appointment_tree.heading("patient", text="Patient")
        self.appointment_tree.heading("date", text="Date")
        self.appointment_tree.heading("heure", text="Heure")
        self.appointment_tree.heading("motif", text="Motif")
        self.appointment_tree.heading("statut", text="Statut")
        self.appointment_tree.grid(row=1, column=0, sticky="nsew")
        self.appointment_tree.bind("<<TreeviewSelect>>", self.on_appointment_select)

        self.appointment_scroll = ttk.Scrollbar(left, orient="vertical", command=self.appointment_tree.yview)
        self.appointment_scroll.grid(row=1, column=1, sticky="ns")
        self.appointment_tree.configure(yscrollcommand=self.appointment_scroll.set)

        actions = ttk.Frame(left)
        actions.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(actions, text="Ajouter", command=self.add_appointment).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(actions, text="Modifier", command=self.update_appointment).grid(row=0, column=1, padx=5)
        ttk.Button(actions, text="Supprimer", command=self.delete_appointment).grid(row=0, column=2, padx=5)
        ttk.Button(actions, text="Changer statut", command=self.change_appointment_status).grid(row=0, column=3, padx=5)

        right = ttk.LabelFrame(page, text="Formulaire rendez-vous")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_columnconfigure(1, weight=1)

        self.appointment_patient_var = tk.StringVar()
        self.appointment_status_var = tk.StringVar(value="Planifié")

        self.appointment_fields = {}
        self.appointment_fields["patient_id"] = self.create_combo_with_label(right, "Patient", row=0, col=0, values=[])
        self.appointment_fields["appointment_date"] = self.create_entry_with_label(right, "Date", row=1, col=0)
        self.appointment_fields["appointment_time"] = self.create_entry_with_label(right, "Heure", row=2, col=0)
        self.appointment_fields["reason"] = self.create_entry_with_label(right, "Motif", row=3, col=0)
        self.appointment_fields["notes"] = self.create_entry_with_label(right, "Notes", row=4, col=0)
        self.appointment_fields["status"] = self.create_combo_with_label(right, "Statut", row=5, col=0, values=["Planifié", "Confirmé", "Terminé", "Annulé", "Absent"])

        self.appointment_current_id = tk.StringVar(value="")
        ttk.Label(right, text="ID rendez-vous:", font=("Segoe UI", 9, "bold")).grid(row=6, column=0, sticky="w", padx=10, pady=(12, 0))
        ttk.Label(right, textvariable=self.appointment_current_id, foreground="#2563eb", font=("Segoe UI", 11, "bold")).grid(row=6, column=1, sticky="w", padx=10, pady=(12, 0))

        self.refresh_appointment_table()
        return page

    def build_consultations_page(self):
        page = ttk.Frame(self.main)
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=1)
        page.grid_rowconfigure(0, weight=1)

        left = ttk.Frame(page)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.grid_columnconfigure(0, weight=1)
        ttk.Label(left, text="Recherche consultation").grid(row=0, column=0, sticky="w")
        self.consultation_search = ttk.Entry(left)
        self.consultation_search.grid(row=1, column=0, sticky="ew")
        ttk.Button(left, text="Rechercher", command=self.refresh_consultation_table).grid(row=1, column=1, padx=(8, 0))

        self.consultation_tree = ttk.Treeview(left, columns=("id", "patient", "date", "diagnostic", "motif"), show="headings", height=18)
        self.consultation_tree.heading("id", text="ID")
        self.consultation_tree.heading("patient", text="Patient")
        self.consultation_tree.heading("date", text="Date")
        self.consultation_tree.heading("diagnostic", text="Diagnostic")
        self.consultation_tree.heading("motif", text="Motif")
        self.consultation_tree.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        self.consultation_tree.bind("<<TreeviewSelect>>", self.on_consultation_select)

        cons_scroll = ttk.Scrollbar(left, orient="vertical", command=self.consultation_tree.yview)
        cons_scroll.grid(row=2, column=1, sticky="ns")
        self.consultation_tree.configure(yscrollcommand=cons_scroll.set)

        buttons = ttk.Frame(left)
        buttons.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(buttons, text="Ajouter", command=self.add_consultation).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(buttons, text="Modifier", command=self.update_consultation).grid(row=0, column=1, padx=5)
        ttk.Button(buttons, text="Supprimer", command=self.delete_consultation).grid(row=0, column=2, padx=5)

        right = ttk.LabelFrame(page, text="Formulaire consultation")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_columnconfigure(1, weight=1)

        self.consultation_fields = {}
        self.consultation_fields["patient_id"] = self.create_combo_with_label(right, "Patient", row=0, col=0, values=[])
        self.consultation_fields["consultation_date"] = self.create_entry_with_label(right, "Date", row=1, col=0)
        self.consultation_fields["reason"] = self.create_entry_with_label(right, "Motif", row=2, col=0)
        self.consultation_fields["diagnosis"] = self.create_entry_with_label(right, "Diagnostic", row=3, col=0)
        self.consultation_fields["observations"] = self.create_entry_with_label(right, "Observations", row=4, col=0)
        self.consultation_fields["recommended_treatment"] = self.create_entry_with_label(right, "Traitement recommandé", row=5, col=0)
        self.consultation_fields["notes"] = self.create_entry_with_label(right, "Notes", row=6, col=0)

        self.consultation_current_id = tk.StringVar(value="")
        ttk.Label(right, text="ID consultation:", font=("Segoe UI", 9, "bold")).grid(row=7, column=0, sticky="w", padx=10, pady=(12, 0))
        ttk.Label(right, textvariable=self.consultation_current_id, foreground="#2563eb", font=("Segoe UI", 11, "bold")).grid(row=7, column=1, sticky="w", padx=10, pady=(12, 0))

        self.refresh_consultation_table()
        return page

    def build_treatments_page(self):
        page = ttk.Frame(self.main)
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=1)
        page.grid_rowconfigure(0, weight=1)

        left = ttk.Frame(page)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.grid_columnconfigure(0, weight=1)
        ttk.Label(left, text="Recherche traitement").grid(row=0, column=0, sticky="w")
        self.treatment_search = ttk.Entry(left)
        self.treatment_search.grid(row=1, column=0, sticky="ew")
        ttk.Button(left, text="Rechercher", command=self.refresh_treatment_table).grid(row=1, column=1, padx=(8, 0))

        self.treatment_tree = ttk.Treeview(left, columns=("id", "patient", "type", "dent", "prix", "statut"), show="headings", height=18)
        self.treatment_tree.heading("id", text="ID")
        self.treatment_tree.heading("patient", text="Patient")
        self.treatment_tree.heading("type", text="Type")
        self.treatment_tree.heading("dent", text="Dent")
        self.treatment_tree.heading("prix", text="Prix")
        self.treatment_tree.heading("statut", text="Statut")
        self.treatment_tree.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        self.treatment_tree.bind("<<TreeviewSelect>>", self.on_treatment_select)

        t_scroll = ttk.Scrollbar(left, orient="vertical", command=self.treatment_tree.yview)
        t_scroll.grid(row=2, column=1, sticky="ns")
        self.treatment_tree.configure(yscrollcommand=t_scroll.set)

        buttons = ttk.Frame(left)
        buttons.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(buttons, text="Ajouter", command=self.add_treatment).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(buttons, text="Modifier", command=self.update_treatment).grid(row=0, column=1, padx=5)
        ttk.Button(buttons, text="Supprimer", command=self.delete_treatment).grid(row=0, column=2, padx=5)

        right = ttk.LabelFrame(page, text="Formulaire traitement")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_columnconfigure(1, weight=1)

        self.treatment_fields = {}
        self.treatment_fields["patient_id"] = self.create_combo_with_label(right, "Patient", row=0, col=0, values=[])
        self.treatment_fields["treatment_type"] = self.create_entry_with_label(right, "Type de traitement", row=1, col=0)
        self.treatment_fields["tooth_number"] = self.create_entry_with_label(right, "Dent concernée", row=2, col=0)
        self.treatment_fields["diagnosis"] = self.create_entry_with_label(right, "Diagnostic", row=3, col=0)
        self.treatment_fields["description"] = self.create_entry_with_label(right, "Description", row=4, col=0)
        self.treatment_fields["treatment_date"] = self.create_entry_with_label(right, "Date", row=5, col=0)
        self.treatment_fields["price"] = self.create_entry_with_label(right, "Prix", row=6, col=0)
        self.treatment_fields["notes"] = self.create_entry_with_label(right, "Notes", row=7, col=0)
        self.treatment_fields["status"] = self.create_combo_with_label(right, "Statut", row=8, col=0, values=["Prévu", "En cours", "Terminé"])

        self.treatment_current_id = tk.StringVar(value="")
        ttk.Label(right, text="ID traitement:", font=("Segoe UI", 9, "bold")).grid(row=9, column=0, sticky="w", padx=10, pady=(12, 0))
        ttk.Label(right, textvariable=self.treatment_current_id, foreground="#2563eb", font=("Segoe UI", 11, "bold")).grid(row=9, column=1, sticky="w", padx=10, pady=(12, 0))

        self.refresh_treatment_table()
        return page

    def build_teeth_page(self):
        page = ttk.Frame(self.main)
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=1)
        page.grid_rowconfigure(0, weight=1)

        left = ttk.Frame(page)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.grid_columnconfigure(0, weight=1)

        ttk.Label(left, text="Patient").grid(row=0, column=0, sticky="w")
        self.teeth_patient_combo = ttk.Combobox(left, state="readonly")
        self.teeth_patient_combo.grid(row=1, column=0, sticky="ew")
        ttk.Button(left, text="Afficher", command=self.refresh_teeth_table).grid(row=1, column=1, padx=(8, 0))

        self.teeth_tree = ttk.Treeview(left, columns=("id", "dent", "état", "diagnostic", "traitement"), show="headings", height=18)
        self.teeth_tree.heading("id", text="ID")
        self.teeth_tree.heading("dent", text="Dent")
        self.teeth_tree.heading("état", text="État")
        self.teeth_tree.heading("diagnostic", text="Diagnostic")
        self.teeth_tree.heading("traitement", text="Traitement")
        self.teeth_tree.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        self.teeth_tree.bind("<<TreeviewSelect>>", self.on_teeth_select)

        t_scroll = ttk.Scrollbar(left, orient="vertical", command=self.teeth_tree.yview)
        t_scroll.grid(row=2, column=1, sticky="ns")
        self.teeth_tree.configure(yscrollcommand=t_scroll.set)

        right = ttk.LabelFrame(page, text="Détail dent")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_columnconfigure(1, weight=1)

        self.teeth_fields = {}
        self.teeth_fields["patient_id"] = self.create_combo_with_label(right, "Patient", row=0, col=0, values=[])
        self.teeth_fields["tooth_number"] = self.create_entry_with_label(right, "Numéro de dent", row=1, col=0)
        self.teeth_fields["state"] = self.create_entry_with_label(right, "État", row=2, col=0)
        self.teeth_fields["diagnosis"] = self.create_entry_with_label(right, "Diagnostic", row=3, col=0)
        self.teeth_fields["treatment"] = self.create_entry_with_label(right, "Traitement", row=4, col=0)
        self.teeth_fields["notes"] = self.create_entry_with_label(right, "Notes", row=5, col=0)

        buttons = ttk.Frame(right)
        buttons.grid(row=6, column=0, sticky="ew", pady=(10, 0), columnspan=2)
        ttk.Button(buttons, text="Ajouter", command=self.add_tooth_record).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(buttons, text="Modifier", command=self.update_tooth_record).grid(row=0, column=1, padx=5)
        ttk.Button(buttons, text="Supprimer", command=self.delete_tooth_record).grid(row=0, column=2, padx=5)

        self.refresh_teeth_controls()
        self.refresh_teeth_table()
        return page

    def build_payments_page(self):
        page = ttk.Frame(self.main)
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=1)
        page.grid_rowconfigure(0, weight=1)

        left = ttk.Frame(page)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.grid_columnconfigure(0, weight=1)
        ttk.Label(left, text="Recherche paiement").grid(row=0, column=0, sticky="w")
        self.payment_search = ttk.Entry(left)
        self.payment_search.grid(row=1, column=0, sticky="ew")
        ttk.Button(left, text="Rechercher", command=self.refresh_payment_table).grid(row=1, column=1, padx=(8, 0))

        self.payment_tree = ttk.Treeview(left, columns=("id", "patient", "date", "montant", "mode", "motif"), show="headings", height=18)
        self.payment_tree.heading("id", text="ID")
        self.payment_tree.heading("patient", text="Patient")
        self.payment_tree.heading("date", text="Date")
        self.payment_tree.heading("montant", text="Montant")
        self.payment_tree.heading("mode", text="Mode")
        self.payment_tree.heading("motif", text="Motif")
        self.payment_tree.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        self.payment_tree.bind("<<TreeviewSelect>>", self.on_payment_select)

        p_scroll = ttk.Scrollbar(left, orient="vertical", command=self.payment_tree.yview)
        p_scroll.grid(row=2, column=1, sticky="ns")
        self.payment_tree.configure(yscrollcommand=p_scroll.set)

        buttons = ttk.Frame(left)
        buttons.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(buttons, text="Ajouter", command=self.add_payment).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(buttons, text="Modifier", command=self.update_payment).grid(row=0, column=1, padx=5)
        ttk.Button(buttons, text="Supprimer", command=self.delete_payment).grid(row=0, column=2, padx=5)
        ttk.Button(buttons, text="Reçu", command=self.preview_payment_receipt).grid(row=0, column=3, padx=5)

        right = ttk.LabelFrame(page, text="Formulaire paiement")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_columnconfigure(1, weight=1)

        self.payment_fields = {}
        self.payment_fields["patient_id"] = self.create_combo_with_label(right, "Patient", row=0, col=0, values=[])
        self.payment_fields["payment_date"] = self.create_entry_with_label(right, "Date", row=1, col=0)
        self.payment_fields["amount"] = self.create_entry_with_label(right, "Montant", row=2, col=0)
        self.payment_fields["payment_method"] = self.create_combo_with_label(right, "Mode de paiement", row=3, col=0, values=["Espèces", "Carte", "Autre"])
        self.payment_fields["reason"] = self.create_entry_with_label(right, "Motif", row=4, col=0)
        self.payment_fields["notes"] = self.create_entry_with_label(right, "Notes", row=5, col=0)

        self.payment_current_id = tk.StringVar(value="")
        ttk.Label(right, text="ID paiement:", font=("Segoe UI", 9, "bold")).grid(row=6, column=0, sticky="w", padx=10, pady=(12, 0))
        ttk.Label(right, textvariable=self.payment_current_id, foreground="#2563eb", font=("Segoe UI", 11, "bold")).grid(row=6, column=1, sticky="w", padx=10, pady=(12, 0))

        self.refresh_payment_table()
        return page

    def build_invoices_page(self):
        page = ttk.Frame(self.main)
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=1)
        page.grid_rowconfigure(0, weight=1)

        left = ttk.Frame(page)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.grid_columnconfigure(0, weight=1)
        ttk.Label(left, text="Recherche facture").grid(row=0, column=0, sticky="w")
        self.invoice_search = ttk.Entry(left)
        self.invoice_search.grid(row=1, column=0, sticky="ew")
        ttk.Button(left, text="Rechercher", command=self.refresh_invoice_table).grid(row=1, column=1, padx=(8, 0))

        self.invoice_tree = ttk.Treeview(left, columns=("id", "num", "patient", "date", "total", "payé", "reste"), show="headings", height=18)
        self.invoice_tree.heading("id", text="ID")
        self.invoice_tree.heading("num", text="N°")
        self.invoice_tree.heading("patient", text="Patient")
        self.invoice_tree.heading("date", text="Date")
        self.invoice_tree.heading("total", text="Total")
        self.invoice_tree.heading("payé", text="Payé")
        self.invoice_tree.heading("reste", text="Reste")
        self.invoice_tree.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        self.invoice_tree.bind("<<TreeviewSelect>>", self.on_invoice_select)

        inv_scroll = ttk.Scrollbar(left, orient="vertical", command=self.invoice_tree.yview)
        inv_scroll.grid(row=2, column=1, sticky="ns")
        self.invoice_tree.configure(yscrollcommand=inv_scroll.set)

        buttons = ttk.Frame(left)
        buttons.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(buttons, text="Créer", command=self.add_invoice).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(buttons, text="Modifier", command=self.update_invoice).grid(row=0, column=1, padx=5)
        ttk.Button(buttons, text="Supprimer", command=self.delete_invoice).grid(row=0, column=2, padx=5)
        ttk.Button(buttons, text="Imprimer", command=self.print_invoice).grid(row=0, column=3, padx=5)

        right = ttk.LabelFrame(page, text="Formulaire facture")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_columnconfigure(1, weight=1)

        self.invoice_fields = {}
        self.invoice_fields["invoice_number"] = self.create_entry_with_label(right, "Numéro facture", row=0, col=0)
        self.invoice_fields["patient_id"] = self.create_combo_with_label(right, "Patient", row=1, col=0, values=[])
        self.invoice_fields["invoice_date"] = self.create_entry_with_label(right, "Date", row=2, col=0)
        self.invoice_fields["treatment_id"] = self.create_combo_with_label(right, "Traitement", row=3, col=0, values=[])
        self.invoice_fields["quantity"] = self.create_entry_with_label(right, "Quantité", row=4, col=0)
        self.invoice_fields["unit_price"] = self.create_entry_with_label(right, "Prix unitaire", row=5, col=0)
        self.invoice_fields["total"] = self.create_entry_with_label(right, "Total", row=6, col=0)
        self.invoice_fields["amount_paid"] = self.create_entry_with_label(right, "Montant payé", row=7, col=0)
        self.invoice_fields["status"] = self.create_combo_with_label(right, "Statut", row=8, col=0, values=["Ouverte", "Partiellement payée", "Payée", "En retard"])
        self.invoice_fields["notes"] = self.create_entry_with_label(right, "Notes", row=9, col=0)

        self.invoice_current_id = tk.StringVar(value="")
        ttk.Label(right, text="ID facture:", font=("Segoe UI", 9, "bold")).grid(row=10, column=0, sticky="w", padx=10, pady=(12, 0))
        ttk.Label(right, textvariable=self.invoice_current_id, foreground="#2563eb", font=("Segoe UI", 11, "bold")).grid(row=10, column=1, sticky="w", padx=10, pady=(12, 0))

        self.refresh_invoice_table()
        return page

    def build_reports_page(self):
        page = ttk.Frame(self.main)
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(0, weight=1)

        header = ttk.Frame(page)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=1)
        ttk.Label(header, text="Rapports", style="Title.TLabel").grid(row=0, column=0, sticky="w")

        summary = ttk.LabelFrame(page, text="Périodes")
        summary.grid(row=1, column=0, sticky="ew")
        summary.grid_columnconfigure(0, weight=1)
        summary.grid_columnconfigure(1, weight=1)

        self.report_period = ttk.Combobox(summary, values=["Aujourd'hui", "Cette semaine", "Ce mois", "Cette année", "Période personnalisée"], state="readonly")
        self.report_period.set("Ce mois")
        self.report_period.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ttk.Button(summary, text="Afficher", command=self.refresh_reports).grid(row=0, column=1, padx=10, pady=10)

        metrics = ttk.Frame(page)
        metrics.grid(row=2, column=0, sticky="nsew", pady=(12, 0))
        metrics.grid_columnconfigure(0, weight=1)
        metrics.grid_columnconfigure(1, weight=1)
        metrics.grid_columnconfigure(2, weight=1)
        metrics.grid_columnconfigure(3, weight=1)

        self.report_values = {}
        for idx, (label, key) in enumerate([
            ("Nombre de patients", "patients"),
            ("Nombre de consultations", "consultations"),
            ("Nombre de rendez-vous", "appointments"),
            ("Chiffre d'affaires", "revenue"),
            ("Paiements", "payments"),
            ("Reste à payer", "due"),
        ]):
            card = ttk.Frame(metrics, padding=18, relief="solid", borderwidth=1)
            card.grid(row=0, column=idx % 3, sticky="nsew", padx=8, pady=8)
            ttk.Label(card, text=label, foreground="#64748b", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
            val = tk.StringVar(value="0")
            ttk.Label(card, textvariable=val, foreground="#1f2937", font=("Segoe UI", 20, "bold")).grid(row=1, column=0, sticky="w", pady=(8, 0))
            self.report_values[key] = val

        self.refresh_reports()
        return page

    def build_settings_page(self):
        page = ttk.Frame(self.main)
        page.grid_columnconfigure(0, weight=1)

        card = ttk.LabelFrame(page, text="Paramètres du cabinet")
        card.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

        fields = [
            ("clinic_name", "Nom du cabinet"),
            ("address", "Adresse"),
            ("phone", "Téléphone"),
            ("email", "Email"),
            ("doctor_name", "Nom du médecin"),
        ]
        self.settings_entries = {}
        for idx, (key, label) in enumerate(fields):
            ttk.Label(card, text=f"{label}:").grid(row=idx, column=0, sticky="w", padx=10, pady=8)
            entry = ttk.Entry(card)
            entry.grid(row=idx, column=1, sticky="ew", padx=10, pady=8)
            self.settings_entries[key] = entry

        ttk.Button(card, text="Enregistrer", command=self.save_settings).grid(row=len(fields), column=0, columnspan=2, sticky="ew", padx=10, pady=12)
        self.load_settings()
        return page

    def create_entry_with_label(self, parent, label_text, row, col):
        ttk.Label(parent, text=f"{label_text}:").grid(row=row, column=col, sticky="w", padx=10, pady=6)
        entry = ttk.Entry(parent)
        entry.grid(row=row, column=col + 1, sticky="ew", padx=10, pady=6)
        return entry

    def create_combo_with_label(self, parent, label_text, row, col, values):
        ttk.Label(parent, text=f"{label_text}:").grid(row=row, column=col, sticky="w", padx=10, pady=6)
        combo = ttk.Combobox(parent, state="readonly", values=values)
        combo.grid(row=row, column=col + 1, sticky="ew", padx=10, pady=6)
        return combo

    def fill_patient_combo(self, combo, selected_id=None):
        patients = models.get_patient_combo()
        combo["values"] = [f"{p['id']} - {p['first_name']} {p['last_name']}" for p in patients]
        if patients:
            if selected_id is not None:
                for idx, p in enumerate(patients):
                    if p["id"] == selected_id:
                        combo.current(idx)
                        break
            else:
                combo.current(0)

    def fill_treatment_combo(self, combo, selected_id=None):
        items = models.get_treatment_combo()
        combo["values"] = [f"{t['id']} - {t['treatment_type']} ({t['price']} €)" for t in items]
        if items:
            if selected_id is not None:
                for idx, t in enumerate(items):
                    if t["id"] == selected_id:
                        combo.current(idx)
                        break
            else:
                combo.current(0)

    def refresh_patient_table(self):
        search = self.patient_search.get()
        rows = models.list_patients(search)
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)
        for r in rows:
            self.patient_tree.insert("", "end", values=(r["id"], r["last_name"], r["first_name"], r["phone"]))

    def clear_patient_form(self):
        for key, widget in self.patient_form.items():
            if isinstance(widget, ttk.Combobox):
                widget.set("")
            else:
                widget.delete(0, tk.END)
        self.patient_current_id.set("")

    def on_patient_select(self, event):
        selected = self.patient_tree.selection()
        if not selected:
            return
        item = self.patient_tree.item(selected[0])
        patient_id = item["values"][0]
        patient = models.get_patient(patient_id)
        if not patient:
            return
        self.patient_current_id.set(str(patient_id))
        for key, widget in self.patient_form.items():
            val = patient.get(key, "")
            if isinstance(widget, ttk.Combobox):
                widget.set(val)
            else:
                widget.delete(0, tk.END)
                widget.insert(0, val)

    def add_patient(self):
        data = self._read_patient_form()
        if not data:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return
        try:
            models.create_patient(data)
            self.refresh_patient_table()
            self.clear_patient_form()
            messagebox.showinfo("Succès", "Patient ajouté avec succès.")
        except sqlite3.Error as exc:
            messagebox.showerror("Erreur SQLite", str(exc))

    def update_patient(self):
        patient_id = self.patient_current_id.get()
        if not patient_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un patient.")
            return
        data = self._read_patient_form()
        if not data:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return
        try:
            models.update_patient(int(patient_id), data)
            self.refresh_patient_table()
            messagebox.showinfo("Succès", "Patient modifié avec succès.")
        except sqlite3.Error as exc:
            messagebox.showerror("Erreur SQLite", str(exc))

    def delete_patient(self):
        patient_id = self.patient_current_id.get()
        if not patient_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un patient.")
            return
        if messagebox.askyesno("Confirmation", "Voulez-vous supprimer ce patient ?"):
            try:
                models.delete_patient(int(patient_id))
                self.refresh_patient_table()
                self.clear_patient_form()
                messagebox.showinfo("Succès", "Patient supprimé.")
            except sqlite3.Error as exc:
                messagebox.showerror("Erreur SQLite", str(exc))

    def _read_patient_form(self):
        required = ["first_name", "last_name", "phone"]
        data = {}
        for key in required:
            widget = self.patient_form.get(key)
            if widget is None:
                return {}
            value = widget.get().strip() if hasattr(widget, "get") else ""
            if not value:
                return {}
            data[key] = value
        for key, widget in self.patient_form.items():
            data[key] = widget.get().strip() if hasattr(widget, "get") else ""
        return data

    def open_patient_history(self):
        patient_id = self.patient_current_id.get()
        if not patient_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un patient.")
            return
        patient = models.get_patient(int(patient_id))
        if not patient:
            return
        history = models.patient_history(int(patient_id))
        top = tk.Toplevel(self.root)
        top.title(f"Historique - {patient['first_name']} {patient['last_name']}")
        top.geometry("1000x600")
        notebook = ttk.Notebook(top)
        notebook.pack(fill="both", expand=True)

        def build_history_tab(title, rows, columns):
            frame = ttk.Frame(notebook)
            tree = ttk.Treeview(frame, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col)
            for row in rows:
                values = [row.get(c, "") for c in columns]
                tree.insert("", "end", values=values)
            tree.pack(fill="both", expand=True)
            notebook.add(frame, text=title)

        build_history_tab("Consultations", history["consultations"], ["consultation_date", "reason", "diagnosis"])
        build_history_tab("Traitements", history["treatments"], ["treatment_date", "treatment_type", "price", "status"])
        build_history_tab("Rendez-vous", history["appointments"], ["appointment_date", "appointment_time", "reason", "status"])
        build_history_tab("Paiements", history["payments"], ["payment_date", "amount", "payment_method", "reason"])

    def refresh_appointment_table(self):
        rows = models.list_appointments(self.appointment_search.get(), "")
        for item in self.appointment_tree.get_children():
            self.appointment_tree.delete(item)
        for r in rows:
            self.appointment_tree.insert("", "end", values=(r["id"], r["patient_name"], r["appointment_date"], r["appointment_time"], r["reason"], r["status"]))

    def on_appointment_select(self, event):
        selected = self.appointment_tree.selection()
        if not selected:
            return
        row = self.appointment_tree.item(selected[0], "values")
        appointment_id = row[0]
        record = models.get_appointment(int(appointment_id))
        if not record:
            return
        self.appointment_current_id.set(str(record['id']))
        self.fill_patient_combo(self.appointment_fields['patient_id'], record['patient_id'])
        self.appointment_fields['appointment_date'].delete(0, tk.END)
        self.appointment_fields['appointment_date'].insert(0, record.get('appointment_date', ''))
        self.appointment_fields['appointment_time'].delete(0, tk.END)
        self.appointment_fields['appointment_time'].insert(0, record.get('appointment_time', ''))
        self.appointment_fields['reason'].delete(0, tk.END)
        self.appointment_fields['reason'].insert(0, record.get('reason', ''))
        self.appointment_fields['notes'].delete(0, tk.END)
        self.appointment_fields['notes'].insert(0, record.get('notes', ''))
        self.appointment_fields['status'].set(record.get('status', 'Planifié'))

    def read_appointment_form(self):
        patient_selection = self.appointment_fields['patient_id'].get()
        patient_id = None
        if patient_selection:
            patient_id = patient_selection.split(" - ")[0]
        if not patient_id or not self.appointment_fields['appointment_date'].get() or not self.appointment_fields['appointment_time'].get():
            return None
        return {
            "patient_id": int(patient_id),
            "appointment_date": self.appointment_fields['appointment_date'].get(),
            "appointment_time": self.appointment_fields['appointment_time'].get(),
            "reason": self.appointment_fields['reason'].get(),
            "notes": self.appointment_fields['notes'].get(),
            "status": self.appointment_fields['status'].get(),
        }

    def add_appointment(self):
        data = self.read_appointment_form()
        if not data:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return
        try:
            models.create_appointment(data)
            self.refresh_appointment_table()
            messagebox.showinfo("Succès", "Rendez-vous ajouté.")
        except sqlite3.Error as exc:
            messagebox.showerror("Erreur SQLite", str(exc))

    def update_appointment(self):
        appt_id = self.appointment_current_id.get()
        if not appt_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un rendez-vous.")
            return
        data = self.read_appointment_form()
        if not data:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return
        try:
            models.update_appointment(int(appt_id), data)
            self.refresh_appointment_table()
            messagebox.showinfo("Succès", "Rendez-vous modifié.")
        except sqlite3.Error as exc:
            messagebox.showerror("Erreur SQLite", str(exc))

    def delete_appointment(self):
        appt_id = self.appointment_current_id.get()
        if not appt_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un rendez-vous.")
            return
        if messagebox.askyesno("Confirmation", "Supprimer ce rendez-vous ?"):
            try:
                models.delete_appointment(int(appt_id))
                self.refresh_appointment_table()
                self.appointment_current_id.set("")
                messagebox.showinfo("Succès", "Rendez-vous supprimé.")
            except sqlite3.Error as exc:
                messagebox.showerror("Erreur SQLite", str(exc))

    def change_appointment_status(self):
        appt_id = self.appointment_current_id.get()
        if not appt_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un rendez-vous.")
            return
        status = self.appointment_fields['status'].get()
        if not status:
            return
        try:
            models.update_appointment(int(appt_id), {"patient_id": 1, "appointment_date": "", "appointment_time": "", "reason": "", "notes": "", "status": status})
        except sqlite3.Error as exc:
            messagebox.showerror("Erreur SQLite", str(exc))
        self.refresh_appointment_table()

    def refresh_consultation_table(self):
        rows = models.list_consultations(self.consultation_search.get())
        for item in self.consultation_tree.get_children():
            self.consultation_tree.delete(item)
        for r in rows:
            self.consultation_tree.insert("", "end", values=(r["id"], r["patient_name"], r["consultation_date"], r["diagnosis"], r["reason"]))

    def on_consultation_select(self, event):
        selected = self.consultation_tree.selection()
        if not selected:
            return
        row = self.consultation_tree.item(selected[0], "values")
        consultation_id = row[0]
        conn = sqlite3.connect(models.db_path)
        rec = conn.execute("SELECT * FROM consultations WHERE id = ?", (consultation_id,)).fetchone()
        conn.close()
        if not rec:
            return
        self.consultation_current_id.set(str(rec[0]))
        self.fill_patient_combo(self.consultation_fields['patient_id'], rec[1])
        self.consultation_fields['consultation_date'].delete(0, tk.END)
        self.consultation_fields['consultation_date'].insert(0, rec[2])
        self.consultation_fields['reason'].delete(0, tk.END)
        self.consultation_fields['reason'].insert(0, rec[3])
        self.consultation_fields['diagnosis'].delete(0, tk.END)
        self.consultation_fields['diagnosis'].insert(0, rec[4])
        self.consultation_fields['observations'].delete(0, tk.END)
        self.consultation_fields['observations'].insert(0, rec[5])
        self.consultation_fields['recommended_treatment'].delete(0, tk.END)
        self.consultation_fields['recommended_treatment'].insert(0, rec[6])
        self.consultation_fields['notes'].delete(0, tk.END)
        self.consultation_fields['notes'].insert(0, rec[7])

    def read_consultation_form(self):
        patient_selection = self.consultation_fields['patient_id'].get()
        patient_id = patient_selection.split(" - ")[0] if patient_selection else ""
        if not patient_id:
            return None
        return {
            "patient_id": int(patient_id),
            "consultation_date": self.consultation_fields['consultation_date'].get(),
            "reason": self.consultation_fields['reason'].get(),
            "diagnosis": self.consultation_fields['diagnosis'].get(),
            "observations": self.consultation_fields['observations'].get(),
            "recommended_treatment": self.consultation_fields['recommended_treatment'].get(),
            "notes": self.consultation_fields['notes'].get(),
        }

    def add_consultation(self):
        data = self.read_consultation_form()
        if not data:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return
        try:
            models.create_consultation(data)
            self.refresh_consultation_table()
            messagebox.showinfo("Succès", "Consultation ajoutée.")
        except sqlite3.Error as exc:
            messagebox.showerror("Erreur SQLite", str(exc))

    def update_consultation(self):
        cons_id = self.consultation_current_id.get()
        if not cons_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner une consultation.")
            return
        data = self.read_consultation_form()
        if not data:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return
        try:
            models.update_consultation(int(cons_id), data)
            self.refresh_consultation_table()
            messagebox.showinfo("Succès", "Consultation modifiée.")
        except sqlite3.Error as exc:
            messagebox.showerror("Erreur SQLite", str(exc))

    def delete_consultation(self):
        cons_id = self.consultation_current_id.get()
        if not cons_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner une consultation.")
            return
        if messagebox.askyesno("Confirmation", "Supprimer cette consultation ?"):
            try:
                models.delete_consultation(int(cons_id))
                self.refresh_consultation_table()
                self.consultation_current_id.set("")
                messagebox.showinfo("Succès", "Consultation supprimée.")
            except sqlite3.Error as exc:
                messagebox.showerror("Erreur SQLite", str(exc))

    def refresh_treatment_table(self):
        rows = models.list_treatments(self.treatment_search.get())
        for item in self.treatment_tree.get_children():
            self.treatment_tree.delete(item)
        for r in rows:
            self.treatment_tree.insert("", "end", values=(r["id"], r["patient_name"], r["treatment_type"], r["tooth_number"], r["price"], r["status"]))

    def on_treatment_select(self, event):
        selected = self.treatment_tree.selection()
        if not selected:
            return
        row = self.treatment_tree.item(selected[0], "values")
        treatment_id = row[0]
        conn = sqlite3.connect(models.db_path)
        rec = conn.execute("SELECT * FROM treatments WHERE id = ?", (treatment_id,)).fetchone()
        conn.close()
        if not rec:
            return
        self.treatment_current_id.set(str(rec[0]))
        self.fill_patient_combo(self.treatment_fields['patient_id'], rec[1])
        self.treatment_fields['treatment_type'].delete(0, tk.END)
        self.treatment_fields['treatment_type'].insert(0, rec[2])
        self.treatment_fields['tooth_number'].delete(0, tk.END)
        self.treatment_fields['tooth_number'].insert(0, str(rec[3]))
        self.treatment_fields['diagnosis'].delete(0, tk.END)
        self.treatment_fields['diagnosis'].insert(0, rec[4])
        self.treatment_fields['description'].delete(0, tk.END)
        self.treatment_fields['description'].insert(0, rec[5])
        self.treatment_fields['treatment_date'].delete(0, tk.END)
        self.treatment_fields['treatment_date'].insert(0, rec[6])
        self.treatment_fields['price'].delete(0, tk.END)
        self.treatment_fields['price'].insert(0, str(rec[7]))
        self.treatment_fields['notes'].delete(0, tk.END)
        self.treatment_fields['notes'].insert(0, rec[8])
        self.treatment_fields['status'].set(rec[9])

    def read_treatment_form(self):
        patient_selection = self.treatment_fields['patient_id'].get()
        patient_id = patient_selection.split(" - ")[0] if patient_selection else ""
        if not patient_id or not self.treatment_fields['treatment_type'].get():
            return None
        try:
            price = float(self.treatment_fields['price'].get().replace("€", "").strip() or 0)
        except ValueError:
            raise ValueError("Le prix doit être un montant valide.")
        return {
            "patient_id": int(patient_id),
            "treatment_type": self.treatment_fields['treatment_type'].get(),
            "tooth_number": int(self.treatment_fields['tooth_number'].get() or 0),
            "diagnosis": self.treatment_fields['diagnosis'].get(),
            "description": self.treatment_fields['description'].get(),
            "treatment_date": self.treatment_fields['treatment_date'].get(),
            "price": price,
            "notes": self.treatment_fields['notes'].get(),
            "status": self.treatment_fields['status'].get(),
        }

    def add_treatment(self):
        try:
            data = self.read_treatment_form()
        except ValueError as exc:
            messagebox.showerror("Erreur", str(exc))
            return
        if not data:
            messagebox.showerror("Erreur", "Veuillez remplir les champs obligatoires.")
            return
        try:
            models.create_treatment(data)
            self.refresh_treatment_table()
            messagebox.showinfo("Succès", "Traitement ajouté.")
        except sqlite3.Error as exc:
            messagebox.showerror("Erreur SQLite", str(exc))

    def update_treatment(self):
        treatment_id = self.treatment_current_id.get()
        if not treatment_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un traitement.")
            return
        try:
            data = self.read_treatment_form()
        except ValueError as exc:
            messagebox.showerror("Erreur", str(exc))
            return
        if not data:
            messagebox.showerror("Erreur", "Veuillez remplir les champs obligatoires.")
            return
        try:
            models.update_treatment(int(treatment_id), data)
            self.refresh_treatment_table()
            messagebox.showinfo("Succès", "Traitement modifié.")
        except sqlite3.Error as exc:
            messagebox.showerror("Erreur SQLite", str(exc))

    def delete_treatment(self):
        treatment_id = self.treatment_current_id.get()
        if not treatment_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un traitement.")
            return
        if messagebox.askyesno("Confirmation", "Supprimer ce traitement ?"):
            try:
                models.delete_treatment(int(treatment_id))
                self.refresh_treatment_table()
                self.treatment_current_id.set("")
                messagebox.showinfo("Succès", "Traitement supprimé.")
            except sqlite3.Error as exc:
                messagebox.showerror("Erreur SQLite", str(exc))

    def refresh_teeth_controls(self):
        patients = models.get_patient_combo()
        options = [f"{p['id']} - {p['first_name']} {p['last_name']}" for p in patients]
        self.teeth_patient_combo["values"] = options
        if options:
            self.teeth_patient_combo.current(0)
        for field in ["patient_id", "tooth_number", "state", "diagnosis", "treatment", "notes"]:
            if field in self.teeth_fields:
                widget = self.teeth_fields[field]
                if field == "patient_id":
                    self.fill_patient_combo(widget)
                else:
                    widget.delete(0, tk.END)

    def refresh_teeth_table(self):
        patient_selection = self.teeth_patient_combo.get()
        patient_id = int(patient_selection.split(" - ")[0]) if patient_selection else None
        rows = models.list_teeth(patient_id or 0)
        for item in self.teeth_tree.get_children():
            self.teeth_tree.delete(item)
        for r in rows:
            self.teeth_tree.insert("", "end", values=(r["id"], r["tooth_number"], r["state"], r["diagnosis"], r["treatment"]))

    def on_teeth_select(self, event):
        selected = self.teeth_tree.selection()
        if not selected:
            return
        row = self.teeth_tree.item(selected[0], "values")
        tooth_id = row[0]
        conn = sqlite3.connect(models.db_path)
        rec = conn.execute("SELECT * FROM teeth WHERE id = ?", (tooth_id,)).fetchone()
        conn.close()
        if not rec:
            return
        self.fill_patient_combo(self.teeth_fields['patient_id'], rec[1])
        self.teeth_fields['tooth_number'].delete(0, tk.END)
        self.teeth_fields['tooth_number'].insert(0, str(rec[2]))
        self.teeth_fields['state'].delete(0, tk.END)
        self.teeth_fields['state'].insert(0, rec[3])
        self.teeth_fields['diagnosis'].delete(0, tk.END)
        self.teeth_fields['diagnosis'].insert(0, rec[4])
        self.teeth_fields['treatment'].delete(0, tk.END)
        self.teeth_fields['treatment'].insert(0, rec[5])
        self.teeth_fields['notes'].delete(0, tk.END)
        self.teeth_fields['notes'].insert(0, rec[6])

    def read_tooth_record(self):
        patient_selection = self.teeth_fields['patient_id'].get()
        patient_id = patient_selection.split(" - ")[0] if patient_selection else ""
        if not patient_id or not self.teeth_fields['tooth_number'].get():
            return None
        return {
            "patient_id": int(patient_id),
            "tooth_number": int(self.teeth_fields['tooth_number'].get()),
            "state": self.teeth_fields['state'].get(),
            "diagnosis": self.teeth_fields['diagnosis'].get(),
            "treatment": self.teeth_fields['treatment'].get(),
            "notes": self.teeth_fields['notes'].get(),
        }

    def add_tooth_record(self):
        data = self.read_tooth_record()
        if not data:
            messagebox.showerror("Erreur", "Veuillez remplir les champs obligatoires.")
            return
        try:
            models.create_tooth_record(data)
            self.refresh_teeth_table()
            messagebox.showinfo("Succès", "Donnée dent ajoutée.")
        except sqlite3.Error as exc:
            messagebox.showerror("Erreur SQLite", str(exc))

    def update_tooth_record(self):
        selected = self.teeth_tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner une dent.")
            return
        tooth_id = self.teeth_tree.item(selected[0], "values")[0]
        data = self.read_tooth_record()
        if not data:
            messagebox.showerror("Erreur", "Veuillez remplir les champs obligatoires.")
            return
        try:
            models.update_tooth_record(int(tooth_id), data)
            self.refresh_teeth_table()
            messagebox.showinfo("Succès", "Donnée dent mise à jour.")
        except sqlite3.Error as exc:
            messagebox.showerror("Erreur SQLite", str(exc))

    def delete_tooth_record(self):
        selected = self.teeth_tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner une dent.")
            return
        tooth_id = self.teeth_tree.item(selected[0], "values")[0]
        if messagebox.askyesno("Confirmation", "Supprimer cette dent ?"):
            try:
                models.delete_tooth_record(int(tooth_id))
                self.refresh_teeth_table()
                messagebox.showinfo("Succès", "Donnée dent supprimée.")
            except sqlite3.Error as exc:
                messagebox.showerror("Erreur SQLite", str(exc))

    def refresh_payment_table(self):
        rows = models.list_payments(self.payment_search.get())
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)
        for r in rows:
            self.payment_tree.insert("", "end", values=(r["id"], r["patient_name"], r["payment_date"], r["amount"], r["payment_method"], r["reason"]))

    def on_payment_select(self, event):
        selected = self.payment_tree.selection()
        if not selected:
            return
        row = self.payment_tree.item(selected[0], "values")
        payment_id = row[0]
        conn = sqlite3.connect(models.db_path)
        rec = conn.execute("SELECT * FROM payments WHERE id = ?", (payment_id,)).fetchone()
        conn.close()
        if not rec:
            return
        self.payment_current_id.set(str(rec[0]))
        self.fill_patient_combo(self.payment_fields['patient_id'], rec[1])
        self.payment_fields['payment_date'].delete(0, tk.END)
        self.payment_fields['payment_date'].insert(0, rec[2])
        self.payment_fields['amount'].delete(0, tk.END)
        self.payment_fields['amount'].insert(0, str(rec[3]))
        self.payment_fields['payment_method'].set(rec[4])
        self.payment_fields['reason'].delete(0, tk.END)
        self.payment_fields['reason'].insert(0, rec[5])
        self.payment_fields['notes'].delete(0, tk.END)
        self.payment_fields['notes'].insert(0, rec[6])

    def read_payment_form(self):
        patient_selection = self.payment_fields['patient_id'].get()
        patient_id = patient_selection.split(" - ")[0] if patient_selection else ""
        if not patient_id or not self.payment_fields['payment_date'].get() or not self.payment_fields['amount'].get():
            return None
        try:
            amount = float(self.payment_fields['amount'].get())
        except ValueError:
            raise ValueError("Le montant doit être un nombre valide.")
        if amount <= 0:
            raise ValueError("Le montant doit être supérieur à zéro.")
        return {
            "patient_id": int(patient_id),
            "payment_date": self.payment_fields['payment_date'].get(),
            "amount": amount,
            "payment_method": self.payment_fields['payment_method'].get(),
            "reason": self.payment_fields['reason'].get(),
            "notes": self.payment_fields['notes'].get(),
        }

    def add_payment(self):
        try:
            data = self.read_payment_form()
        except ValueError as exc:
            messagebox.showerror("Erreur", str(exc))
            return
        if not data:
            messagebox.showerror("Erreur", "Veuillez remplir les champs obligatoires.")
            return
        try:
            models.create_payment(data)
            self.refresh_payment_table()
            messagebox.showinfo("Succès", "Paiement enregistré.")
        except sqlite3.Error as exc:
            messagebox.showerror("Erreur SQLite", str(exc))

    def update_payment(self):
        payment_id = self.payment_current_id.get()
        if not payment_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un paiement.")
            return
        try:
            data = self.read_payment_form()
        except ValueError as exc:
            messagebox.showerror("Erreur", str(exc))
            return
        if not data:
            messagebox.showerror("Erreur", "Veuillez remplir les champs obligatoires.")
            return
        try:
            models.update_payment(int(payment_id), data)
            self.refresh_payment_table()
            messagebox.showinfo("Succès", "Paiement modifié.")
        except sqlite3.Error as exc:
            messagebox.showerror("Erreur SQLite", str(exc))

    def delete_payment(self):
        payment_id = self.payment_current_id.get()
        if not payment_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un paiement.")
            return
        if messagebox.askyesno("Confirmation", "Supprimer ce paiement ?"):
            try:
                models.delete_payment(int(payment_id))
                self.refresh_payment_table()
                self.payment_current_id.set("")
                messagebox.showinfo("Succès", "Paiement supprimé.")
            except sqlite3.Error as exc:
                messagebox.showerror("Erreur SQLite", str(exc))

    def preview_payment_receipt(self):
        payment_id = self.payment_current_id.get()
        if not payment_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un paiement.")
            return
        conn = sqlite3.connect(models.db_path)
        rec = conn.execute("SELECT p.*, pa.first_name, pa.last_name FROM payments p JOIN patients pa ON pa.id = p.patient_id WHERE p.id = ?", (payment_id,)).fetchone()
        conn.close()
        if not rec:
            return
        text = f"REÇU DE PAIEMENT\n\nPatient: {rec['first_name']} {rec['last_name']}\nDate: {rec['payment_date']}\nMontant: {rec['amount']} €\nMode: {rec['payment_method']}\nMotif: {rec['reason']}\n"
        self.show_preview_window("Reçu de paiement", text)

    def refresh_invoice_table(self):
        rows = models.list_invoices(self.invoice_search.get())
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        for r in rows:
            self.invoice_tree.insert("", "end", values=(r["id"], r["invoice_number"], r["patient_name"], r["invoice_date"], r["total"], r["amount_paid"], r["remaining"]))

    def on_invoice_select(self, event):
        selected = self.invoice_tree.selection()
        if not selected:
            return
        row = self.invoice_tree.item(selected[0], "values")
        invoice_id = row[0]
        invoice = models.get_invoice(int(invoice_id))
        if not invoice:
            return
        self.invoice_current_id.set(str(invoice['id']))
        self.invoice_fields['invoice_number'].delete(0, tk.END)
        self.invoice_fields['invoice_number'].insert(0, invoice.get('invoice_number', ''))
        self.fill_patient_combo(self.invoice_fields['patient_id'], invoice['patient_id'])
        self.invoice_fields['invoice_date'].delete(0, tk.END)
        self.invoice_fields['invoice_date'].insert(0, invoice.get('invoice_date', ''))
        self.fill_treatment_combo(self.invoice_fields['treatment_id'], invoice.get('treatment_id'))
        self.invoice_fields['quantity'].delete(0, tk.END)
        self.invoice_fields['quantity'].insert(0, str(invoice.get('quantity', 1)))
        self.invoice_fields['unit_price'].delete(0, tk.END)
        self.invoice_fields['unit_price'].insert(0, str(invoice.get('unit_price', 0)))
        self.invoice_fields['total'].delete(0, tk.END)
        self.invoice_fields['total'].insert(0, str(invoice.get('total', 0)))
        self.invoice_fields['amount_paid'].delete(0, tk.END)
        self.invoice_fields['amount_paid'].insert(0, str(invoice.get('amount_paid', 0)))
        self.invoice_fields['status'].set(invoice.get('status', 'Ouverte'))
        self.invoice_fields['notes'].delete(0, tk.END)
        self.invoice_fields['notes'].insert(0, invoice.get('notes', ''))

    def read_invoice_form(self):
        patient_selection = self.invoice_fields['patient_id'].get()
        patient_id = patient_selection.split(" - ")[0] if patient_selection else ""
        treatment_selection = self.invoice_fields['treatment_id'].get()
        treatment_id = treatment_selection.split(" - ")[0] if treatment_selection else ""
        invoice_number = self.invoice_fields['invoice_number'].get().strip()
        if not patient_id or not invoice_number:
            return None
        try:
            total = float(self.invoice_fields['total'].get() or 0)
            amount_paid = float(self.invoice_fields['amount_paid'].get() or 0)
            quantity = int(self.invoice_fields['quantity'].get() or 1)
            unit_price = float(self.invoice_fields['unit_price'].get() or 0)
            if total <= 0:
                total = quantity * unit_price
        except ValueError:
            raise ValueError("Les montants et quantités doivent être valides.")
        return {
            "invoice_number": invoice_number,
            "patient_id": int(patient_id),
            "invoice_date": self.invoice_fields['invoice_date'].get(),
            "treatment_id": int(treatment_id) if treatment_id else None,
            "quantity": quantity,
            "unit_price": unit_price,
            "total": total,
            "amount_paid": amount_paid,
            "status": self.invoice_fields['status'].get(),
            "notes": self.invoice_fields['notes'].get(),
            "treatment_name": self.invoice_fields['treatment_id'].get(),
        }

    def add_invoice(self):
        try:
            data = self.read_invoice_form()
        except ValueError as exc:
            messagebox.showerror("Erreur", str(exc))
            return
        if not data:
            messagebox.showerror("Erreur", "Veuillez remplir les champs obligatoires.")
            return
        data["invoice_number"] = data["invoice_number"] or models.generate_invoice_number()
        try:
            models.create_invoice(data)
            self.refresh_invoice_table()
            messagebox.showinfo("Succès", "Facture créée.")
        except sqlite3.Error as exc:
            messagebox.showerror("Erreur SQLite", str(exc))

    def update_invoice(self):
        invoice_id = self.invoice_current_id.get()
        if not invoice_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner une facture.")
            return
        try:
            data = self.read_invoice_form()
        except ValueError as exc:
            messagebox.showerror("Erreur", str(exc))
            return
        if not data:
            messagebox.showerror("Erreur", "Veuillez remplir les champs obligatoires.")
            return
        try:
            models.update_invoice(int(invoice_id), data)
            self.refresh_invoice_table()
            messagebox.showinfo("Succès", "Facture modifiée.")
        except sqlite3.Error as exc:
            messagebox.showerror("Erreur SQLite", str(exc))

    def delete_invoice(self):
        invoice_id = self.invoice_current_id.get()
        if not invoice_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner une facture.")
            return
        if messagebox.askyesno("Confirmation", "Supprimer cette facture ?"):
            try:
                models.delete_invoice(int(invoice_id))
                self.refresh_invoice_table()
                self.invoice_current_id.set("")
                messagebox.showinfo("Succès", "Facture supprimée.")
            except sqlite3.Error as exc:
                messagebox.showerror("Erreur SQLite", str(exc))

    def print_invoice(self):
        invoice_id = self.invoice_current_id.get()
        if not invoice_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner une facture.")
            return
        invoice = models.get_invoice(int(invoice_id))
        if not invoice:
            return
        text = f"FACTURE {invoice['invoice_number']}\n\nPatient: {invoice['first_name']} {invoice['last_name']}\nDate: {invoice['invoice_date']}\nTraitement: {invoice['treatment_type']}\nTotal: {invoice['total']} €\nMontant payé: {invoice['amount_paid']} €\nReste: {invoice['remaining']} €"
        self.show_preview_window("Facture", text)

    def show_preview_window(self, title, text):
        top = tk.Toplevel(self.root)
        top.title(title)
        top.geometry("700x500")
        text_area = tk.Text(top, wrap="word", font=("Segoe UI", 11))
        text_area.insert("1.0", text)
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Button(top, text="Enregistrer (.txt)", command=lambda: self.save_preview_text(text)).pack(pady=(0, 10))

    def save_preview_text(self, text):
        folder = os.path.join(os.getcwd(), "exports")
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        messagebox.showinfo("Succès", f"Document enregistré : {file_path}")

    def load_settings(self):
        settings = models.get_settings()
        for key, widget in self.settings_entries.items():
            widget.delete(0, tk.END)
            widget.insert(0, settings.get(key, ""))

    def save_settings(self):
        data = {key: widget.get().strip() for key, widget in self.settings_entries.items()}
        try:
            models.save_settings(data)
            messagebox.showinfo("Succès", "Paramètres enregistrés.")
        except sqlite3.Error as exc:
            messagebox.showerror("Erreur SQLite", str(exc))

    def refresh_reports(self):
        period = self.report_period.get()
        today = datetime.now().strftime("%Y-%m-%d")
        if period == "Aujourd'hui":
            start, end = today, today
        elif period == "Cette semaine":
            start = (datetime.now().date().fromisoformat(datetime.now().strftime("%Y-%m-%d")) if False else datetime.now().strftime("%Y-%m-%d"))
            start = (datetime.now() - __import__('datetime').timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
            end = today
        elif period == "Ce mois":
            start = datetime.now().strftime("%Y-%m-01")
            end = today
        elif period == "Cette année":
            start = datetime.now().strftime("%Y-01-01")
            end = today
        else:
            start, end = datetime.now().strftime("%Y-%m-01"), today

        data = models.reports(start, end)
        self.report_values["patients"].set(str(data.get("patients", 0)))
        self.report_values["consultations"].set(str(data.get("consultations", 0)))
        self.report_values["appointments"].set(str(data.get("appointments", 0)))
        self.report_values["revenue"].set(f"{data.get('revenue', 0):.2f} €")
        self.report_values["payments"].set(f"{data.get('payments', 0):.2f} €")
        self.report_values["due"].set(f"{data.get('due', 0):.2f} €")


def main():
    ensure_database()
    root = tk.Tk()
    app = DentalClinicApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
