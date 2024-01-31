import sqlite3


class DatabaseHelper:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    selection_status INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def add_message(self, content):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (content) VALUES (?)
            ''', (content,))
            conn.commit()

    def get_random_message(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, content
                FROM messages
                WHERE selection_status = 1
                ORDER BY RANDOM()
                LIMIT 1;
            ''')
            selected_new_message = cursor.fetchone()

            if selected_new_message:
                # If a message with selection_status 1 is found, update its status to -1
                self.update_selection_status(-1, selected_new_message[0])
                return selected_new_message
            else:
                cursor.execute('''
                                SELECT id, content
                                FROM messages
                                WHERE selection_status = 0
                                ORDER BY RANDOM()
                                LIMIT 1;
                            ''')
                selected_old_message = cursor.fetchone()
                if selected_old_message:
                    self.update_selection_status(-1, selected_old_message[0])
                    return selected_old_message

            # If no message with selection_status 1/0 is found, reset all selection_status to 0
            cursor.execute('''
                    UPDATE messages
                    SET selection_status = 0;
                ''')
            conn.commit()

            # Retry the selection
            cursor.execute('''
                    SELECT id, content
                    FROM messages
                    WHERE selection_status = 0
                    ORDER BY RANDOM()
                    LIMIT 1;
                ''')
            selected_message = cursor.fetchone()

            if selected_message:
                # If a message is found, update its status to -1
                self.update_selection_status(-1, selected_message[0])
                return selected_message

            # If still no message is found, return None
            return None

    def update_selection_status(self, selection_status, message_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE messages
                SET selection_status = ?
                WHERE id = ?
            ''', (selection_status, message_id,))
            conn.commit()

    def get_all_messages(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, content, selection_status, created_at
                FROM messages
            ''')
            return cursor.fetchall()

    def execute_schema(self, query):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                            ?
                        ''', (query,))
            conn.commit()

    def delete_message_by_id(self, message_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE id=?", (message_id,))
            conn.commit()

    def delete_all_messages(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages")
            conn.commit()


# Example usage
if __name__ == "__main__":
    # Initialize the DatabaseHelper with the path to your SQLite database file
    db_helper = DatabaseHelper("messages.db")

    db_helper.add_message("Welcome!")
    random_message = db_helper.get_random_message()
    print("Random Message:", random_message)

    db_helper.delete_message_by_id(1)

    # Get all messages
    all_messages = db_helper.get_all_messages()
    print("All Messages:", all_messages)

    db_helper.delete_all_messages()
