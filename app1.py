from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
import qrcode

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
db = SQLAlchemy(app)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    # Add other patient fields as necessary

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        # Capture other fields as necessary

        # Create a new patient record
        new_patient = Patient(name=name, age=int(age))
        db.session.add(new_patient)
        db.session.commit()

        # Redirect to generate QR code for the new patient
        return redirect(url_for('generate_qr', patient_id=new_patient.id))
    return render_template('registration.html')

@app.route('/generate_qr/<int:patient_id>')
def generate_qr(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    data = f"Patient ID: {patient.id}, Name: {patient.name}, Age: {patient.age}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, 'PNG')
    buffer.seek(0)
    
    return send_file(buffer, mimetype='image/png')

if __name__ == '_main_':
    db.create_all()  # Create database tables
    app.run(debug=True)