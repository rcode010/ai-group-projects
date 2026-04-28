import tkinter as tk
from tkinter import ttk, messagebox


# ── Colours & fonts ──────────────────────────────────────────────────────────
BG          = "#0f1117"
CARD        = "#1a1d27"
ACCENT      = "#6c63ff"
ACCENT_DARK = "#4e47cc"
TEXT        = "#e8e8f0"
TEXT_DIM    = "#7a7a9a"
SUCCESS     = "#22c55e"
DANGER      = "#ef4444"
BORDER      = "#2a2d3e"

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_SUB    = ("Segoe UI", 11)
FONT_LABEL  = ("Segoe UI", 10, "bold")
FONT_INPUT  = ("Segoe UI", 11)
FONT_BTN    = ("Segoe UI", 11, "bold")
FONT_RESULT = ("Segoe UI", 14, "bold")
FONT_SMALL  = ("Segoe UI", 9)


# ── Placeholder entry helper ─────────────────────────────────────────────────
class PlaceholderEntry(tk.Entry):
    def __init__(self, master, placeholder, **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self._active = False
        self.configure(fg=TEXT_DIM)
        self.insert(0, placeholder)
        self.bind("<FocusIn>",  self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, _):
        if not self._active:
            self.delete(0, tk.END)
            self.configure(fg=TEXT)
            self._active = True

    def _on_focus_out(self, _):
        if not self.get():
            self.insert(0, self.placeholder)
            self.configure(fg=TEXT_DIM)
            self._active = False

    def get_value(self):
        v = self.get()
        return "" if v == self.placeholder else v.strip()


# ── Main App ─────────────────────────────────────────────────────────────────
class AnimalConditionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Animal Condition Classifier")
        self.geometry("700x780")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._center()
        self._build()

    # ── window centering ──
    def _center(self):
        self.update_idletasks()
        w, h = 700, 780
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── layout ──
    def _build(self):
        # scrollable canvas so it works on small screens too
        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=BG)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._build_header()
        self._build_animal_row()
        self._build_symptoms()
        self._build_button()
        self._build_results()
        self._build_footer()

    # ── header ──
    def _build_header(self):
        f = tk.Frame(self.scroll_frame, bg=BG)
        f.pack(fill="x", padx=40, pady=(36, 4))

        tk.Label(f, text="🐾  Animal Condition Classifier",
                 bg=BG, fg=TEXT, font=FONT_TITLE).pack(anchor="w")
        tk.Label(f, text="Enter the animal name and five observed symptoms to predict condition severity.",
                 bg=BG, fg=TEXT_DIM, font=FONT_SUB).pack(anchor="w", pady=(4, 0))

        # divider
        tk.Frame(self.scroll_frame, bg=BORDER, height=1).pack(fill="x", padx=40, pady=(16, 0))

    # ── animal name row ──
    def _build_animal_row(self):
        card = self._card(pady_top=24)

        tk.Label(card, text="Animal Name", bg=CARD, fg=TEXT_DIM,
                 font=FONT_LABEL).pack(anchor="w", pady=(0, 6))

        self.animal_entry = PlaceholderEntry(
            card, "e.g. Dog, Cat, Buffalo …",
            bg=CARD, relief="flat", font=FONT_INPUT,
            insertbackground=TEXT, highlightthickness=1,
            highlightbackground=BORDER, highlightcolor=ACCENT
        )
        self.animal_entry.pack(fill="x", ipady=10, padx=2)

    # ── symptom inputs ──
    def _build_symptoms(self):
        card = self._card(pady_top=16)

        tk.Label(card, text="Observed Symptoms", bg=CARD, fg=TEXT_DIM,
                 font=FONT_LABEL).pack(anchor="w", pady=(0, 14))

        placeholders = [
            "e.g. Fever",
            "e.g. Diarrhea",
            "e.g. Vomiting",
            "e.g. Weight loss",
            "e.g. Lethargy",
        ]

        self.symptom_entries = []
        for i, ph in enumerate(placeholders):
            row = tk.Frame(card, bg=CARD)
            row.pack(fill="x", pady=5)

            # number badge
            badge = tk.Label(row, text=str(i + 1), bg=ACCENT, fg="white",
                             font=("Segoe UI", 9, "bold"), width=2)
            badge.pack(side="left", padx=(0, 10), ipady=6)

            entry = PlaceholderEntry(
                row, ph,
                bg="#22253a", relief="flat", font=FONT_INPUT,
                insertbackground=TEXT, highlightthickness=1,
                highlightbackground=BORDER, highlightcolor=ACCENT
            )
            entry.pack(side="left", fill="x", expand=True, ipady=9, padx=2)
            self.symptom_entries.append(entry)

    # ── predict button ──
    def _build_button(self):
        f = tk.Frame(self.scroll_frame, bg=BG)
        f.pack(fill="x", padx=40, pady=(20, 0))

        self.predict_btn = tk.Button(
            f, text="  Predict Condition  ",
            bg=ACCENT, fg="white", font=FONT_BTN,
            relief="flat", cursor="hand2", activebackground=ACCENT_DARK,
            activeforeground="white", padx=20, pady=12,
            command=self._predict
        )
        self.predict_btn.pack(side="left")

        self.clear_btn = tk.Button(
            f, text="Clear",
            bg=CARD, fg=TEXT_DIM, font=FONT_BTN,
            relief="flat", cursor="hand2", activebackground=BORDER,
            activeforeground=TEXT, padx=20, pady=12,
            command=self._clear
        )
        self.clear_btn.pack(side="left", padx=(12, 0))

    # ── results panel ──
    def _build_results(self):
        self.results_frame = tk.Frame(self.scroll_frame, bg=BG)
        self.results_frame.pack(fill="x", padx=40, pady=(24, 0))

    # ── footer ──
    def _build_footer(self):
        tk.Frame(self.scroll_frame, bg=BORDER, height=1).pack(fill="x", padx=40, pady=(28, 0))
        tk.Label(self.scroll_frame,
                 text="AI Final Project  •  Koya University  •  2025",
                 bg=BG, fg=TEXT_DIM, font=FONT_SMALL).pack(pady=(8, 24))

    # ── card helper ──
    def _card(self, pady_top=16):
        outer = tk.Frame(self.scroll_frame, bg=CARD, bd=0,
                         highlightthickness=1, highlightbackground=BORDER)
        outer.pack(fill="x", padx=40, pady=(pady_top, 0))
        inner = tk.Frame(outer, bg=CARD)
        inner.pack(fill="x", padx=20, pady=18)
        return inner

    # ── predict logic ──
    def _predict(self):
        animal   = self.animal_entry.get_value()
        symptoms = [e.get_value() for e in self.symptom_entries]

        # validation
        if not animal:
            messagebox.showwarning("Missing Input", "Please enter the animal name.")
            return
        if any(s == "" for s in symptoms):
            messagebox.showwarning("Missing Input", "Please fill in all 5 symptoms.")
            return

        # ── call your models here ──────────────────────────────────────────
        # Replace the mock results below with real model predictions.
        # Example:
        #   from preprocessing.preprocessing import encode_input
        #   from models.knn.knn       import predict as knn_predict
        #   from models.svm.svm       import predict as svm_predict
        #   from models.naive_bayes.naive_bayes import predict as nb_predict
        #   from models.neural_network.neural_network import predict as nn_predict
        #
        #   X = encode_input(symptoms)
        #   predictions = {
        #       "KNN":            knn_predict(X),
        #       "SVM":            svm_predict(X),
        #       "Naive Bayes":    nb_predict(X),
        #       "Neural Network": nn_predict(X),
        #   }
        # ─────────────────────────────────────────────────────────────────

        # MOCK — remove when models are ready
        predictions = {
            "KNN":            "Dangerous",
            "SVM":            "Dangerous",
            "Naive Bayes":    "Not Dangerous",
            "Neural Network": "Dangerous",
        }

        self._show_results(animal, symptoms, predictions)

    # ── render results ──
    def _show_results(self, animal, symptoms, predictions):
        # clear old results
        for w in self.results_frame.winfo_children():
            w.destroy()

        # title
        tk.Label(self.results_frame, text="Prediction Results",
                 bg=BG, fg=TEXT, font=FONT_LABEL).pack(anchor="w", pady=(0, 12))

        # summary badge
        dangerous_votes = sum(1 for v in predictions.values() if v == "Dangerous")
        total           = len(predictions)
        majority        = "Dangerous" if dangerous_votes > total // 2 else "Not Dangerous"
        badge_color     = DANGER if majority == "Dangerous" else SUCCESS
        badge_text      = f"{'⚠️  DANGEROUS' if majority == 'Dangerous' else '✅  NOT DANGEROUS'}  —  {dangerous_votes}/{total} models agree"

        summary = tk.Frame(self.results_frame, bg=badge_color)
        summary.pack(fill="x", pady=(0, 14))
        tk.Label(summary, text=badge_text,
                 bg=badge_color, fg="white", font=FONT_RESULT,
                 pady=14).pack()

        # per-model cards
        icons = {
            "KNN":            "🔵",
            "SVM":            "🟣",
            "Naive Bayes":    "🟠",
            "Neural Network": "🟢",
        }

        for model_name, result in predictions.items():
            color = DANGER if result == "Dangerous" else SUCCESS
            card  = tk.Frame(self.results_frame, bg=CARD,
                             highlightthickness=1, highlightbackground=BORDER)
            card.pack(fill="x", pady=4)

            inner = tk.Frame(card, bg=CARD)
            inner.pack(fill="x", padx=16, pady=12)

            tk.Label(inner,
                     text=f"{icons.get(model_name, '⚪')}  {model_name}",
                     bg=CARD, fg=TEXT, font=FONT_INPUT).pack(side="left")

            tk.Label(inner, text=result,
                     bg=color, fg="white",
                     font=("Segoe UI", 9, "bold"),
                     padx=10, pady=4).pack(side="right")

        # input summary
        summary_card = tk.Frame(self.results_frame, bg=CARD,
                                highlightthickness=1, highlightbackground=BORDER)
        summary_card.pack(fill="x", pady=(14, 24))
        inner2 = tk.Frame(summary_card, bg=CARD)
        inner2.pack(fill="x", padx=16, pady=12)

        tk.Label(inner2, text=f"Animal: {animal}",
                 bg=CARD, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")
        tk.Label(inner2,
                 text="Symptoms: " + "  •  ".join(symptoms),
                 bg=CARD, fg=TEXT_DIM, font=FONT_SMALL,
                 wraplength=580, justify="left").pack(anchor="w", pady=(4, 0))

    # ── clear ──
    def _clear(self):
        self.animal_entry.delete(0, tk.END)
        self.animal_entry.insert(0, self.animal_entry.placeholder)
        self.animal_entry.configure(fg=TEXT_DIM)
        self.animal_entry._active = False

        for e in self.symptom_entries:
            e.delete(0, tk.END)
            e.insert(0, e.placeholder)
            e.configure(fg=TEXT_DIM)
            e._active = False

        for w in self.results_frame.winfo_children():
            w.destroy()


# ── run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = AnimalConditionApp()
    app.mainloop()