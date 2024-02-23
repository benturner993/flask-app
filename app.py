
import csv
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import datetime

app = Flask(__name__)
app.secret_key = '123'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Load user credentials from CSV
def load_user_credentials():
    users = {}
    with open('data/user_credentials.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            users[row['username']] = {'password': row['password']}
    return users

users = load_user_credentials()

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username and password:
            # Check if the username already exists
            if username in users:
                return 'Username already exists. Please choose a different username.'
            else:
                # Add the new user to the database and update the CSV file
                users[username] = {'password': password}
                with open('data/user_credentials.csv', 'a', newline='') as csvfile:
                    fieldnames = ['username', 'password']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow({'username': username, 'password': password})
                return 'Registration successful. You can now login with your new account.'
        else:
            return 'Username and password are required fields.'
    else:
        return render_template('register.html')

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
    customers = read_customers_from_csv('data/reactive_input.csv')
    return render_template('reactive.html', customers=customers)

@app.route('/search_customer')
@login_required
def search_customer():
    registration_id = request.args.get('registrationId')
    if registration_id is None:
        return jsonify({"error": "Registration ID not provided"})

    # Simulate customer lookup in reactive_input.csv
    with open('data/reactive_input.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['CustomerID'] == registration_id:
                return jsonify({
                    "CustomerID": row['CustomerID'],
                    "Name": row['Name'],
                    "Email": row['Email'],
                    "Phone": row['Phone'],
                    "Lapse_Propensity": row['Lapse_Propensity'],
                    "Customer_Lifetime_Value": row['Customer_Lifetime_Value'],
                    "Call_Agent": row['Call_Agent'],
                    "Discount_Eligibility": row['Discount_Eligibility'],  # Assuming this field exists in the CSV
                    "Annual_Premium": row['Annual_Premium']  # Assuming this field exists in the CSV
                })

    return jsonify({"error": "Customer not found"})

@app.route('/track_outcome', methods=['POST'])
@login_required
def track_outcome():
    data = request.get_json()
    registration_id = request.args.get('registrationId')
    outcome = data['outcome']
    username = data['username']
    time = datetime.datetime.now()

    # Fetching additional fields from the request data
    lapse_propensity = data.get('lapsePropensity')
    customer_lifetime_value = data.get('customerLifetimeValue')
    call_agent = data.get('callAgent')
    discount_eligibility = data.get('discountEligibility')
    annual_premium = data.get('annualPremium')
    stm_name = data.get('stmName')  # Fetching the STM Name from the request data

    # Constructing the outcome tracking message
    outcome_message = f"Registration ID: {registration_id}, Outcome: {outcome}, Username: {username}, Time: {time}"
    if lapse_propensity:
        outcome_message += f", Lapse Propensity: {lapse_propensity}"
    if customer_lifetime_value:
        outcome_message += f", Customer Lifetime Value: {customer_lifetime_value}"
    if call_agent:
        outcome_message += f", Call Agent: {call_agent}"
    if discount_eligibility:
        outcome_message += f", Discount Eligibility: {discount_eligibility}"
    if annual_premium:
        outcome_message += f", Annual Premium: {annual_premium}"
    if stm_name is not None:  # Add STM Name to the outcome message if it is not None
        outcome_message += f", STM Name: {stm_name}"

    # Writing the outcome message to the file
    with open('data/reactive_intervention_outcome.txt', 'a') as file:
        file.write(outcome_message + "\n")

    return jsonify({"message": "Outcome tracked successfully"})

@app.route('/track_outcome_not_found', methods=['POST'])
@login_required
def track_outcome_not_found():
    data = request.get_json()
    registration_id = data.get('registrationId')  # Use get() to avoid KeyError if 'registrationId' is not in data
    username = current_user.username
    time = datetime.datetime.now()
    with open('data/reactive_eligibility.txt', 'a') as file:
        file.write(f"Outcome: not found, Registration ID {registration_id}, Username: {username}, Time: {time}\n")
    return jsonify({"message": "Outcome tracked successfully"})

@app.route('/track_outcome_not_eligible', methods=['POST'])
@login_required
def track_outcome_not_eligible():
    data = request.get_json()
    registration_id = data.get('registrationId')  # Use get() to avoid KeyError if 'registrationId' is not in data
    username = current_user.username
    time = datetime.datetime.now()
    with open('data/reactive_eligibility.txt', 'a') as file:
        file.write(f"Outcome: not eligible, Registration ID {registration_id}, Username: {username}, Time: {time}\n")
    return jsonify({"message": "Outcome tracked successfully"})

@app.route('/track_outcome_eligible', methods=['POST'])
@login_required
def track_outcome_eligible():
    data = request.get_json()
    registration_id = data.get('registrationId')
    username = current_user.username
    time = datetime.datetime.now()
    with open('data/reactive_eligibility.txt', 'a') as file:
        file.write(f"Outcome: eligible, Registration ID {registration_id}, Username: {username}, Time: {time}\n")
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
