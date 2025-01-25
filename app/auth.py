import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required,current_user
from app.models import User
from flask_mail import Message, Mail
import jwt
from datetime import datetime, timedelta

def generate_reset_token(email):
    expiration = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    payload = {
        'email': email,
        'exp': expiration
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def send_reset_email(email):
    token = generate_reset_token(email)
    reset_url = f"{request.url_root}resetUserPassword/{token}"
    
    mail = current_app.extensions['mail']
    # Email content
    msg = Message("Password Reset Request",
                  sender="username@mail.com",
                  recipients=[email])
    msg.body = f"""
    To reset your password, visit the following link:
    {reset_url}
    If you did not make this request, please ignore this email.
    """
    mail.send(msg)

# Configure Flask to use 'dist' for static files
auth = Blueprint('auth', __name__)

@auth.route("/", methods=["GET", "POST"])
def loginUser():
    if request.method == "POST":
        print(f"Is user authenticated before login? {current_user.is_authenticated}")
        email = request.form.get("Email")
        password = request.form.get("Password")
        user = current_app.db['users'].find_one({'email': email})

        if user and check_password_hash(user['password'], password):
           # User authenticated, now login them in
            user_instance = User(user['_id'], user['userName'], user['email'])
            login_user(user_instance)  # This logs the user in
            print(f"Logged in user: {user_instance}") 
            flash('Login successful!', 'success')

            # Debugging: Check if user is logged in
            print(f"Is user authenticated? {current_user.is_authenticated}")

            # Check for the 'next' parameter and redirect accordingly
            next_page = request.args.get('next')
            if next_page:  # If there's a next page, redirect to it
                print(f"Next page: {next_page}")
                return redirect(next_page)
            else:  # Otherwise, redirect to the default page (dashboard)
                print("Redirecting to default page (homePage).")
                return redirect(url_for('views.homePage'))  # Default to dashboard if no 'next' URL
            
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.loginUser'))  # Stay on login page
    return render_template('auth-signin.html')

@auth.route('/signup', methods=['GET','POST'])
def registerUser():
    if request.method == 'POST':
        # Get form data
        userName = request.form.get('Username')
        email = request.form.get('Email')
        password = request.form.get('Password')

        # Debugging output
        print(f"Received - Username: {userName}, Email: {email}, Password: {password}")

        # Existing logic
       
        # Input validation (Checking if any field is missing)
        if not userName or not email or not password:
            flash('All fields are required!', 'error')
            return redirect(url_for('auth.registerUser'))

        userCollection = current_app.db['users']
        # Check if the user already exists
        existing_user = userCollection.find_one({'email': email})
        if existing_user:
            flash('User already exists with this email!', 'error')
            return redirect(url_for('auth.registerUser'))

        # Hash the password for security
        # hashed_password = generate_password_hash(password, method='sha256')
        # Hash the password for security
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')


        # Try inserting the user into the database
        try:
            # Log form data for debugging
            print(f"Form data - UserName: {userName}, Email: {email}, Password: {password}")

            # Save the user to the database
            result = userCollection.insert_one({
                'userName' : userName,
                'email': email,
                'password': hashed_password
            })
            print(f"Data inserted with ID: {result.inserted_id}")  # Log the inserted id for confirmation
            
            
        except Exception as e:
            print(f"Error inserting to MongoDB: {e}")  # Log the error to identify any issues
            flash('An error occurred while creating your account. Please try again later.', 'error')
            return redirect(url_for('auth.registerUser'))

        # # Success message
        flash('Account created successfully! Please sign in.', 'success')
        return redirect(url_for('auth.loginUser'))  # Redirect to the login page

    # For GET request, render the sign-up page
    return render_template('auth-signup.html')


@auth.route('/resetUserPassword/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # app = current_app
    try:
        # Decode the JWT
        decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        email = decoded['email']
    except jwt.ExpiredSignatureError:
        flash('The password reset link has expired.', 'error')
        return redirect(url_for('auth.resetUserPassword'))
    except jwt.InvalidTokenError:
        flash('Invalid password reset link.', 'error')
        return redirect(url_for('auth.resetUserPassword'))

    # Handle password reset form submission
    if request.method == 'POST':
        new_password = request.form.get('Password')
        confirm_password = request.form.get('confirmPassword')

        if not new_password or not confirm_password:
            flash('All fields are required!', 'error')
            return render_template('authRestPassword.html', email=email)

        if new_password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('authRestPassword.html', email=email)

        # Hash and update the password in the database
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        userCollection = current_app.db['users']
        userCollection.update_one({'email': email}, {'$set': {'password': hashed_password}})
        print("Password change success")
        flash('Your password has been reset successfully!', 'success')
        return redirect(url_for('auth.loginUser'))

    return render_template('authRestPassword.html', email=email, token=token)


@auth.route("/resetPassword", methods=['GET', 'POST'])
def resetUserPassword():
    if request.method == 'POST':

        email = request.form.get('Email')

        # Debugging output
        print(f"Received - Email: {email}")
        if not email:
            flash('Email field is  required!', 'error')
            print("email not entered")
            return redirect(url_for('auth.resetUserPassword'))
        
        data = current_app.db['users']
        existingEmail = data.find_one({'email': email})
        if existingEmail:
                # Send the reset email directly
                send_reset_email(email)
                print("message send success")
                return redirect(url_for('auth.resetUserPassword'))
        else:
            flash("Email not registered!Please register yourself first.", "error")
            return redirect(url_for('auth.registerUser'))

    return render_template('auth-reset-password.html')

@auth.route("/logout")
@login_required
def logoutUser():
    print("Logout route reached.")
    print(f"User: {current_user.username}, Authenticated: {current_user.is_authenticated}")
    logout_user()
    print("User logged out.")
    session.clear()
    return redirect(url_for('auth.loginUser'))


