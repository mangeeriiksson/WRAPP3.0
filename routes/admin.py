from flask import Blueprint, render_template, session, request, redirect, url_for, flash, jsonify
import sqlite3
from models.database import delete_product
from config import Config  # Behöver Config för databas-URL

admin_blueprint = Blueprint("admin", __name__)

@admin_blueprint.route("/admin", endpoint="admin_panel")
def admin_panel():
    """Visa adminpanelen om användaren är inloggad och har admin-roll."""
    if "user_token" in session and session.get("role") == "admin":
        return render_template("admin.html")

    flash("Unauthorized access!", "danger")
    return redirect(url_for("auth.login"))

@admin_blueprint.route("/infinite_money", methods=["POST"])
def infinite_money():
    """Lägger till pengar för admin själv."""
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

@admin_blueprint.route("/add_money", methods=["POST"])
def add_money_to_user():
    """Låter admin lägga till pengar på en annan användares konto."""
    if session.get("role") != "admin":
        return jsonify({"error": "Access denied! Only admins can add money to users."}), 403

    data = request.json
    username = data.get("username")
    amount = data.get("amount")

    if not username or not amount:
        return jsonify({"error": "Username and amount are required."}), 400

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({"error": "Invalid amount."}), 400

    database_url = Config.SQLALCHEMY_DATABASE_URI
    if database_url.startswith('sqlite:///'):
        database_path = database_url[len('sqlite:///'):]
    else:
        return jsonify({"error": "Unsupported database URL"}), 500

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (amount, username))
        conn.commit()

    return jsonify({"message": f"Added {amount} to {username}'s balance!"}), 200

@admin_blueprint.route("/delete_product/<int:product_id>", methods=["POST"])
def delete_product_route(product_id):
    """Tar bort en produkt från databasen – Endast admin."""
    if session.get("role") != "admin":
        flash("Access denied! Only admins can delete products.", "error")
        return redirect(url_for("admin.admin_panel"))
    
    delete_product(product_id)
    flash("Product deleted successfully!", "success")
    return redirect(url_for("admin.admin_panel"))

@admin_blueprint.route("/reset_all_balances", methods=["POST"])
def reset_all_balances():
    """Nollställer balansen för alla användare – Endast för admin."""
    if session.get("role") != "admin":
        return jsonify({"error": "Access denied! Only admins can reset all balances."}), 403

    database_url = Config.SQLALCHEMY_DATABASE_URI
    if database_url.startswith('sqlite:///'):
        database_path = database_url[len('sqlite:///'):]
    else:
        return jsonify({"error": "Unsupported database URL"}), 500

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = 0")  # Nollställer alla balanser
        conn.commit()

    return jsonify({"message": "All users' balances have been reset!"}), 200
