import customtkinter as ctk
from tkinter import messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from solver import resoudre
from graph import creer_graphique

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLORS = {
    "proteines": "#E63946",
    "vitamines": "#457B9D",
    "mineraux":  "#2A9D8F",
    "optimal":   "#F4A261",
    "bg":        "#F8F9FA",
    "text":      "#1D3557",
    "success":   "#2A9D8F",
}


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Optimisation Nutritionnelle")
        self.geometry("1150x700")
        self.resizable(True, True)
        self.configure(fg_color="#F0F4F8")

        self._last_result = None
        self._last_inputs = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_input_panel()
        self._build_result_panel()

    def _build_input_panel(self):
        frame = ctk.CTkFrame(self, corner_radius=16, fg_color="white")
        frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(
            frame,
            text="Optimisation du Regime Alimentaire",
            font=("Arial", 18, "bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, columnspan=3, pady=(20, 5))

        ctk.CTkLabel(
            frame,
            text="Saisir les donnees du probleme",
            font=("Arial", 12),
            text_color="gray",
        ).grid(row=1, column=0, columnspan=3, pady=(0, 15))

        ctk.CTkLabel(frame, text="Couts des aliments (dh)",
                     font=("Arial", 14, "bold"), text_color=COLORS["text"]
                     ).grid(row=2, column=0, columnspan=3, pady=(5, 5))

        self.cost_entries = []
        aliments = ["Aliment A (x1)", "Aliment B (x2)", "Aliment C (x3)"]
        for i in range(3):
            ctk.CTkLabel(frame, text=aliments[i], font=("Arial", 11),
                         text_color="gray").grid(row=3, column=i, padx=10)
            e = ctk.CTkEntry(frame, width=110, height=36,
                             placeholder_text="c" + str(i + 1))
            e.grid(row=4, column=i, padx=10, pady=5)
            self.cost_entries.append(e)

        ctk.CTkLabel(frame, text="Apports Nutritionnels (matrice 3x3)",
                     font=("Arial", 14, "bold"), text_color=COLORS["text"]
                     ).grid(row=5, column=0, columnspan=3, pady=(18, 5))

        headers = ["x1", "x2", "x3"]
        row_labels = ["Proteines", "Vitamines", "Mineraux"]
        row_colors = [COLORS["proteines"], COLORS["vitamines"], COLORS["mineraux"]]

        for j, h in enumerate(headers):
            ctk.CTkLabel(frame, text=h, font=("Arial", 11, "bold"),
                         text_color="gray").grid(row=6, column=j, padx=8)

        self.nutrition_entries = []
        for i in range(3):
            ctk.CTkLabel(frame, text=row_labels[i], font=("Arial", 11, "bold"),
                         text_color=row_colors[i]
                         ).grid(row=7 + i, column=0, padx=(15, 0), sticky="e")
            row_entries = []
            for j in range(3):
                e = ctk.CTkEntry(frame, width=85, height=34,
                                 placeholder_text="a" + str(i + 1) + str(j + 1))
                e.grid(row=7 + i, column=j, padx=8, pady=6)
                row_entries.append(e)
            self.nutrition_entries.append(row_entries)

        ctk.CTkLabel(frame, text="Besoins Minimaux",
                     font=("Arial", 14, "bold"), text_color=COLORS["text"]
                     ).grid(row=10, column=0, columnspan=3, pady=(18, 5))

        self.need_entries = []
        for i in range(3):
            ctk.CTkLabel(frame, text=row_labels[i], font=("Arial", 11),
                         text_color=row_colors[i]).grid(row=11, column=i, padx=10)
            e = ctk.CTkEntry(frame, width=110, height=36,
                             placeholder_text="B" + str(i + 1))
            e.grid(row=12, column=i, padx=10, pady=5)
            self.need_entries.append(e)

        self.solve_button = ctk.CTkButton(
            frame,
            text="Resoudre",
            width=220, height=42,
            font=("Arial", 14, "bold"),
            fg_color=COLORS["text"],
            hover_color="#2F4A70",
            command=self.validate_and_solve,
        )
        self.solve_button.grid(row=13, column=0, columnspan=3, pady=(22, 6))

        self.graph_button = ctk.CTkButton(
            frame,
            text="Voir le graphique",
            width=220, height=42,
            font=("Arial", 13),
            fg_color=COLORS["mineraux"],
            hover_color="#22877A",
            command=self.show_graph_window,
        )
        self.graph_button.grid(row=14, column=0, columnspan=3, pady=(0, 20))

    def _build_result_panel(self):
        self.result_frame = ctk.CTkFrame(self, corner_radius=16, fg_color="white")
        self.result_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        self.result_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.result_frame,
            text="Resultats de l'Optimisation",
            font=("Arial", 18, "bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, pady=(20, 5), padx=20, sticky="w")

        self.status_label = ctk.CTkLabel(
            self.result_frame,
            text="En attente de donnees...",
            font=("Arial", 12),
            text_color="gray",
        )
        self.status_label.grid(row=1, column=0, pady=(0, 15), padx=20, sticky="w")

        sep = ctk.CTkFrame(self.result_frame, height=2, fg_color="#E9ECEF")
        sep.grid(row=2, column=0, sticky="ew", padx=20, pady=5)

        ctk.CTkLabel(
            self.result_frame,
            text="Quantites optimales",
            font=("Arial", 13, "bold"),
            text_color=COLORS["text"],
        ).grid(row=3, column=0, pady=(12, 4), padx=20, sticky="w")

        self.qty_frame = ctk.CTkFrame(self.result_frame, fg_color="#F8F9FA",
                                      corner_radius=10)
        self.qty_frame.grid(row=4, column=0, padx=20, sticky="ew", pady=5)
        self.qty_frame.grid_columnconfigure((0, 1, 2), weight=1)

        aliments = ["Aliment A\n(x1)", "Aliment B\n(x2)", "Aliment C\n(x3)"]
        label_colors = [COLORS["proteines"], COLORS["vitamines"], COLORS["mineraux"]]
        self.qty_labels = []
        for i in range(3):
            ctk.CTkLabel(self.qty_frame, text=aliments[i],
                         font=("Arial", 11), text_color="gray"
                         ).grid(row=0, column=i, padx=10, pady=(10, 2))
            lbl = ctk.CTkLabel(self.qty_frame, text="--",
                               font=("Arial", 22, "bold"),
                               text_color=label_colors[i])
            lbl.grid(row=1, column=i, padx=10, pady=(0, 10))
            self.qty_labels.append(lbl)

        sep2 = ctk.CTkFrame(self.result_frame, height=2, fg_color="#E9ECEF")
        sep2.grid(row=5, column=0, sticky="ew", padx=20, pady=10)

        ctk.CTkLabel(
            self.result_frame,
            text="Cout total minimal",
            font=("Arial", 13, "bold"),
            text_color=COLORS["text"],
        ).grid(row=6, column=0, pady=(5, 4), padx=20, sticky="w")

        self.cost_label = ctk.CTkLabel(
            self.result_frame,
            text="-- dh",
            font=("Arial", 36, "bold"),
            text_color=COLORS["optimal"],
        )
        self.cost_label.grid(row=7, column=0, pady=5, padx=20, sticky="w")

        sep3 = ctk.CTkFrame(self.result_frame, height=2, fg_color="#E9ECEF")
        sep3.grid(row=8, column=0, sticky="ew", padx=20, pady=10)

        ctk.CTkLabel(
            self.result_frame,
            text="Verification des contraintes",
            font=("Arial", 13, "bold"),
            text_color=COLORS["text"],
        ).grid(row=9, column=0, pady=(5, 4), padx=20, sticky="w")

        self.constraint_frame = ctk.CTkFrame(self.result_frame, fg_color="#F8F9FA",
                                             corner_radius=10)
        self.constraint_frame.grid(row=10, column=0, padx=20, sticky="ew", pady=5)
        self.constraint_frame.grid_columnconfigure(0, weight=1)

        self.constraint_labels = []
        nut_names = ["Proteines", "Vitamines", "Mineraux"]
        for i in range(3):
            lbl = ctk.CTkLabel(self.constraint_frame,
                               text=nut_names[i] + ": --",
                               font=("Arial", 11), text_color="gray",
                               anchor="w")
            lbl.grid(row=i, column=0, padx=15, pady=4, sticky="w")
            self.constraint_labels.append(lbl)

        self.bottom_msg = ctk.CTkLabel(
            self.result_frame, text="",
            font=("Arial", 11), text_color="gray",
            wraplength=350,
        )
        self.bottom_msg.grid(row=11, column=0, pady=(10, 20), padx=20, sticky="w")

    def validate_and_solve(self):
        try:
            costs = [float(e.get()) for e in self.cost_entries]
            nutrition = [[float(e.get()) for e in row] for row in self.nutrition_entries]
            needs = [float(e.get()) for e in self.need_entries]
        except ValueError:
            messagebox.showerror("Erreur de saisie",
                                 "Tous les champs doivent contenir des nombres valides.")
            return

        if any(v < 0 for v in costs + needs):
            messagebox.showerror("Erreur de saisie",
                                 "Les couts et besoins doivent etre positifs.")
            return

        for row in nutrition:
            if any(v < 0 for v in row):
                messagebox.showerror("Erreur de saisie",
                                     "Les apports nutritionnels doivent etre positifs.")
                return

        result = resoudre(costs, nutrition, needs)
        self._last_result = result
        self._last_inputs = (costs, nutrition, needs)

        self._display_results(result, nutrition, needs)

    def _display_results(self, result, nutrition, needs):
        nut_names = ["Proteines", "Vitamines", "Mineraux"]
        nut_colors = [COLORS["proteines"], COLORS["vitamines"], COLORS["mineraux"]]

        if result["succes"]:
            self.status_label.configure(
                text="Solution optimale trouvee", text_color=COLORS["success"])

            q = result["quantites"]
            for i, lbl in enumerate(self.qty_labels):
                lbl.configure(text=str(round(q[i], 4)))

            self.cost_label.configure(text=str(round(result["cout_total"], 4)) + " dh")

            for i in range(3):
                apport_total = sum(nutrition[i][j] * q[j] for j in range(3))
                besoin = needs[i]
                ok = apport_total >= besoin - 1e-6
                icon = "OK" if ok else "!!"
                color = COLORS["success"] if ok else "#E63946"
                self.constraint_labels[i].configure(
                    text=icon + " " + nut_names[i] + " : " + str(round(apport_total, 2)) + " >= " + str(besoin),
                    text_color=color,
                )

            self.bottom_msg.configure(
                text=result["message"],
                text_color=COLORS["success"],
            )
        else:
            self.status_label.configure(
                text="Aucune solution trouvee", text_color="#E63946")
            for lbl in self.qty_labels:
                lbl.configure(text="--")
            self.cost_label.configure(text="-- dh")
            for i, lbl in enumerate(self.constraint_labels):
                lbl.configure(text=nut_names[i] + ": --", text_color="gray")
            self.bottom_msg.configure(
                text=result["message"],
                text_color="#E63946",
            )

    def show_graph_window(self):
        if self._last_result is None or not self._last_result["succes"]:
            messagebox.showwarning("Graphique",
                                   "Veuillez d'abord resoudre le probleme avec succes.")
            return

        costs, nutrition, needs = self._last_inputs
        x_opt = self._last_result["quantites"]
        z_opt = self._last_result["cout_total"]

        fig, _ = creer_graphique(
            couts=costs,
            apports=nutrition,
            besoins=needs,
            x_opt=x_opt,
            z_opt=z_opt,
            master=None,
        )

        win = ctk.CTkToplevel(self)
        win.title("Visualisation des Contraintes")
        win.geometry("700x580")
        win.configure(fg_color="white")
        win.grab_set()

        ctk.CTkLabel(win, text="Region Realisable et Point Optimal",
                     font=("Arial", 16, "bold"), text_color=COLORS["text"]
                     ).pack(pady=(15, 5))

        ctk.CTkLabel(win,
                     text="x1=" + str(x_opt[0]) + "  x2=" + str(x_opt[1]) + "  x3=" + str(x_opt[2]) + "   Z*=" + str(z_opt) + " dh",
                     font=("Arial", 12), text_color=COLORS["optimal"]
                     ).pack(pady=(0, 10))

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 15))

        ctk.CTkButton(win, text="Fermer", width=120,
                      fg_color=COLORS["text"], hover_color="#2F4A70",
                      command=win.destroy).pack(pady=(0, 15))


if __name__ == "__main__":
    app = App()
    app.mainloop()