PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS manufacturers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS interfaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER,
    manufacturer_id INTEGER,
    wifi INTEGER NOT NULL DEFAULT 0 CHECK (wifi IN (0, 1)),
    ble INTEGER NOT NULL DEFAULT 0 CHECK (ble IN (0, 1)),
    matter INTEGER NOT NULL DEFAULT 0 CHECK (matter IN (0, 1)),
    zigbee INTEGER NOT NULL DEFAULT 0 CHECK (zigbee IN (0, 1)),
    thread INTEGER NOT NULL DEFAULT 0 CHECK (thread IN (0, 1)),
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    storage_row INTEGER CHECK (storage_row IS NULL OR storage_row >= 0),
    storage_column INTEGER CHECK (storage_column IS NULL OR storage_column >= 0),
    description TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS component_interfaces (
    component_id INTEGER NOT NULL,
    interface_id INTEGER NOT NULL,
    PRIMARY KEY (component_id, interface_id),
    FOREIGN KEY (component_id) REFERENCES components(id) ON DELETE CASCADE,
    FOREIGN KEY (interface_id) REFERENCES interfaces(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_components_name ON components(name);
CREATE INDEX IF NOT EXISTS idx_components_category ON components(category_id);
CREATE INDEX IF NOT EXISTS idx_components_manufacturer ON components(manufacturer_id);
