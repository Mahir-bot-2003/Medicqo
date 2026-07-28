import customtkinter as ctk
import httpx
from datetime import datetime
import webbrowser
import os
import fitz
from PIL import Image

API_URL = "http://127.0.0.1:8000"

# COLORS
THEME_SIDEBAR = "#0c2340"
THEME_SIDEBAR_HOVER = "#1a365d"
THEME_BG = "#f5f6fa"
THEME_CARD = "#ffffff"
THEME_PRIMARY = "#1877f2"
THEME_TEXT_MAIN = "#111827"
THEME_TEXT_MUTED = "#6b7280"

ctk.set_appearance_mode("Light")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Medicqo - Hospital CRM")
        self.geometry("1100x750")
        self.state("zoomed")
        self.configure(fg_color=THEME_BG)
        
        self.current_doctor = None
        self.current_patient = None
        self.content_area = None
        
        self.show_login_screen()

    def clear_main(self):
        if self.content_area:
            for widget in self.content_area.winfo_children():
                widget.destroy()

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
            
    # --- AUTHENTICATION ---
    def show_login_screen(self):
        self.clear_screen()
        
        # Split layout for login (left form, right blue panel)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        left_frame = ctk.CTkFrame(self, fg_color=THEME_CARD, corner_radius=0)
        left_frame.grid(row=0, column=0, sticky="nsew")
        
        right_frame = ctk.CTkFrame(self, fg_color=THEME_PRIMARY, corner_radius=0)
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # Right Side Graphic Image
        try:
            img = Image.open("image.png")
            bg_image = ctk.CTkImage(light_image=img, dark_image=img, size=(750, 750))
            lbl = ctk.CTkLabel(right_frame, image=bg_image, text="")
            lbl.place(relx=0.5, rely=0.5, anchor="center")
            
            def resize_bg(event):
                if event.width > 50 and event.height > 50:
                    bg_image.configure(size=(event.width, event.height))
                    
            right_frame.bind("<Configure>", resize_bg)
        except Exception as e:
            print("Login background image not found:", e)
            ctk.CTkLabel(right_frame, text="Medicqo", font=("Helvetica", 40, "bold"), text_color="white").place(relx=0.5, rely=0.4, anchor="center")
            ctk.CTkLabel(right_frame, text="Hospital CRM &\nDigital Prescriptions", font=("Helvetica", 20), text_color="white").place(relx=0.5, rely=0.5, anchor="center")
        
        # Left Side Form
        form_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        form_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(form_frame, text="Welcome Back,\nDoctor", font=("Helvetica", 28, "bold"), text_color=THEME_TEXT_MAIN, justify="left").pack(anchor="w", pady=(0,30))
        
        ctk.CTkLabel(form_frame, text="Phone Number", text_color=THEME_TEXT_MUTED, font=("Helvetica", 12)).pack(anchor="w")
        self.login_phone = ctk.CTkEntry(form_frame, width=300, height=40, border_color="#e5e7eb")
        self.login_phone.pack(pady=(5, 15))
        self.login_phone.insert(0, "555-0100")
        
        ctk.CTkLabel(form_frame, text="Password", text_color=THEME_TEXT_MUTED, font=("Helvetica", 12)).pack(anchor="w")
        self.login_pass = ctk.CTkEntry(form_frame, width=300, height=40, show="*", border_color="#e5e7eb")
        self.login_pass.pack(pady=(5, 20))
        self.login_pass.insert(0, "demo")
        
        ctk.CTkButton(form_frame, text="Login", width=300, height=45, fg_color=THEME_PRIMARY, font=("Helvetica", 14, "bold"), command=self.do_login).pack(pady=(10, 10))
        ctk.CTkButton(form_frame, text="Register New Doctor", width=300, height=40, fg_color="transparent", text_color=THEME_PRIMARY, hover_color="#e5e7eb", command=self.show_register_screen).pack()
        
        self.login_error_label = ctk.CTkLabel(form_frame, text="", text_color="red")
        self.login_error_label.pack(pady=10)

    def do_login(self):
        phone = self.login_phone.get()
        password = self.login_pass.get()
        try:
            res = httpx.post(f"{API_URL}/doctors/login", json={"phone": phone, "password": password})
            if res.status_code == 200:
                self.current_doctor = res.json()
                self.build_main_layout()
            else:
                self.login_error_label.configure(text="Invalid credentials")
        except Exception as e:
            self.login_error_label.configure(text="API connection failed")

    def show_register_screen(self):
        # Extremely simple register view on top of white frame
        self.clear_screen()
        
        form_frame = ctk.CTkFrame(self, fg_color=THEME_CARD, corner_radius=10)
        form_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(form_frame, text="Register Doctor", font=("Helvetica", 24, "bold"), text_color=THEME_TEXT_MAIN).pack(pady=(30,20), padx=50)
        
        reg_name = ctk.CTkEntry(form_frame, placeholder_text="Full Name", width=300, height=40)
        reg_name.pack(pady=10, padx=50)
        reg_spec = ctk.CTkEntry(form_frame, placeholder_text="Specialization", width=300, height=40)
        reg_spec.pack(pady=10, padx=50)
        reg_phone = ctk.CTkEntry(form_frame, placeholder_text="Phone Number", width=300, height=40)
        reg_phone.pack(pady=10, padx=50)
        reg_pass = ctk.CTkEntry(form_frame, placeholder_text="Password", show="*", width=300, height=40)
        reg_pass.pack(pady=10, padx=50)
        
        error_label = ctk.CTkLabel(form_frame, text="", text_color="red")
        
        def do_register():
            try:
                res = httpx.post(f"{API_URL}/doctors/", json={
                    "name": reg_name.get(), "specialization": reg_spec.get(),
                    "phone": reg_phone.get(), "password": reg_pass.get()
                })
                if res.status_code == 200: self.show_login_screen()
                else: error_label.configure(text="Registration failed")
            except Exception:
                error_label.configure(text="API connection failed")
                
        ctk.CTkButton(form_frame, text="Register", width=300, height=45, fg_color=THEME_PRIMARY, command=do_register).pack(pady=(20, 10), padx=50)
        ctk.CTkButton(form_frame, text="Back to Login", width=300, height=40, fg_color="transparent", text_color=THEME_TEXT_MUTED, command=self.show_login_screen).pack(pady=(0, 30), padx=50)
        error_label.pack(pady=5)

    # --- MAIN APPLICATION LAYOUT ---
    def build_main_layout(self):
        self.clear_screen()
        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.build_sidebar()
        
        self.main_container = ctk.CTkFrame(self, fg_color=THEME_BG, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        self.build_header()
        
        self.content_area = ctk.CTkFrame(self.main_container, fg_color=THEME_BG, corner_radius=0)
        self.content_area.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        self.show_patients_view() # Default view

    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=THEME_SIDEBAR, corner_radius=0, width=160)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        logo = ctk.CTkLabel(self.sidebar, text="🏥 Medicqo", font=("Helvetica", 24, "bold"), text_color="white")
        logo.pack(pady=(30, 40), padx=20, anchor="w")
        
        nav_items = [
            ("👥 Patients", self.show_patients_view),
            ("➕ Add Patient", self.show_add_patient_view),
            ("⚙️ Settings", self.show_settings_view)
        ]
        
        for text, cmd in nav_items:
            btn = ctk.CTkButton(self.sidebar, text=text, fg_color="transparent", text_color="white", 
                                hover_color=THEME_SIDEBAR_HOVER, anchor="w", command=cmd, font=("Helvetica", 14))
            btn.pack(fill="x", padx=10, pady=5)
            
        logout_btn = ctk.CTkButton(self.sidebar, text="🚪 Logout", fg_color="transparent", text_color="#ef4444", 
                                hover_color=THEME_SIDEBAR_HOVER, anchor="w", command=self.show_login_screen, font=("Helvetica", 14))
        logout_btn.pack(side="bottom", fill="x", padx=10, pady=20)

    def build_header(self):
        header = ctk.CTkFrame(self.main_container, fg_color=THEME_CARD, corner_radius=0, height=70)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        
        # Search Bar
        search = ctk.CTkEntry(header, placeholder_text="🔍 Search patients...", width=400, height=35, border_color="#e5e7eb", fg_color="#f3f4f6")
        search.pack(side="left", padx=20, pady=17)
        
        # Doctor Profile
        profile_frame = ctk.CTkFrame(header, fg_color="transparent")
        profile_frame.pack(side="right", padx=20, pady=10)
        
        ctk.CTkLabel(profile_frame, text=self.current_doctor['name'], font=("Helvetica", 14, "bold"), text_color=THEME_TEXT_MAIN).pack(side="top", anchor="e")
        ctk.CTkLabel(profile_frame, text=self.current_doctor['specialization'], font=("Helvetica", 11), text_color=THEME_TEXT_MUTED).pack(side="bottom", anchor="e")

    # --- VIEWS ---
    def show_patients_view(self):
        self.clear_main()
        
        top = ctk.CTkFrame(self.content_area, fg_color="transparent")
        top.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(top, text="Patients", font=("Helvetica", 24, "bold"), text_color=THEME_TEXT_MAIN).pack(side="left")
        ctk.CTkButton(top, text="+ Add Patient", fg_color=THEME_PRIMARY, command=self.show_add_patient_view).pack(side="right")
        
        list_frame = ctk.CTkScrollableFrame(self.content_area, fg_color=THEME_CARD, corner_radius=10)
        list_frame.pack(fill="both", expand=True)
        
        # Table Header
        header_frame = ctk.CTkFrame(list_frame, fg_color="#f9fafb", corner_radius=5)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(header_frame, text="Name", font=("Helvetica", 12, "bold"), text_color=THEME_TEXT_MUTED, width=150, anchor="w").pack(side="left", padx=10, pady=5)
        ctk.CTkLabel(header_frame, text="Phone", font=("Helvetica", 12, "bold"), text_color=THEME_TEXT_MUTED, width=120, anchor="w").pack(side="left", padx=10, pady=5)
        ctk.CTkLabel(header_frame, text="DOB", font=("Helvetica", 12, "bold"), text_color=THEME_TEXT_MUTED, width=100, anchor="w").pack(side="left", padx=10, pady=5)
        ctk.CTkLabel(header_frame, text="Action", font=("Helvetica", 12, "bold"), text_color=THEME_TEXT_MUTED, width=150, anchor="w").pack(side="right", padx=10, pady=5)
        
        try:
            res = httpx.get(f"{API_URL}/patients/")
            if res.status_code == 200:
                for p in res.json():
                    row = ctk.CTkFrame(list_frame, fg_color="transparent")
                    row.pack(fill="x", padx=10, pady=2)
                    
                    ctk.CTkLabel(row, text=p['name'], font=("Helvetica", 13), text_color=THEME_TEXT_MAIN, width=150, anchor="w").pack(side="left", padx=10, pady=5)
                    ctk.CTkLabel(row, text=p['phone'], font=("Helvetica", 13), text_color=THEME_TEXT_MUTED, width=120, anchor="w").pack(side="left", padx=10, pady=5)
                    ctk.CTkLabel(row, text=p['dob'], font=("Helvetica", 13), text_color=THEME_TEXT_MUTED, width=100, anchor="w").pack(side="left", padx=10, pady=5)
                    
                    action_frame = ctk.CTkFrame(row, fg_color="transparent", width=150)
                    action_frame.pack(side="right", padx=10)
                    
                    def delete_patient_action(pid=p['id']):
                        try:
                            httpx.delete(f"{API_URL}/patients/{pid}")
                            self.show_patients_view()
                        except: pass
                        
                    ctk.CTkButton(action_frame, text="🗑", width=30, fg_color="#ef4444", hover_color="#dc2626", command=delete_patient_action).pack(side="right", padx=2)
                    ctk.CTkButton(action_frame, text="📝 Prescribe", width=80, fg_color=THEME_PRIMARY, command=lambda patient=p: self.show_prescription_view(patient)).pack(side="right", padx=2)
                    
                    # separator
                    ctk.CTkFrame(list_frame, height=1, fg_color="#e5e7eb").pack(fill="x", padx=10)
        except Exception as e:
            ctk.CTkLabel(list_frame, text="Error loading patients.", text_color="red").pack(pady=20)

    def show_add_patient_view(self):
        self.clear_main()
        
        ctk.CTkLabel(self.content_area, text="Add New Patient", font=("Helvetica", 24, "bold"), text_color=THEME_TEXT_MAIN).pack(anchor="w", pady=(0, 20))
        
        form = ctk.CTkFrame(self.content_area, fg_color=THEME_CARD, corner_radius=10)
        form.pack(fill="both", expand=True)
        
        name_entry = ctk.CTkEntry(form, placeholder_text="Full Name", width=400, height=40)
        name_entry.pack(pady=(30,10), padx=40)
        
        phone_entry = ctk.CTkEntry(form, placeholder_text="Phone Number", width=400, height=40)
        phone_entry.pack(pady=10, padx=40)
        
        dob_frame = ctk.CTkFrame(form, fg_color="transparent")
        dob_frame.pack(pady=10, padx=40)
        
        dob_d = ctk.CTkEntry(dob_frame, placeholder_text="DD", width=95, height=40)
        dob_d.pack(side="left")
        
        ctk.CTkLabel(dob_frame, text="/", font=("Helvetica", 18)).pack(side="left", padx=10)
        
        dob_m = ctk.CTkEntry(dob_frame, placeholder_text="MM", width=95, height=40)
        dob_m.pack(side="left")
        
        ctk.CTkLabel(dob_frame, text="/", font=("Helvetica", 18)).pack(side="left", padx=10)
        
        dob_y = ctk.CTkEntry(dob_frame, placeholder_text="YYYY", width=150, height=40)
        dob_y.pack(side="left")
        
        gender_entry = ctk.CTkComboBox(form, values=["Male", "Female", "Other"], width=400, height=40)
        gender_entry.pack(pady=10, padx=40)
        
        err_label = ctk.CTkLabel(form, text="", text_color="red")
        
        def save_patient():
            payload = {
                "name": name_entry.get().strip(),
                "phone": phone_entry.get().strip(),
                "dob": f"{dob_y.get().strip()}-{dob_m.get().strip()}-{dob_d.get().strip()}",
                "gender": gender_entry.get()
            }
            try:
                res = httpx.post(f"{API_URL}/patients/", json=payload)
                if res.status_code == 200: self.show_patients_view()
                else: err_label.configure(text="Failed to add patient")
            except Exception as e:
                err_label.configure(text="API Error")
                
        ctk.CTkButton(form, text="Save Patient", width=400, height=45, fg_color=THEME_PRIMARY, command=save_patient).pack(pady=(20, 10), padx=40)
        err_label.pack()

    def show_prescription_view(self, patient):
        self.clear_main()
        self.current_patient = patient
        
        top = ctk.CTkFrame(self.content_area, fg_color="transparent")
        top.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(top, text=f"New Prescription - {patient['name']}", font=("Helvetica", 24, "bold"), text_color=THEME_TEXT_MAIN).pack(side="left")
        ctk.CTkButton(top, text="< Back", fg_color="transparent", text_color=THEME_PRIMARY, border_width=1, border_color=THEME_PRIMARY, command=self.show_patients_view).pack(side="right")
        
        # 2 Column layout
        grid_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        grid_frame.grid_rowconfigure(0, weight=1)
        
        # LEFT COLUMN (Details)
        left_col = ctk.CTkFrame(grid_frame, fg_color=THEME_CARD, corner_radius=10)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(left_col, text="Symptoms", font=("Helvetica", 14, "bold"), text_color=THEME_TEXT_MAIN).pack(anchor="w", padx=20, pady=(20,5))
        ent_symptoms = ["Ear Pain", "Hearing Loss", "Sore Throat", "Nasal Congestion", "Tinnitus", "Vertigo", "Tonsillitis", "Cough", "Cold"]
        symp_box = ctk.CTkComboBox(left_col, values=ent_symptoms, height=35, fg_color="#f9fafb", border_color="#e5e7eb", border_width=1)
        symp_box.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(left_col, text="Diagnosis", font=("Helvetica", 14, "bold"), text_color=THEME_TEXT_MAIN).pack(anchor="w", padx=20, pady=(15,5))
        ent_diagnosis = ["Otitis Media", "Allergic Rhinitis", "Pharyngitis", "Sinusitis", "Wax Impaction", "Laryngitis"]
        diag_box = ctk.CTkComboBox(left_col, values=ent_diagnosis, height=35, fg_color="#f9fafb", border_color="#e5e7eb", border_width=1)
        diag_box.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(left_col, text="Notes", font=("Helvetica", 14, "bold"), text_color=THEME_TEXT_MAIN).pack(anchor="w", padx=20, pady=(15,5))
        notes_box = ctk.CTkTextbox(left_col, height=60, fg_color="#f9fafb", border_color="#e5e7eb", border_width=1)
        notes_box.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(left_col, text="Past History", font=("Helvetica", 14, "bold"), text_color=THEME_TEXT_MAIN).pack(anchor="w", padx=20, pady=(20,5))
        history_frame = ctk.CTkScrollableFrame(left_col, fg_color="#f9fafb", border_color="#e5e7eb", border_width=1)
        history_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        try:
            res = httpx.get(f"{API_URL}/patients/{patient['id']}/prescriptions/")
            if res.status_code == 200:
                past_rx = res.json()
                if not past_rx:
                    ctk.CTkLabel(history_frame, text="No previous history.", text_color=THEME_TEXT_MUTED).pack(pady=10)
                else:
                    for rx in reversed(past_rx):
                        date_str = rx.get("created_at", "Unknown")[:10] if rx.get("created_at") else "Unknown"
                        diag = rx.get("diagnosis", "N/A")
                        rx_id = rx.get("id")
                        
                        def make_open_cmd(pid):
                            return lambda: __import__('os').startfile(__import__('os').path.abspath(f"prescriptions_pdfs/prescription_{pid}.pdf")) if __import__('os').path.exists(f"prescriptions_pdfs/prescription_{pid}.pdf") else print("PDF not found")
                            
                        ctk.CTkButton(history_frame, text=f"📄 {date_str}: {diag}", 
                                      fg_color="transparent", text_color=THEME_PRIMARY, hover_color="#e5e7eb",
                                      anchor="w", command=make_open_cmd(rx_id)).pack(fill="x", padx=10, pady=2)
        except Exception as e:
            ctk.CTkLabel(history_frame, text="Could not load history.", text_color="red").pack()
        
        # RIGHT COLUMN (Medicines)
        right_col = ctk.CTkFrame(grid_frame, fg_color=THEME_CARD, corner_radius=10)
        right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        ctk.CTkLabel(right_col, text="Medicines", font=("Helvetica", 14, "bold"), text_color=THEME_TEXT_MAIN).pack(anchor="w", padx=20, pady=(20, 10))
        
        meds_frame = ctk.CTkScrollableFrame(right_col, fg_color="transparent", height=180)
        meds_frame.pack(fill="x", padx=10)
        
        self.medicine_rows = []
        
        def add_med_row():
            row = ctk.CTkFrame(meds_frame, fg_color="#f9fafb", border_color="#e5e7eb", border_width=1, corner_radius=5)
            row.pack(fill="x", pady=5)
            
            ent_meds = ["Paracetamol 500mg", "Amoxicillin 500mg", "Ibuprofen 400mg", "Cetirizine 10mg", "Azithromycin 500mg", "Otrivin Drops", "Cough Syrup"]
            n = ctk.CTkComboBox(row, values=ent_meds, width=140, height=30)
            n.pack(side="left", padx=5, pady=5)
            
            d = ctk.CTkEntry(row, placeholder_text="Dosage", width=60, height=30)
            d.pack(side="left", padx=5, pady=5)
            
            f = ctk.CTkEntry(row, placeholder_text="Freq (1-0-1)", width=80, height=30)
            f.pack(side="left", padx=5, pady=5)
            
            dur_options = ["3 Days", "5 Days", "7 Days", "10 Days", "14 Days", "1 Month"]
            dur = ctk.CTkComboBox(row, values=dur_options, width=80, height=30)
            dur.pack(side="left", padx=5, pady=5)
            
            def remove_self():
                row.destroy()
                self.medicine_rows = [r for r in self.medicine_rows if r["frame"] != row]
                
            ctk.CTkButton(row, text="X", width=30, fg_color="#ef4444", command=remove_self).pack(side="right", padx=5)
            
            self.medicine_rows.append({"frame": row, "name": n, "dosage": d, "freq": f, "dur": dur})
            
        add_med_row() # initial row
        
        ctk.CTkButton(right_col, text="+ Add Medicine", fg_color="transparent", text_color=THEME_PRIMARY, border_color=THEME_PRIMARY, border_width=1, command=add_med_row).pack(pady=10, padx=20, anchor="w")
        
        # Bottom Actions
        actions = ctk.CTkFrame(right_col, fg_color="transparent")
        actions.pack(fill="x", pady=20, padx=20)
        
        send_channel = ctk.CTkComboBox(actions, values=["whatsapp", "telegram"], width=120)
        send_channel.pack(side="left")
        
        status_lbl = ctk.CTkLabel(actions, text="", text_color="green")
        status_lbl.pack(side="left", padx=10)
        
        preview_scroll = ctk.CTkScrollableFrame(right_col, fg_color="transparent")
        preview_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        preview_lbl = ctk.CTkLabel(preview_scroll, text="PDF Preview will appear here", text_color=THEME_TEXT_MUTED)
        preview_lbl.pack(pady=20)
        
        def submit_with_channel(channel_str):
            meds = []
            for r in self.medicine_rows:
                n = r["name"].get().strip()
                if n:
                    meds.append({
                        "name": n,
                        "dosage": r["dosage"].get(),
                        "frequency": r["freq"].get(),
                        "duration": r["dur"].get()
                    })
                    
            payload = {
                "symptoms": symp_box.get().strip(),
                "diagnosis": diag_box.get().strip(),
                "notes": notes_box.get("1.0", "end").strip(),
                "medicines": meds,
                "patient_id": patient["id"],
                "doctor_id": self.current_doctor["id"],
                "send_channel": channel_str
            }
            
            try:
                res = httpx.post(f"{API_URL}/prescriptions/", json=payload)
                if res.status_code == 200:
                    pid = res.json()['id']
                    if channel_str == "preview":
                        status_lbl.configure(text="Generated!", text_color="green")
                        # Give the background task 1 second to create the PDF, then open it
                        import os
                        self.after(1000, lambda: self.show_inline_pdf_preview(os.path.abspath(f"prescriptions_pdfs/prescription_{pid}.pdf"), preview_lbl))
                    else:
                        status_lbl.configure(text="Sent!", text_color="green")
                else:
                    status_lbl.configure(text="Failed", text_color="red")
            except Exception:
                status_lbl.configure(text="API Error", text_color="red")
                
        ctk.CTkButton(actions, text="Preview PDF", fg_color="transparent", text_color=THEME_PRIMARY, border_color=THEME_PRIMARY, border_width=1, height=40, command=lambda: submit_with_channel("preview")).pack(side="right", padx=10)
        ctk.CTkButton(actions, text="Generate & Send", fg_color=THEME_PRIMARY, height=40, command=lambda: submit_with_channel(send_channel.get())).pack(side="right")

    def show_settings_view(self):
        self.clear_main()
        
        ctk.CTkLabel(self.content_area, text="Settings", font=("Helvetica", 24, "bold"), text_color=THEME_TEXT_MAIN).pack(anchor="w", pady=(0, 20))
        
        form = ctk.CTkFrame(self.content_area, fg_color=THEME_CARD, corner_radius=10)
        form.pack(fill="both", expand=True)
        
        ctk.CTkLabel(form, text="Messaging API Keys", font=("Helvetica", 16, "bold"), text_color=THEME_TEXT_MAIN).pack(anchor="w", pady=(20, 10), padx=40)
        
        t_sid = ctk.CTkEntry(form, placeholder_text="Twilio Account SID", width=400, height=40)
        t_sid.pack(pady=10, padx=40, anchor="w")
        
        t_auth = ctk.CTkEntry(form, placeholder_text="Twilio Auth Token", width=400, height=40, show="*")
        t_auth.pack(pady=10, padx=40, anchor="w")
        
        t_from = ctk.CTkEntry(form, placeholder_text="Twilio From Number (e.g. whatsapp:+14155238886)", width=400, height=40)
        t_from.pack(pady=10, padx=40, anchor="w")
        
        tg_token = ctk.CTkEntry(form, placeholder_text="Telegram Bot Token", width=400, height=40)
        tg_token.pack(pady=10, padx=40, anchor="w")
        
        # Load existing
        try:
            res = httpx.get(f"{API_URL}/settings/")
            if res.status_code == 200:
                data = res.json()
                t_sid.insert(0, data.get("twilio_sid", ""))
                t_auth.insert(0, data.get("twilio_auth", ""))
                t_from.insert(0, data.get("twilio_from", ""))
                tg_token.insert(0, data.get("telegram_bot_token", ""))
        except: pass
        
        status_lbl = ctk.CTkLabel(form, text="", text_color="green")
        
        def save_settings():
            payload = {
                "twilio_sid": t_sid.get().strip(),
                "twilio_auth": t_auth.get().strip(),
                "twilio_from": t_from.get().strip(),
                "telegram_bot_token": tg_token.get().strip()
            }
            try:
                res = httpx.post(f"{API_URL}/settings/", json=payload)
                if res.status_code == 200:
                    status_lbl.configure(text="Settings Saved!", text_color="green")
                else:
                    status_lbl.configure(text="Failed to save", text_color="red")
            except:
                status_lbl.configure(text="API Error", text_color="red")
                
        ctk.CTkButton(form, text="Save Settings", width=200, height=45, fg_color=THEME_PRIMARY, command=save_settings).pack(pady=(20, 10), padx=40, anchor="w")
        status_lbl.pack(padx=40, anchor="w")

    def show_inline_pdf_preview(self, pdf_path, lbl_widget):
        try:
            doc = fitz.open(pdf_path)
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.8, 0.8)) # Scaled slightly to fit well inline
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(pix.width, pix.height))
            lbl_widget.configure(image=ctk_img, text="")
            lbl_widget.image = ctk_img
        except Exception as e:
            print(f"Failed to load PDF preview: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
