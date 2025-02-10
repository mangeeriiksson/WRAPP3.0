from flask import Blueprint, render_template, session, request, redirect, url_for, flash, jsonify

cart_blueprint = Blueprint("cart_blueprint", __name__, url_prefix="/cart")

# Simulerad kupongdatabas
VALID_COUPONS = {
    "DISCOUNT10": 0.10,  # 10% rabatt
    "SAVE20": 0.20,      # 20% rabatt
    "FREESHIP": 0.00     # Fri frakt (kan hanteras separat)
}

@cart_blueprint.route("/")
def view_cart():
    cart = session.get("cart", [])

    subtotal = sum(item["price"] * item.get("quantity", 1) for item in cart)
    discount = session.get("discount", 0)
    total_price = subtotal - (subtotal * discount)

    used_coupons = session.get("used_coupons", [])
    user_balance = session.get("balance", 0)  # Användarens saldo

    return render_template(
        "cart.html", 
        cart=cart, 
        subtotal=subtotal, 
        total_price=total_price, 
        discount=discount, 
        used_coupons=used_coupons,
        user_balance=user_balance
    )

@cart_blueprint.route("/add", methods=["POST"])
def add_to_cart():
    product_id = request.form.get("product_id")
    price = request.form.get("price")
    quantity = int(request.form.get("quantity", 1))

    if not product_id or not price:
        return jsonify({"success": False, "message": "Felaktiga produktuppgifter!"})

    if "cart" not in session:
        session["cart"] = []

    for item in session["cart"]:
        if item["id"] == int(product_id):
            item["quantity"] += quantity
            break
    else:
        session["cart"].append({"id": int(product_id), "price": float(price), "quantity": quantity})
    
    session.modified = True
    return redirect(url_for("cart_blueprint.view_cart"))

@cart_blueprint.route("/remove", methods=["POST"])
def remove_from_cart():
    product_id = int(request.form.get("product_id"))
    
    if "cart" in session:
        session["cart"] = [item for item in session["cart"] if item["id"] != product_id]
        session.modified = True
        flash("Product removed from cart", "success")
    else:
        flash("Cart is empty!", "danger")
    
    return redirect(url_for("cart_blueprint.view_cart"))

@cart_blueprint.route("/apply_coupon", methods=["POST"])
def apply_coupon():
    coupon_code = request.form.get("coupon_code").strip().upper()
    used_coupons = session.get("used_coupons", [])

    if coupon_code in used_coupons:
        flash("This coupon has already been used!", "danger")
        return redirect(url_for("cart_blueprint.view_cart"))
    
    if coupon_code in VALID_COUPONS:
        session["discount"] = VALID_COUPONS[coupon_code]
        used_coupons.append(coupon_code)
        session["used_coupons"] = used_coupons
        flash(f"Coupon '{coupon_code}' applied! Discount: {VALID_COUPONS[coupon_code] * 100}%", "success")
    else:
        flash("Invalid coupon code!", "danger")

    return redirect(url_for("cart_blueprint.view_cart"))

@cart_blueprint.route("/checkout", methods=["POST"])
def checkout():
    cart = session.get("cart", [])
    if not cart:
        flash("Your cart is empty!", "danger")
        return redirect(url_for("cart_blueprint.view_cart"))
    
    subtotal = sum(item["price"] * item.get("quantity", 1) for item in cart)
    discount = session.get("discount", 0)
    total_price = subtotal - (subtotal * discount)

    user_balance = session.get("balance", 0)

    if user_balance < total_price:
        flash("Insufficient balance!", "danger")
        return redirect(url_for("cart_blueprint.view_cart"))

    session["balance"] = user_balance - total_price
    session.pop("cart", None)
    session.pop("discount", None)
    session.pop("used_coupons", None)
    session.modified = True

    flash(f"Purchase completed! Total: {total_price} SEK", "success")
    return redirect(url_for("checkout_blueprint.confirmation"))
