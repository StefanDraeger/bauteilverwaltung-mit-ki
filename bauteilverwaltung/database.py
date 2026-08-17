from __future__ import annotations

import sqlite3
from pathlib import Path


class WorkshopDatabase:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self._initialize_schema()

    def _initialize_schema(self):
        schema_path = Path(__file__).with_name("schema.sql")
        self.connection.executescript(schema_path.read_text(encoding="utf-8"))
        self.connection.commit()

    def close(self):
        self.connection.close()

    def seed_defaults(self):
        defaults = {
            "categories": [
                "Mikrocontroller",
                "Sensor",
                "Display",
                "Aktor",
                "LED",
                "Modul",
                "Sonstiges",
            ],
            "manufacturers": [
                "Espressif",
                "Seeed Studio",
                "Adafruit",
                "Waveshare",
                "Bosch",
                "Shelly",
            ],
            "interfaces": [
                "GPIO",
                "I2C",
                "SPI",
                "UART",
                "Analog",
                "1-Wire",
                "USB",
                "CAN",
            ],
        }

        for table, values in defaults.items():
            for value in values:
                self.connection.execute(
                    f"INSERT OR IGNORE INTO {table} (name) VALUES (?)",
                    (value,),
                )
        self.connection.commit()

    def get_lookup(self, table: str):
        if table not in {"categories", "manufacturers", "interfaces"}:
            raise ValueError("Ungültige Stammdatentabelle")
        return self.connection.execute(
            f"SELECT id, name FROM {table} ORDER BY name COLLATE NOCASE"
        ).fetchall()

    def add_lookup(self, table: str, name: str):
        if table not in {"categories", "manufacturers", "interfaces"}:
            raise ValueError("Ungültige Stammdatentabelle")
        name = name.strip()
        if not name:
            raise ValueError("Name darf nicht leer sein.")
        self.connection.execute(
            f"INSERT INTO {table} (name) VALUES (?)",
            (name,),
        )
        self.connection.commit()

    def delete_lookup(self, table: str, row_id: int):
        if table not in {"categories", "manufacturers", "interfaces"}:
            raise ValueError("Ungültige Stammdatentabelle")
        self.connection.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
        self.connection.commit()

    def list_components(self, search: str = ""):
        search = search.strip()
        sql = """
            SELECT
                c.id,
                c.name,
                COALESCE(cat.name, '') AS category,
                COALESCE(m.name, '') AS manufacturer,
                c.quantity,
                c.storage_row,
                c.storage_column,
                c.wifi,
                c.ble,
                c.matter,
                c.zigbee,
                c.thread
            FROM components c
            LEFT JOIN categories cat ON cat.id = c.category_id
            LEFT JOIN manufacturers m ON m.id = c.manufacturer_id
        """
        params = []
        if search:
            sql += """
                WHERE
                    c.name LIKE ?
                    OR COALESCE(cat.name, '') LIKE ?
                    OR COALESCE(m.name, '') LIKE ?
                    OR CAST(COALESCE(c.storage_row, '') AS TEXT) LIKE ?
                    OR CAST(COALESCE(c.storage_column, '') AS TEXT) LIKE ?
                    OR COALESCE(c.description, '') LIKE ?
                    OR EXISTS (
                        SELECT 1
                        FROM component_interfaces ci
                        JOIN interfaces i ON i.id = ci.interface_id
                        WHERE ci.component_id = c.id
                          AND i.name LIKE ?
                    )
            """
            pattern = f"%{search}%"
            params = [pattern] * 7
        sql += " ORDER BY c.name COLLATE NOCASE"
        return self.connection.execute(sql, params).fetchall()

    def get_component(self, component_id: int):
        component = self.connection.execute(
            "SELECT * FROM components WHERE id = ?",
            (component_id,),
        ).fetchone()

        if not component:
            return None

        interface_ids = [
            row["interface_id"]
            for row in self.connection.execute(
                "SELECT interface_id FROM component_interfaces WHERE component_id = ?",
                (component_id,),
            ).fetchall()
        ]

        return component, interface_ids

    def save_component(self, data: dict, interface_ids: list[int], component_id: int | None = None):
        values = (
            data["name"].strip(),
            data.get("category_id"),
            data.get("manufacturer_id"),
            int(bool(data.get("wifi"))),
            int(bool(data.get("ble"))),
            int(bool(data.get("matter"))),
            int(bool(data.get("zigbee"))),
            int(bool(data.get("thread"))),
            int(data.get("quantity", 0)),
            data.get("storage_row"),
            data.get("storage_column"),
            data.get("description", "").strip(),
        )

        if not values[0]:
            raise ValueError("Der Name des Bauteils darf nicht leer sein.")
        if values[8] < 0:
            raise ValueError("Die Anzahl darf nicht negativ sein.")

        with self.connection:
            if component_id is None:
                cursor = self.connection.execute(
                    """
                    INSERT INTO components (
                        name, category_id, manufacturer_id,
                        wifi, ble, matter, zigbee, thread,
                        quantity, storage_row, storage_column, description
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    values,
                )
                component_id = cursor.lastrowid
            else:
                self.connection.execute(
                    """
                    UPDATE components SET
                        name = ?,
                        category_id = ?,
                        manufacturer_id = ?,
                        wifi = ?,
                        ble = ?,
                        matter = ?,
                        zigbee = ?,
                        thread = ?,
                        quantity = ?,
                        storage_row = ?,
                        storage_column = ?,
                        description = ?
                    WHERE id = ?
                    """,
                    values + (component_id,),
                )
                self.connection.execute(
                    "DELETE FROM component_interfaces WHERE component_id = ?",
                    (component_id,),
                )

            for interface_id in interface_ids:
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO component_interfaces (component_id, interface_id)
                    VALUES (?, ?)
                    """,
                    (component_id, interface_id),
                )

        return component_id

    def delete_component(self, component_id: int):
        with self.connection:
            self.connection.execute(
                "DELETE FROM components WHERE id = ?",
                (component_id,),
            )
