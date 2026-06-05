import sqlite3
import os

DB_PATH = r"c:\Users\MERCYLYNY\Desktop\pro\construction.db"

def run_migration():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Add columns to 'walls' table
    columns_to_add_walls = [
        ("wall_type", "VARCHAR DEFAULT 'UNKNOWN'"),
        ("classification_confidence", "FLOAT DEFAULT 0.0"),
        ("reasoning", "VARCHAR DEFAULT ''")
    ]

    for col_name, col_def in columns_to_add_walls:
        try:
            cursor.execute(f"ALTER TABLE walls ADD COLUMN {col_name} {col_def}")
            print(f"Added column '{col_name}' to 'walls' table.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column '{col_name}' already exists in 'walls' table.")
            else:
                print(f"Error adding column '{col_name}' to 'walls': {e}")

    # Add columns to 'building_summaries' table
    columns_to_add_summaries = [
        ("stairs", "INTEGER DEFAULT 0")
    ]

    for col_name, col_def in columns_to_add_summaries:
        try:
            cursor.execute(f"ALTER TABLE building_summaries ADD COLUMN {col_name} {col_def}")
            print(f"Added column '{col_name}' to 'building_summaries' table.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column '{col_name}' already exists in 'building_summaries' table.")
            else:
                print(f"Error adding column '{col_name}' to 'building_summaries': {e}")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    run_migration()
