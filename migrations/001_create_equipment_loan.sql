-- Migration: create equipment_loan table
CREATE TABLE IF NOT EXISTS equipment_loan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER,
    requester_id INTEGER,
    requester_dept VARCHAR(120),
    start_date DATETIME,
    end_date DATETIME,
    status VARCHAR(64),
    approved_by INTEGER,
    approved_date DATETIME,
    borrowed_date DATETIME,
    returned_date DATETIME,
    notes TEXT,
    pickup_notified BOOLEAN DEFAULT 0,
    created_date DATETIME,
    updated_date DATETIME
);

-- Optional foreign keys (SQLite enforces if PRAGMA foreign_keys=ON)
-- ALTER TABLE equipment_loan ADD FOREIGN KEY (equipment_id) REFERENCES equipment(id);
-- ALTER TABLE equipment_loan ADD FOREIGN KEY (requester_id) REFERENCES user(id);
-- ALTER TABLE equipment_loan ADD FOREIGN KEY (approved_by) REFERENCES user(id);
