import csv
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import datetime

app = Flask(__name__)
app.secret_key = '123'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Mock user database (replace this with your actual user database)
users = {'username': {'password': 'password'}}  

# User class required by Flask-Login
class User(UserMixin):
    def __init__(self, username):
        self.username = username

    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(user_id):
    user = User(user_id)
    return user

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Received POST request with username: {username} and password: {password}")
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            print(f"User {username} logged in successfully")
            return redirect(url_for('home'))
        else:
            print("Invalid username or password")
            return 'Invalid username or password'
    else:
        print("Received GET request for login page")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Function to read customer data from CSV file
def read_customers_from_csv(filename):
    customers = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            customers.append(row)
    return customers

@app.route('/proactive')
@login_required
def proactive():
    customers = read_customers_from_csv('data/proactive_input.csv')
    return render_template('proactive.html', customers=customers)

@app.route('/winback_output', methods=['POST'])
@login_required
def winback_output():
    data = request.get_json()
    customer_name = data['customerName']
    acceptance = data['acceptance']
    username = current_user.username
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Save acceptance to a text file
    with open('data/winback_output.txt', 'a') as file:
        file.write(f"Customer: {customer_name}, Acceptance: {acceptance}, Username: {username}, Time: {time}\n")
    return jsonify({"message": "Acceptance saved successfully"})


@app.route('/save_acceptance', methods=['POST'])
@login_required
def save_acceptance():
    data = request.get_json()
    customer_name = data['customerName']
    acceptance = data['acceptance']
    username = current_user.username
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Save acceptance to a text file
    with open('data/proactive_output.txt', 'a') as file:
        file.write(f"Customer: {customer_name}, Acceptance: {acceptance}, Username: {username}, Time: {time}\n")
    return jsonify({"message": "Acceptance saved successfully"})

@app.route('/reactive')
@login_required
def reactive():
    return render_template('reactive.html')

@app.route('/search_customer')
@login_required
def search_customer():
    registration_id = request.args.get('registrationId')
    if registration_id is None:
        return 'Registration ID not provided'
    # Simulate customer lookup in customers.csv
    with open('data/reactive_input.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            if row[0] == registration_id:
                return 'found'
    return 'not found'

@app.route('/track_outcome', methods=['POST'])
@login_required
def track_outcome():
    data = request.get_json()
    customer_number = request.args.get('customerNumber')
    outcome = data['outcome']
    username = current_user.username
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Save outcome to a text file
    with open('data/reactive_output.txt', 'a') as file:
        file.write(f"Customer Number: {customer_number}, Outcome: {outcome}, Username: {username}, Time: {time}\n")
    return jsonify({"message": "Outcome tracked successfully"})

@app.route('/performance')
@login_required
def performance():
    return render_template('performance.html')

@app.route('/issues-tracking')
@login_required
def issues_tracking():
    return render_template('issues_tracking.html')

@app.route('/win-back')  # Route for the Win-Back page
@login_required
def win_back():
    customers = read_customers_from_csv('data/winback_input.csv')
    return render_template('win_back.html', customers=customers)

if __name__ == '__main__':
    app.run(debug=True)
