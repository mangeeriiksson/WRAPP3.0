from flask import Flask, Blueprint, render_template, request, session, redirect, url_for, flash, current_app as app
from models.database import verify_user, add_user
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
from datetime import timedelta

app = Flask(__name__)
auth_blueprint = Blueprint("auth", __name__)

# Encryption key and cipher setup
key = b"Sixteen byte key"
cipher = Cipher(algorithms.AES(key), modes.ECB())

def encrypt_token(token):
    padded_token = token + (16 - len(token) % 16) * " "
    return base64.b64encode(cipher.encryptor().update(padded_token.encode())).decode()

def decrypt_token(token):
    decoded = base64.b64decode(token)
    return cipher.decryptor().update(decoded).decode().strip()

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        stay_logged_in = request.form.get("stay_logged_in")

        print(f"Login attempt: username={username}, stay_logged_in={stay_logged_in}")

        role = verify_user(username, password)  # Retrieve role from database

        if role:
            session["user_token"] = encrypt_token(username)
            session["role"] = role  # Save user role

            if stay_logged_in:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=30)  # Set session timeout to 30 days
            else:
                session.permanent = False

            if role == "admin":
                return redirect(url_for("admin.admin_panel"))  # Redirect admin to admin panel
            else:
                return redirect(url_for("user.profile"))  # Redirect user to profile (dashboard not found)

        flash("Invalid credentials", "error")
        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        print(f"Registration attempt: username={username}, email={email}")

        # Check if the username or email already exists
        if add_user(username, password, email):
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("Username or email already exists", "error")

    return render_template("register.html")

@auth_blueprint.route('/logout')
def logout():
    session.pop("user_token", None)
    session.pop("role", None)
    flash("You have been logged out", "success")
    return redirect(url_for("home"))

# Move infinite_money function to admin panel
admin_blueprint = Blueprint("admin", __name__)

@admin_blueprint.route("/infinite_money", methods=["POST"])
def infinite_money():
    if session.get("role") != "admin":
        flash("Access denied! Only admins can add money.", "error")
        return redirect(url_for("admin.admin_panel"))
    
    amount = request.form.get("amount")
    if amount:
        try:
            amount = float(amount)
            session["balance"] = session.get("balance", 0) + amount
            flash(f"Added {amount} to your balance!", "success")
        except ValueError:
            flash("Invalid amount!", "error")
    else:
        flash("Amount is required!", "error")
    return redirect(url_for("admin.admin_panel"))
