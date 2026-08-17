from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from database import WorkshopDatabase


APP_TITLE = "Bauteilsuche"
DEFAULT_DB = Path(__file__).with_name("workshop.db")

BG = "#f5f7fb"
SURFACE = "#ffffff"
SURFACE_ALT = "#f8fafc"
BORDER = "#e5e7eb"
TEXT = "#111827"
MUTED = "#6b7280"
ACCENT = "#2563eb"
ACCENT_SOFT = "#eff6ff"


class SearchApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1040x650")
        self.minsize(860, 560)
        self.configure(bg=BG)

        self.db = None
        self.interface_names = {}

        self._configure_style()
        self._build_ui()

        if DEFAULT_DB.exists():
            self.open_database(DEFAULT_DB)
        else:
            self.db_name.set("Keine Datenbank geöffnet")

    def _configure_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background=SURFACE,
            fieldbackground=SURFACE,
            foreground=TEXT,
            rowheight=38,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.map(
            "Treeview",
            background=[("selected", ACCENT_SOFT)],
            foreground=[("selected", TEXT)],
        )
        style.configure(
            "Treeview.Heading",
            background=SURFACE_ALT,
            foreground=MUTED,
            borderwidth=0,
            padding=(10, 10),
            font=("Segoe UI Semibold", 9),
        )

    def _build_ui(self):
        page = tk.Frame(self, bg=BG)
        page.pack(fill="both", expand=True, padx=26, pady=22)

        header = tk.Frame(page, bg=BG)
        header.pack(fill="x", pady=(0, 18))

        title = tk.Frame(header, bg=BG)
        title.pack(side="left", fill="x", expand=True)

        tk.Label(
            title,
            text="Bauteilsuche",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI Semibold", 22),
        ).pack(anchor="w")

        tk.Label(
            title,
            text="Durchsuche deinen katalogisierten Elektronikbestand.",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(3, 0))

        self.db_name = tk.StringVar(value="")
        tk.Label(
            header,
            textvariable=self.db_name,
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(side="right", padx=(0, 12))

        tk.Button(
            header,
            text="Datenbank öffnen",
            command=self.choose_database,
            bg=ACCENT,
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI Semibold", 9),
            padx=14,
            pady=8,
        ).pack(side="right")

        search_card = tk.Frame(
            page,
            bg=SURFACE,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        search_card.pack(fill="x", pady=(0, 14))

        row = tk.Frame(search_card, bg=SURFACE)
        row.pack(fill="x", padx=16, pady=16)

        search_shell = tk.Frame(
            row,
            bg=SURFACE_ALT,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        search_shell.pack(side="left", fill="x", expand=True)

        tk.Label(
            search_shell,
            text="Suche",
            bg=SURFACE_ALT,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(side="left", padx=(12, 8))

        self.search_var = tk.StringVar()
        entry = tk.Entry(
            search_shell,
            textvariable=self.search_var,
            bg=SURFACE_ALT,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            bd=0,
            font=("Segoe UI", 11),
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=10)
        entry.bind("<KeyRelease>", lambda _e: self.refresh_results())

        tk.Button(
            search_shell,
            text="×",
            command=self.clear_search,
            bg=SURFACE_ALT,
            fg=MUTED,
            activebackground=SURFACE_ALT,
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI Semibold", 12),
        ).pack(side="right", padx=(0, 8))

        self.count_var = tk.StringVar(value="0 Treffer")
        tk.Label(
            row,
            textvariable=self.count_var,
            bg=SURFACE,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(side="right", padx=(14, 0))

        body = tk.Frame(page, bg=BG)
        body.pack(fill="both", expand=True)

        table_card = tk.Frame(
            body,
            bg=SURFACE,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        table_card.pack(side="left", fill="both", expand=True)

        columns = ("name", "category", "manufacturer", "interfaces", "quantity", "row", "column")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")

        headings = {
            "name": "Name",
            "category": "Kategorie",
            "manufacturer": "Hersteller",
            "interfaces": "Schnittstellen",
            "quantity": "Bestand",
            "row": "Reihe",
            "column": "Spalte",
        }
        widths = {
            "name": 180,
            "category": 120,
            "manufacturer": 130,
            "interfaces": 170,
            "quantity": 70,
            "row": 60,
            "column": 60,
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")

        scroll = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.show_details)

        details = tk.Frame(
            body,
            bg=SURFACE,
            width=270,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        details.pack(side="left", fill="y", padx=(14, 0))
        details.pack_propagate(False)

        tk.Label(
            details,
            text="Details",
            bg=SURFACE,
            fg=TEXT,
            font=("Segoe UI Semibold", 14),
        ).pack(anchor="w", padx=18, pady=(18, 4))

        self.details = tk.Text(
            details,
            bg=SURFACE,
            fg=TEXT,
            relief="flat",
            bd=0,
            highlightthickness=0,
            wrap="word",
            font=("Segoe UI", 10),
            state="disabled",
        )
        self.details.pack(fill="both", expand=True, padx=18, pady=(8, 18))

        entry.focus_set()

    def choose_database(self):
        path = filedialog.askopenfilename(
            title="SQLite-Datenbank öffnen",
            filetypes=[
                ("SQLite-Datenbank", "*.db *.sqlite *.sqlite3"),
                ("Alle Dateien", "*.*"),
            ],
        )
        if path:
            self.open_database(Path(path))

    def open_database(self, path: Path):
        try:
            if self.db:
                self.db.close()

            self.db = WorkshopDatabase(path)
            self.interface_names = {
                row["id"]: row["name"]
                for row in self.db.get_lookup("interfaces")
            }
            self.db_name.set(path.name)
            self.title(f"{APP_TITLE} – {path.name}")
            self.refresh_results()

        except Exception as exc:
            messagebox.showerror(
                "Fehler",
                f"Datenbank konnte nicht geöffnet werden:\n{exc}",
            )

    def clear_search(self):
        self.search_var.set("")
        self.refresh_results()

    def refresh_results(self):
        if not self.db:
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = self.db.list_components(self.search_var.get())
        self.count_var.set(f"{len(rows)} Treffer")

        for row in rows:
            result = self.db.get_component(row["id"])
            interface_ids = result[1] if result else []

            interfaces = ", ".join(
                self.interface_names[i]
                for i in interface_ids
                if i in self.interface_names
            )

            self.tree.insert(
                "",
                tk.END,
                iid=str(row["id"]),
                values=(
                    row["name"],
                    row["category"],
                    row["manufacturer"],
                    interfaces,
                    row["quantity"],
                    "" if row["storage_row"] is None else row["storage_row"],
                    "" if row["storage_column"] is None else row["storage_column"],
                ),
            )

        self._set_details("Bauteil auswählen, um weitere Informationen anzuzeigen.")

    def show_details(self, _event=None):
        if not self.db:
            return

        selection = self.tree.selection()
        if not selection:
            return

        result = self.db.get_component(int(selection[0]))
        if not result:
            return

        component, interface_ids = result

        category = self._lookup("categories", component["category_id"]) or "–"
        manufacturer = self._lookup("manufacturers", component["manufacturer_id"]) or "–"

        interfaces = ", ".join(
            self.interface_names[i]
            for i in interface_ids
            if i in self.interface_names
        ) or "–"

        radio = ", ".join(
            label
            for label, enabled in [
                ("WiFi", component["wifi"]),
                ("BLE", component["ble"]),
                ("Matter", component["matter"]),
                ("Zigbee", component["zigbee"]),
                ("Thread", component["thread"]),
            ]
            if enabled
        ) or "–"

        position = (
            f"Reihe {component['storage_row'] if component['storage_row'] is not None else '–'}, "
            f"Spalte {component['storage_column'] if component['storage_column'] is not None else '–'}"
        )

        self._set_details(
            f"{component['name']}\n\n"
            f"Kategorie\n{category}\n\n"
            f"Hersteller\n{manufacturer}\n\n"
            f"Schnittstellen\n{interfaces}\n\n"
            f"Funkstandards\n{radio}\n\n"
            f"Bestand\n{component['quantity']}\n\n"
            f"Lagerposition\n{position}\n\n"
            f"Beschreibung\n{component['description'] or '–'}"
        )

    def _lookup(self, table, row_id):
        if row_id is None or not self.db:
            return ""
        for row in self.db.get_lookup(table):
            if row["id"] == row_id:
                return row["name"]
        return ""

    def _set_details(self, text):
        self.details.configure(state="normal")
        self.details.delete("1.0", tk.END)
        self.details.insert("1.0", text)
        self.details.configure(state="disabled")

    def destroy(self):
        if self.db:
            self.db.close()
        super().destroy()


if __name__ == "__main__":
    SearchApp().mainloop()
