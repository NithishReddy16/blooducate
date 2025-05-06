from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import pymysql
from models import find_donors
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'secretkey'

# Database connection function
def get_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='6666',
        database='blooducate',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/search_donors')
def search_donors():
    blood_group = request.args.get('blood_group')
    location = request.args.get('location')
    donors = None
    
    if blood_group and location:
        # Get donors who haven't donated in the last 3 months
        three_months_ago = datetime.now() - timedelta(days=90)
        donors = find_donors(blood_group, location, three_months_ago)
    
    return jsonify({'donors': donors})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        phone = request.form['phone']
        location = request.form['location']
        gender = request.form['gender']
        blood_group = request.form['blood_group']

        # Validate password length
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return redirect('/register')

        # Validate password match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect('/register')

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO donors (name, email, password, phone, location, gender, blood_group)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, email, password, phone, location, gender, blood_group))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect('/login')
        except pymysql.Error as e:
            flash(f'Registration failed: {str(e)}', 'error')
            return redirect('/register')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM donors WHERE email=%s AND password=%s", (email, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user:
                session['user'] = user
                return redirect('/donor_dashboard')
            else:
                flash('Invalid login credentials.', 'error')
        except pymysql.Error as e:
            flash(f'Login failed: {str(e)}', 'error')
    return render_template('login.html')

@app.route('/donor_dashboard')
def donor_dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('donor_dashboard.html', user=session['user'])

@app.route('/update_last_donation', methods=['POST'])
def update_last_donation():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    last_donation_date = request.form.get('last_donation_date')
    if not last_donation_date:
        return jsonify({'success': False, 'message': 'Please select a date'})
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE donors 
            SET last_donation_date = %s 
            WHERE id = %s
        """, (last_donation_date, session['user']['id']))
        conn.commit()
        cursor.close()
        conn.close()
        
        # Update session data
        session['user']['last_donation_date'] = last_donation_date
        
        return jsonify({
            'success': True,
            'message': 'Last donation date updated successfully!',
            'new_date': last_donation_date
        })
    except pymysql.Error as e:
        return jsonify({'success': False, 'message': f'Update failed: {str(e)}'})

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = None
    if request.method == 'POST':
        blood_group = request.form['blood_group']
        area = request.form['area']
        cursor = get_db().cursor()
        cursor.execute("SELECT name, phone, blood_group, area FROM donors WHERE blood_group=%s AND area=%s", (blood_group, area))
        results = cursor.fetchall()
        cursor.close()
    return render_template('search.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)