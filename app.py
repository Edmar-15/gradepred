from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import joblib
import pandas as pd

app = Flask(__name__)

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin1111",
    database="student_performance_db"
)
cursor = db.cursor()

# Load ML model
model = joblib.load('student_model.pkl')

@app.route('/')
def index():
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM predictions")
    pred_count = cursor.fetchone()[0]
    return render_template('index.html', users=user_count, predictions=pred_count)

# USERS CRUD
@app.route('/users')
def users():
    cursor.execute("SELECT * FROM users")
    all_users = cursor.fetchall()
    return render_template('users.html', users=all_users)

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form['name']
    email = request.form['email']
    cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
    db.commit()
    return redirect(url_for('users'))

@app.route('/delete_user/<int:id>')
def delete_user(id):
    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    db.commit()
    return redirect(url_for('users'))

# PREDICTION
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    prediction = None
    cursor.execute("SELECT id, name FROM users")
    users_list = cursor.fetchall()

    if request.method == 'POST':
        user_id = request.form['user_id']
        studytime = int(request.form['studytime'])
        failures = int(request.form['failures'])
        absences = int(request.form['absences'])
        G1 = int(request.form['G1'])
        G2 = int(request.form['G2'])

        # Predict
        input_data = pd.DataFrame([[studytime, failures, absences, G1, G2]], 
                                  columns=['studytime', 'failures', 'absences', 'G1', 'G2'])
        pred = model.predict(input_data)[0]

        # Save to DB
        cursor.execute(""" 
            INSERT INTO predictions (user_id, studytime, failures, absences, G1, G2, predicted_G3)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, studytime, failures, absences, G1, G2, pred))
        db.commit()

        prediction = round(pred, 2)

    return render_template('predict.html', prediction=prediction, users=users_list)

# PREDICTION HISTORY
@app.route('/history')
def history():
    cursor.execute("""
        SELECT p.*, u.name 
        FROM predictions p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
    """)
    records = cursor.fetchall()
    return render_template('history.html', records=records)

if __name__ == '__main__':
    app.run(debug=True)