from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from models.database import get_order_status, get_user_orders

user_blueprint = Blueprint("user", __name__)

@user_blueprint.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        # Handle form submission
        bio = request.form.get("bio")
        profile_picture = request.files.get("profile_picture")
        # Save bio and profile picture to the database or session
        session["bio"] = bio
        if profile_picture:
            # Save the profile picture to the static folder
            profile_picture.save(f"static/{profile_picture.filename}")
            session["profile_picture"] = profile_picture.filename
        flash("Profile updated successfully!", "success")
        return redirect(url_for("user.profile"))

    bio = session.get("bio", "")
    profile_picture = session.get("profile_picture", "")
    balance = session.get("balance", 0)
    return render_template("profile.html", bio=bio, profile_picture=profile_picture, balance=balance)

@user_blueprint.route("/order_status", methods=["GET", "POST"])
def order_status():
    result = None
    error = None
    if request.method == "POST":
        order_id = request.form.get("order_id")
        if order_id:
            result = get_order_status(order_id)
            if not result:
                error = "Order not found"
        else:
            error = "Order ID is required"

    user_orders = get_user_orders(session["user_token"])
    return render_template("order_status.html", result=result, error=error, user_orders=user_orders)

# Add infinite_money function to admin panel
admin_blueprint = Blueprint("admin", __name__)

@admin_blueprint.route("/admin", endpoint="admin_panel")
def admin_panel():
    if 'user_token' in session:
        return render_template("admin.html")
    
    flash("Unauthorized access!", "danger")
    return redirect(url_for("auth.login"))

@admin_blueprint.route("/infinite_money", methods=["POST"])
def infinite_money():
    if session.get("role") != "admin":
        flash("Access denied! Only admins can add money.", "error")
        return redirect(url_for("admin_panel"))
    
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
    return redirect(url_for("admin_panel"))

# Redirect from shop to cart
@user_blueprint.route("/products/shop")
def shop():
    return redirect(url_for("cart"))

# Redirect from cart to checkout
@user_blueprint.route("/cart")
def cart():
    return redirect(url_for("checkout"))

# Checkout page route
@user_blueprint.route("/checkout")
def checkout():
    return render_template("checkout.html")
