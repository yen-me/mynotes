from flask import Flask, render_template, request, redirect, jsonify
import psycopg2
from datetime import timedelta

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="mynotes",
    user="postgres",
    password="P@ssW0rd",
    port="5432"
)
cur = conn.cursor()

# Flask app setup
app = Flask(__name__, static_folder='public')
app.secret_key = "abc"

# Initialization function to create the table if it doesn't exist
def init_db():
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                date_added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                date_updated TIMESTAMP,
                note VARCHAR(255) NOT NULL
            )
        """)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error during database initialization: {e}")

# Call the initialization function
init_db()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        note = request.form['note']
        try:
            cur.execute("INSERT INTO notes (note) VALUES (%s)", (note,))
            conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'error': str(e)})

    try:
        cur.execute("SELECT * FROM notes ORDER BY date_added ASC")
        notes = cur.fetchall()  # notes is a list of tuples.

        # Convert tuples to dictionaries:
        notes = [dict(id=note[0], date_added=note[1], date_updated=note[2], note=note[3]) for note in notes]

    except Exception as e:
        return f"There was an error while fetching the notes: {e}"

    return render_template("index.html", notes=notes)

@app.route('/delete/<int:id>', methods=['GET'])
def delete(id):
    try:
        cur.execute("DELETE FROM notes WHERE id = %s", (id,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    note = request.form['note']
    try:
        cur.execute("UPDATE notes SET note = %s, date_updated = CURRENT_TIMESTAMP WHERE id = %s", (note, id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_note/<int:id>', methods=['GET'])
def get_note(id):
    try:
        cur.execute("SELECT * FROM notes WHERE id = %s", (id,))
        note = cur.fetchone()
        if note:
            note_dict = dict(id=note[0], date_added=note[1], date_updated=note[2], note=note[3])
            return jsonify({'success': True, 'note': note_dict})
        else:
            return jsonify({'success': False, 'error': 'Note not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(port=8080, debug=True)