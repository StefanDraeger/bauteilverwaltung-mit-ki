from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from database import WorkshopDatabase


APP_TITLE = "Smarte Elektronik-Werkstatt"
DEFAULT_DB = Path(__file__).with_name("workshop.db")

COLORS = {
    "window": "#f5f7fb",
    "sidebar": "#ffffff",
    "surface": "#ffffff",
    "surface_alt": "#f8fafc",
    "border": "#e5e7eb",
    "border_strong": "#d1d5db",
    "text": "#111827",
    "muted": "#6b7280",
    "accent": "#2563eb",
    "accent_hover": "#1d4ed8",
    "accent_soft": "#eff6ff",
    "danger": "#dc2626",
    "danger_soft": "#fef2f2",
    "success": "#059669",
}


class WorkshopApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("1260x760")
        self.minsize(1080, 660)
        self.configure(bg=COLORS["window"])

        self.db: WorkshopDatabase | None = None
        self.current_component_id: int | None = None

        self.category_map: dict[str, int] = {}
        self.manufacturer_map: dict[str, int] = {}
        self.interface_rows = []

        self.active_view = "components"

        self._configure_styles()
        self._build_window()
        self.open_database(DEFAULT_DB, seed=True)

    # ------------------------------------------------------------------
    # Style
    # ------------------------------------------------------------------

    def _configure_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            ".",
            font=("Segoe UI", 10),
            background=COLORS["surface"],
            foreground=COLORS["text"],
        )

        style.configure(
            "Treeview",
            background=COLORS["surface"],
            fieldbackground=COLORS["surface"],
            foreground=COLORS["text"],
            borderwidth=0,
            relief="flat",
            rowheight=38,
            font=("Segoe UI", 10),
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["accent_soft"])],
            foreground=[("selected", COLORS["text"])],
        )

        style.configure(
            "Treeview.Heading",
            background=COLORS["surface_alt"],
            foreground=COLORS["muted"],
            borderwidth=0,
            relief="flat",
            padding=(10, 10),
            font=("Segoe UI Semibold", 9),
        )
        style.map(
            "Treeview.Heading",
            background=[("active", "#f1f5f9")],
        )

        style.configure(
            "TCombobox",
            fieldbackground=COLORS["surface"],
            foreground=COLORS["text"],
            bordercolor=COLORS["border_strong"],
            lightcolor=COLORS["border_strong"],
            darkcolor=COLORS["border_strong"],
            arrowcolor=COLORS["muted"],
            padding=8,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", COLORS["surface"])],
            foreground=[("readonly", COLORS["text"])],
            selectbackground=[("readonly", COLORS["surface"])],
            selectforeground=[("readonly", COLORS["text"])],
        )

        style.configure(
            "TSpinbox",
            fieldbackground=COLORS["surface"],
            foreground=COLORS["text"],
            bordercolor=COLORS["border_strong"],
            lightcolor=COLORS["border_strong"],
            darkcolor=COLORS["border_strong"],
            arrowcolor=COLORS["muted"],
            padding=7,
        )

        style.configure(
            "TScrollbar",
            background=COLORS["surface_alt"],
            troughcolor=COLORS["surface"],
            bordercolor=COLORS["surface"],
            arrowcolor=COLORS["muted"],
        )

    # ------------------------------------------------------------------
    # Shell
    # ------------------------------------------------------------------

    def _build_window(self):
        self.sidebar = tk.Frame(
            self,
            bg=COLORS["sidebar"],
            width=210,
            highlightbackground=COLORS["border"],
            highlightthickness=0,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        divider = tk.Frame(self, bg=COLORS["border"], width=1)
        divider.pack(side="left", fill="y")

        self.content = tk.Frame(self, bg=COLORS["window"])
        self.content.pack(side="left", fill="both", expand=True)

        self._build_sidebar()
        self._show_components_view()

    def _build_sidebar(self):
        logo = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        logo.pack(fill="x", padx=20, pady=(24, 24))

        mark = tk.Canvas(
            logo,
            width=34,
            height=34,
            bg=COLORS["sidebar"],
            highlightthickness=0,
        )
        mark.pack(side="left")
        mark.create_rectangle(
            4, 4, 30, 30,
            outline=COLORS["accent"],
            width=2,
        )
        mark.create_line(10, 17, 24, 17, fill=COLORS["accent"], width=2)
        mark.create_line(17, 10, 17, 24, fill=COLORS["accent"], width=2)

        title = tk.Frame(logo, bg=COLORS["sidebar"])
        title.pack(side="left", padx=(10, 0))

        tk.Label(
            title,
            text="Smarte Elektronik-",
            bg=COLORS["sidebar"],
            fg=COLORS["text"],
            font=("Segoe UI Semibold", 10),
            anchor="w",
        ).pack(anchor="w")
        tk.Label(
            title,
            text="Werkstatt",
            bg=COLORS["sidebar"],
            fg=COLORS["text"],
            font=("Segoe UI Semibold", 10),
            anchor="w",
        ).pack(anchor="w")

        self.nav_buttons: dict[str, tk.Button] = {}

        self._nav_button("components", "Bauteile", self._show_components_view)
        self._nav_button("categories", "Kategorien", lambda: self._show_master_view("categories"))
        self._nav_button("manufacturers", "Hersteller", lambda: self._show_master_view("manufacturers"))
        self._nav_button("interfaces", "Schnittstellen", lambda: self._show_master_view("interfaces"))

        spacer = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        spacer.pack(fill="both", expand=True)

        db_block = tk.Frame(
            self.sidebar,
            bg=COLORS["surface_alt"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        db_block.pack(fill="x", padx=14, pady=14)

        tk.Label(
            db_block,
            text="DATENBANK",
            bg=COLORS["surface_alt"],
            fg=COLORS["muted"],
            font=("Segoe UI Semibold", 8),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(10, 2))

        self.db_name_var = tk.StringVar(value="workshop.db")
        tk.Label(
            db_block,
            textvariable=self.db_name_var,
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(fill="x", padx=12)

        tk.Button(
            db_block,
            text="Andere Datenbank öffnen",
            command=self.choose_database,
            bg=COLORS["surface_alt"],
            fg=COLORS["accent"],
            activebackground=COLORS["accent_soft"],
            activeforeground=COLORS["accent_hover"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI Semibold", 9),
            anchor="w",
            padx=12,
        ).pack(fill="x", pady=(6, 10))

    def _nav_button(self, key: str, text: str, command):
        button = tk.Button(
            self.sidebar,
            text=text,
            command=command,
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            activebackground=COLORS["accent_soft"],
            activeforeground=COLORS["accent"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI Semibold", 10),
            anchor="w",
            padx=20,
            pady=11,
        )
        button.pack(fill="x", padx=10, pady=2)
        self.nav_buttons[key] = button

    def _set_active_nav(self, key: str):
        self.active_view = key
        for nav_key, button in self.nav_buttons.items():
            if nav_key == key:
                button.configure(
                    bg=COLORS["accent_soft"],
                    fg=COLORS["accent"],
                )
            else:
                button.configure(
                    bg=COLORS["sidebar"],
                    fg=COLORS["muted"],
                )

    def _clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    # ------------------------------------------------------------------
    # Components view
    # ------------------------------------------------------------------

    def _show_components_view(self):
        self._clear_content()
        self._set_active_nav("components")

        page = tk.Frame(self.content, bg=COLORS["window"])
        page.pack(fill="both", expand=True, padx=28, pady=24)

        self._build_components_header(page)
        self._build_components_body(page)

        if self.db:
            self.refresh_lookups()
            self.refresh_components()

    def _build_components_header(self, parent):
        header = tk.Frame(parent, bg=COLORS["window"])
        header.pack(fill="x", pady=(0, 18))

        title = tk.Frame(header, bg=COLORS["window"])
        title.pack(side="left", fill="x", expand=True)

        tk.Label(
            title,
            text="Bauteile",
            bg=COLORS["window"],
            fg=COLORS["text"],
            font=("Segoe UI Semibold", 22),
            anchor="w",
        ).pack(anchor="w")

        tk.Label(
            title,
            text="Elektronik-Komponenten erfassen, durchsuchen und verwalten.",
            bg=COLORS["window"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10),
            anchor="w",
        ).pack(anchor="w", pady=(3, 0))

        self._primary_button(
            header,
            "+  Neues Bauteil",
            self.open_new_component_editor,
        ).pack(side="right", padx=(10, 0))

        self._secondary_button(
            header,
            "Neue Datenbank",
            self.create_database,
        ).pack(side="right")

    def _build_components_body(self, parent):
        card = tk.Frame(
            parent,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        card.pack(fill="both", expand=True)

        toolbar = tk.Frame(card, bg=COLORS["surface"])
        toolbar.pack(fill="x", padx=16, pady=16)

        search_frame = tk.Frame(
            toolbar,
            bg=COLORS["surface_alt"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        search_frame.pack(side="left", fill="x", expand=True)

        tk.Label(
            search_frame,
            text="Suche",
            bg=COLORS["surface_alt"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
        ).pack(side="left", padx=(12, 8))

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            bd=0,
            font=("Segoe UI", 10),
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=9)
        search_entry.bind("<KeyRelease>", lambda _event: self.refresh_components())

        clear = tk.Button(
            search_frame,
            text="×",
            command=self.clear_search,
            bg=COLORS["surface_alt"],
            fg=COLORS["muted"],
            activebackground=COLORS["surface_alt"],
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI Semibold", 12),
        )
        clear.pack(side="right", padx=(0, 8))

        self.count_var = tk.StringVar(value="0 Einträge")
        tk.Label(
            toolbar,
            textvariable=self.count_var,
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
        ).pack(side="right", padx=(14, 0))

        table_frame = tk.Frame(card, bg=COLORS["surface"])
        table_frame.pack(fill="both", expand=True, padx=1, pady=(0, 1))

        columns = (
            "name",
            "category",
            "manufacturer",
            "interfaces",
            "quantity",
            "row",
            "column",
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

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
            "name": 200,
            "category": 130,
            "manufacturer": 140,
            "interfaces": 200,
            "quantity": 80,
            "row": 70,
            "column": 70,
        }

        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="w")

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda _event: self.open_selected_component_editor())
        self.tree.bind("<Return>", lambda _event: self.open_selected_component_editor())

        footer = tk.Frame(card, bg=COLORS["surface_alt"])
        footer.pack(fill="x")

        tk.Label(
            footer,
            text="Tipp: Doppelklick auf ein Bauteil zum Bearbeiten.",
            bg=COLORS["surface_alt"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
        ).pack(side="left", padx=14, pady=9)

        self._text_button(
            footer,
            "Bearbeiten",
            self.open_selected_component_editor,
            COLORS["accent"],
        ).pack(side="right", padx=(0, 8))

        self._text_button(
            footer,
            "Löschen",
            self.delete_selected_component,
            COLORS["danger"],
        ).pack(side="right", padx=(0, 6))

    def refresh_components(self):
        if not self.db or not hasattr(self, "tree"):
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = self.db.list_components(self.search_var.get())
        self.count_var.set(f"{len(rows)} Einträge")

        for row in rows:
            interfaces = self._component_interfaces_text(row["id"])

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

    def _component_interfaces_text(self, component_id: int) -> str:
        if not self.db:
            return ""

        result = self.db.get_component(component_id)
        if not result:
            return ""

        _, interface_ids = result
        interface_names = {
            row["id"]: row["name"]
            for row in self.db.get_lookup("interfaces")
        }

        return ", ".join(
            interface_names[interface_id]
            for interface_id in interface_ids
            if interface_id in interface_names
        )

    def clear_search(self):
        self.search_var.set("")
        self.refresh_components()

    def _selected_component_id(self) -> int | None:
        if not hasattr(self, "tree"):
            return None

        selected = self.tree.selection()
        if not selected:
            return None

        return int(selected[0])

    def open_new_component_editor(self):
        self._open_component_editor(None)

    def open_selected_component_editor(self):
        component_id = self._selected_component_id()
        if component_id is None:
            messagebox.showinfo("Bauteil bearbeiten", "Bitte zuerst ein Bauteil auswählen.")
            return

        self._open_component_editor(component_id)

    def _open_component_editor(self, component_id: int | None):
        if not self.db:
            return

        dialog = tk.Toplevel(self)
        dialog.title("Neues Bauteil" if component_id is None else "Bauteil bearbeiten")
        dialog.geometry("720x780")
        dialog.minsize(660, 700)
        dialog.configure(bg=COLORS["surface"])
        dialog.transient(self)
        dialog.grab_set()

        outer = tk.Frame(dialog, bg=COLORS["surface"])
        outer.pack(fill="both", expand=True)

        top = tk.Frame(outer, bg=COLORS["surface"])
        top.pack(fill="x", padx=26, pady=(24, 16))

        tk.Label(
            top,
            text="Neues Bauteil" if component_id is None else "Bauteil bearbeiten",
            bg=COLORS["surface"],
            fg=COLORS["text"],
            font=("Segoe UI Semibold", 18),
            anchor="w",
        ).pack(anchor="w")

        tk.Label(
            top,
            text="Technische Daten und Lagerposition zentral pflegen.",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(anchor="w", pady=(3, 0))

        separator = tk.Frame(outer, bg=COLORS["border"], height=1)
        separator.pack(fill="x")

        canvas = tk.Canvas(
            outer,
            bg=COLORS["surface"],
            highlightthickness=0,
            bd=0,
        )
        scroll = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        form = tk.Frame(canvas, bg=COLORS["surface"])

        form_window = canvas.create_window((0, 0), window=form, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)

        def update_scroll(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(form_window, width=canvas.winfo_width())

        form.bind("<Configure>", update_scroll)
        canvas.bind("<Configure>", update_scroll)

        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        inner = tk.Frame(form, bg=COLORS["surface"])
        inner.pack(fill="both", expand=True, padx=26, pady=20)
        inner.grid_columnconfigure(0, weight=1)
        inner.grid_columnconfigure(1, weight=1)

        name_var = tk.StringVar()
        category_var = tk.StringVar()
        manufacturer_var = tk.StringVar()
        quantity_var = tk.StringVar(value="0")
        row_var = tk.StringVar()
        column_var = tk.StringVar()

        wifi_var = tk.BooleanVar()
        ble_var = tk.BooleanVar()
        matter_var = tk.BooleanVar()
        zigbee_var = tk.BooleanVar()
        thread_var = tk.BooleanVar()

        # Name
        self._form_label(inner, "Name", 0, 0, columnspan=2)
        name_entry = self._entry(inner, name_var)
        name_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 14))

        # Category / manufacturer
        self._form_label(inner, "Kategorie", 2, 0)
        self._form_label(inner, "Hersteller", 2, 1)

        category_combo = ttk.Combobox(
            inner,
            textvariable=category_var,
            state="readonly",
            values=[""] + list(self.category_map.keys()),
        )
        category_combo.grid(row=3, column=0, sticky="ew", padx=(0, 7), pady=(4, 14))

        manufacturer_combo = ttk.Combobox(
            inner,
            textvariable=manufacturer_var,
            state="readonly",
            values=[""] + list(self.manufacturer_map.keys()),
        )
        manufacturer_combo.grid(row=3, column=1, sticky="ew", padx=(7, 0), pady=(4, 14))

        # Interfaces
        self._form_label(inner, "Schnittstellen", 4, 0, columnspan=2)

        interface_box = tk.Frame(
            inner,
            bg=COLORS["surface_alt"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        interface_box.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(4, 14))

        interface_list = tk.Listbox(
            interface_box,
            selectmode=tk.MULTIPLE,
            exportselection=False,
            height=5,
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            selectbackground=COLORS["accent_soft"],
            selectforeground=COLORS["accent"],
            activestyle="none",
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 10),
        )
        interface_list.pack(fill="both", expand=True, padx=10, pady=8)

        for row in self.interface_rows:
            interface_list.insert(tk.END, row["name"])

        # Radio standards
        self._form_label(inner, "Funkstandards", 6, 0, columnspan=2)

        radio_box = tk.Frame(inner, bg=COLORS["surface"])
        radio_box.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(4, 14))

        for label, variable in [
            ("WiFi", wifi_var),
            ("BLE", ble_var),
            ("Matter", matter_var),
            ("Zigbee", zigbee_var),
            ("Thread", thread_var),
        ]:
            tk.Checkbutton(
                radio_box,
                text=label,
                variable=variable,
                bg=COLORS["surface"],
                fg=COLORS["text"],
                activebackground=COLORS["surface"],
                activeforeground=COLORS["text"],
                selectcolor=COLORS["surface"],
                highlightthickness=0,
                bd=0,
                font=("Segoe UI", 10),
            ).pack(side="left", padx=(0, 14))

        # Inventory
        self._form_label(inner, "Bestand", 8, 0, columnspan=2)

        quantity_spin = ttk.Spinbox(inner, from_=0, to=100000, textvariable=quantity_var)
        quantity_spin.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(4, 14))

        # Storage position
        self._form_label(inner, "Lagerposition", 10, 0, columnspan=2)

        position_frame = tk.Frame(inner, bg=COLORS["surface"])
        position_frame.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(4, 14))
        position_frame.grid_columnconfigure(0, weight=1)
        position_frame.grid_columnconfigure(1, weight=1)

        row_box = tk.Frame(position_frame, bg=COLORS["surface"])
        row_box.grid(row=0, column=0, sticky="ew", padx=(0, 7))
        tk.Label(
            row_box,
            text="Reihe",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(fill="x", pady=(0, 4))
        row_spin = ttk.Spinbox(row_box, from_=0, to=1000, textvariable=row_var)
        row_spin.pack(fill="x")

        column_box = tk.Frame(position_frame, bg=COLORS["surface"])
        column_box.grid(row=0, column=1, sticky="ew", padx=(7, 0))
        tk.Label(
            column_box,
            text="Spalte",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(fill="x", pady=(0, 4))
        column_spin = ttk.Spinbox(column_box, from_=0, to=1000, textvariable=column_var)
        column_spin.pack(fill="x")

        # Description
        self._form_label(inner, "Beschreibung", 12, 0, columnspan=2)

        description_box = tk.Frame(
            inner,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border_strong"],
            highlightthickness=1,
        )
        description_box.grid(row=13, column=0, columnspan=2, sticky="nsew", pady=(4, 18))

        description = tk.Text(
            description_box,
            height=5,
            wrap="word",
            bg=COLORS["surface"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 10),
        )
        description.pack(fill="both", expand=True, padx=9, pady=8)

        selected_interface_ids: list[int] = []

        if component_id is not None:
            result = self.db.get_component(component_id)
            if result:
                component, selected_interface_ids = result
                name_var.set(component["name"])
                category_var.set(self._lookup_name("categories", component["category_id"]))
                manufacturer_var.set(self._lookup_name("manufacturers", component["manufacturer_id"]))
                quantity_var.set(str(component["quantity"]))
                row_var.set("" if component["storage_row"] is None else str(component["storage_row"]))
                column_var.set("" if component["storage_column"] is None else str(component["storage_column"]))

                wifi_var.set(bool(component["wifi"]))
                ble_var.set(bool(component["ble"]))
                matter_var.set(bool(component["matter"]))
                zigbee_var.set(bool(component["zigbee"]))
                thread_var.set(bool(component["thread"]))

                description.insert("1.0", component["description"] or "")

                selected = set(selected_interface_ids)
                for index, interface_row in enumerate(self.interface_rows):
                    if interface_row["id"] in selected:
                        interface_list.selection_set(index)

        button_bar = tk.Frame(outer, bg=COLORS["surface_alt"])
        button_bar.pack(fill="x", side="bottom")

        self._secondary_button(
            button_bar,
            "Abbrechen",
            dialog.destroy,
        ).pack(side="right", padx=(8, 22), pady=14)

        def save():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning(
                    "Fehlender Name",
                    "Bitte einen Namen für das Bauteil eingeben.",
                    parent=dialog,
                )
                return

            try:
                quantity = int(quantity_var.get())
                if quantity < 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning(
                    "Ungültiger Bestand",
                    "Der Bestand muss eine positive ganze Zahl sein.",
                    parent=dialog,
                )
                return

            try:
                storage_row = int(row_var.get()) if row_var.get().strip() else None
                storage_column = int(column_var.get()) if column_var.get().strip() else None
                if storage_row is not None and storage_row < 0:
                    raise ValueError
                if storage_column is not None and storage_column < 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning(
                    "Ungültige Lagerposition",
                    "Reihe und Spalte müssen positive ganze Zahlen oder leer sein.",
                    parent=dialog,
                )
                return

            interface_ids = [
                self.interface_rows[index]["id"]
                for index in interface_list.curselection()
            ]

            data = {
                "name": name,
                "category_id": self.category_map.get(category_var.get()),
                "manufacturer_id": self.manufacturer_map.get(manufacturer_var.get()),
                "wifi": wifi_var.get(),
                "ble": ble_var.get(),
                "matter": matter_var.get(),
                "zigbee": zigbee_var.get(),
                "thread": thread_var.get(),
                "quantity": quantity,
                "storage_row": storage_row,
                "storage_column": storage_column,
                "description": description.get("1.0", tk.END).strip(),
            }

            try:
                self.db.save_component(data, interface_ids, component_id)
                dialog.destroy()
                self.refresh_components()
            except Exception as exc:
                messagebox.showerror(
                    "Fehler",
                    f"Bauteil konnte nicht gespeichert werden:\n{exc}",
                    parent=dialog,
                )

        self._primary_button(
            button_bar,
            "Speichern",
            save,
        ).pack(side="right", pady=14)

        dialog.after(100, name_entry.focus_set)

    def delete_selected_component(self):
        component_id = self._selected_component_id()
        if component_id is None or not self.db:
            messagebox.showinfo("Bauteil löschen", "Bitte zuerst ein Bauteil auswählen.")
            return

        result = self.db.get_component(component_id)
        if not result:
            return

        component, _ = result
        name = component["name"]

        if not messagebox.askyesno(
            "Bauteil löschen",
            f"'{name}' wirklich löschen?",
        ):
            return

        self.db.delete_component(component_id)
        self.refresh_components()

    # ------------------------------------------------------------------
    # Master data views
    # ------------------------------------------------------------------

    def _show_master_view(self, table: str):
        self._clear_content()
        self._set_active_nav(table)

        names = {
            "categories": ("Kategorien", "Bauteile in übersichtliche Gruppen einordnen."),
            "manufacturers": ("Hersteller", "Hersteller zentral verwalten und einheitlich verwenden."),
            "interfaces": ("Schnittstellen", "Verfügbare Schnittstellen für Bauteile definieren."),
        }

        title, subtitle = names[table]

        page = tk.Frame(self.content, bg=COLORS["window"])
        page.pack(fill="both", expand=True, padx=28, pady=24)

        header = tk.Frame(page, bg=COLORS["window"])
        header.pack(fill="x", pady=(0, 18))

        tk.Label(
            header,
            text=title,
            bg=COLORS["window"],
            fg=COLORS["text"],
            font=("Segoe UI Semibold", 22),
            anchor="w",
        ).pack(anchor="w")

        tk.Label(
            header,
            text=subtitle,
            bg=COLORS["window"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10),
            anchor="w",
        ).pack(anchor="w", pady=(3, 0))

        card = tk.Frame(
            page,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        card.pack(fill="both", expand=True)

        form = tk.Frame(card, bg=COLORS["surface"])
        form.pack(fill="x", padx=18, pady=18)

        entry_var = tk.StringVar()

        entry_shell = tk.Frame(
            form,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border_strong"],
            highlightthickness=1,
        )
        entry_shell.pack(side="left", fill="x", expand=True)

        entry = tk.Entry(
            entry_shell,
            textvariable=entry_var,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            bd=0,
            font=("Segoe UI", 10),
        )
        entry.pack(fill="x", padx=10, pady=10)

        listbox = tk.Listbox(
            card,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            selectbackground=COLORS["accent_soft"],
            selectforeground=COLORS["accent"],
            activestyle="none",
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 10),
        )
        listbox.pack(fill="both", expand=True, padx=18, pady=(0, 14))

        rows = list(self.db.get_lookup(table)) if self.db else []
        for row in rows:
            listbox.insert(tk.END, row["name"])

        def add():
            if not self.db:
                return

            name = entry_var.get().strip()
            if not name:
                return

            try:
                self.db.add_lookup(table, name)
                entry_var.set("")
                self.refresh_lookups()
                self._show_master_view(table)
            except Exception as exc:
                messagebox.showerror("Fehler", f"Eintrag konnte nicht angelegt werden:\n{exc}")

        def delete():
            if not self.db:
                return

            selection = listbox.curselection()
            if not selection:
                return

            row = rows[selection[0]]

            if not messagebox.askyesno(
                "Eintrag löschen",
                f"'{row['name']}' wirklich löschen?",
            ):
                return

            try:
                self.db.delete_lookup(table, row["id"])
                self.refresh_lookups()
                self._show_master_view(table)
            except Exception as exc:
                messagebox.showerror("Fehler", f"Eintrag konnte nicht gelöscht werden:\n{exc}")

        self._primary_button(form, "Hinzufügen", add).pack(side="left", padx=(10, 0))
        entry.bind("<Return>", lambda _event: add())

        footer = tk.Frame(card, bg=COLORS["surface_alt"])
        footer.pack(fill="x", side="bottom")

        self._text_button(
            footer,
            "Ausgewählten Eintrag löschen",
            delete,
            COLORS["danger"],
        ).pack(side="right", padx=12, pady=9)

        entry.focus_set()

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    def open_database(self, path: Path, seed: bool = False):
        try:
            if self.db:
                self.db.close()

            self.db = WorkshopDatabase(path)

            if seed:
                self.db.seed_defaults()

            self.db_name_var.set(path.name)
            self.title(f"{APP_TITLE} – {path.name}")

            self.refresh_lookups()

            if self.active_view == "components":
                self.refresh_components()
            else:
                self._show_master_view(self.active_view)

        except Exception as exc:
            messagebox.showerror(
                "Datenbank konnte nicht geöffnet werden",
                str(exc),
            )

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

    def create_database(self):
        path = filedialog.asksaveasfilename(
            title="Neue SQLite-Datenbank",
            defaultextension=".db",
            filetypes=[("SQLite-Datenbank", "*.db")],
        )
        if path:
            self.open_database(Path(path), seed=True)

    def refresh_lookups(self):
        if not self.db:
            return

        categories = self.db.get_lookup("categories")
        manufacturers = self.db.get_lookup("manufacturers")
        self.interface_rows = list(self.db.get_lookup("interfaces"))

        self.category_map = {row["name"]: row["id"] for row in categories}
        self.manufacturer_map = {row["name"]: row["id"] for row in manufacturers}

    def _lookup_name(self, table: str, row_id):
        if row_id is None or not self.db:
            return ""

        for row in self.db.get_lookup(table):
            if row["id"] == row_id:
                return row["name"]

        return ""

    # ------------------------------------------------------------------
    # Generic widgets
    # ------------------------------------------------------------------

    def _primary_button(self, parent, text: str, command):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=COLORS["accent"],
            fg="#ffffff",
            activebackground=COLORS["accent_hover"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI Semibold", 9),
            padx=16,
            pady=9,
        )
        return button

    def _secondary_button(self, parent, text: str, command):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            activebackground=COLORS["surface_alt"],
            activeforeground=COLORS["text"],
            highlightbackground=COLORS["border_strong"],
            highlightthickness=1,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI Semibold", 9),
            padx=14,
            pady=8,
        )
        return button

    def _text_button(self, parent, text: str, command, color: str):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=COLORS["surface_alt"],
            fg=color,
            activebackground=COLORS["surface_alt"],
            activeforeground=color,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI Semibold", 9),
            padx=8,
            pady=7,
        )
        return button

    def _form_label(self, parent, text: str, row: int, column: int, columnspan: int = 1):
        label = tk.Label(
            parent,
            text=text,
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Segoe UI Semibold", 9),
            anchor="w",
        )
        label.grid(
            row=row,
            column=column,
            columnspan=columnspan,
            sticky="w",
            padx=(0, 7 if column == 0 else 0),
        )

    def _entry(self, parent, variable):
        shell = tk.Frame(
            parent,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border_strong"],
            highlightthickness=1,
        )

        entry = tk.Entry(
            shell,
            textvariable=variable,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            bd=0,
            font=("Segoe UI", 10),
        )
        entry.pack(fill="x", padx=9, pady=8)

        # Return the entry while preserving the wrapper grid API.
        class EntryProxy:
            def grid(self, **kwargs):
                shell.grid(**kwargs)
            def focus_set(self):
                entry.focus_set()

        return EntryProxy()

    def destroy(self):
        if self.db:
            self.db.close()
        super().destroy()


if __name__ == "__main__":
    app = WorkshopApp()
    app.mainloop()
