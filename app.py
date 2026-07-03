from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "secret_hospital_key_123"

def init_db():
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            phone TEXT UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            date TEXT,
            symptoms TEXT,
            diagnosis TEXT,
            prescription TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def home():
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phone = request.form['phone']
        try:
            cursor.execute("INSERT INTO patients (name, age, gender, phone) VALUES (?, ?, ?, ?)", (name, age, gender, phone))
            conn.commit()
            flash('Patient registered successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Phone number already exists!', 'danger')
        return redirect(url_for('home'))
    cursor.execute("SELECT * FROM patients ORDER BY id DESC")
    patients = cursor.fetchall()
    conn.close()
    return render_template('index.html', patients=patients)

@app.route('/patient/<int:id>', methods=['GET', 'POST'])
def patient_profile(id):
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        date = request.form['date']
        symptoms = request.form['symptoms']
        diagnosis = request.form['diagnosis']
        prescription = request.form['prescription']
        cursor.execute("INSERT INTO history (patient_id, date, symptoms, diagnosis, prescription) VALUES (?, ?, ?, ?, ?)", 
                       (id, date, symptoms, diagnosis, prescription))
        conn.commit()
        flash('Medical history file updated!', 'success')
        return redirect(url_for('patient_profile', id=id))
    cursor.execute("SELECT * FROM patients WHERE id = ?", (id,))
    patient = cursor.fetchone()
    cursor.execute("SELECT date, symptoms, diagnosis, prescription FROM history WHERE patient_id = ? ORDER BY id DESC", (id,))
    history = cursor.fetchall()
    conn.close()
    return render_template('profile.html', patient=patient, history=history)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
