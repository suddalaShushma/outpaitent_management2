from flask import Flask, render_template, request, redirect, url_for
from io import BytesIO
import sqlite3
import qrcode
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
# Ensure the static directory exists
os.makedirs('static', exist_ok=True)
DATABASE = 'patient_database.db'
# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('patient_database.db')
    conn.row_factory = sqlite3.Row
    return conn
# Initialize database
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                patient_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                contact TEXT NOT NULL
            )
        ''')
        conn.commit()

# Ensure the database is initialized when the application starts
init_db()


# Create table if it doesn't exist
with get_db_connection() as conn:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            contact TEXT NOT NULL
        )
    ''')
    conn.commit()

@app.route('/')
def index():
    return render_template('registration.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    age = request.form['age']
    contact = request.form['contact']
    if not name or not age or not contact:
        flash('All fields are required!', 'error')
        return redirect(url_for('index'))

    try:
        age = int(age)
    except ValueError:
        flash('Age must be a number!', 'error')
        return redirect(url_for('index'))

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO patients (name, age, contact) VALUES (?, ?, ?)", (name, age, contact))
        conn.commit()
        patient_id = cursor.lastrowid

    qr_code_filename = generate_qr_code(patient_id, name)
    print(f"Generated QR code filename: {qr_code_filename}")
    return render_template('registration_success.html', qr_code_filename=qr_code_filename)

def generate_qr_code(patient_id, name):
    data = f"Patient ID: {patient_id}\nName: {name}"
    filename = f"static/patient_{patient_id}_qr_code.png"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    return filename
@app.route('/patients')
def list_patients():
    with get_db_connection() as conn:
        patients = conn.execute('SELECT * FROM patients').fetchall()
    return render_template('patients.html', patients=patients)

@app.route('/edit/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    with get_db_connection() as conn:
        patient = conn.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        contact = request.form['contact']

        if not name or not age or not contact:
            flash('All fields are required!', 'error')
            return redirect(url_for('edit_patient', patient_id=patient_id))

        try:
            age = int(age)
        except ValueError:
            flash('Age must be a number!', 'error')
            return redirect(url_for('edit_patient', patient_id=patient_id))

        with get_db_connection() as conn:
            conn.execute('UPDATE patients SET name = ?, age = ?, contact = ? WHERE patient_id = ?',
                         (name, age, contact, patient_id))
            conn.commit()
        flash('Patient updated successfully!', 'success')
        return redirect(url_for('list_patients'))

    return render_template('edit_patient.html', patient=patient)

@app.route('/delete/<int:patient_id>')
def delete_patient(patient_id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM patients WHERE patient_id = ?', (patient_id,))
        conn.commit()
    flash('Patient deleted successfully!', 'success')
    return redirect(url_for('list_patients'))

if __name__ == '__main__':
    app.run(debug=True)
