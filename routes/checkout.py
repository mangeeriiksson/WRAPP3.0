from flask import Blueprint, session, redirect, url_for, flash, request, render_template

checkout_blueprint = Blueprint("checkout_blueprint", __name__)

@checkout_blueprint.route("/checkout", methods=["GET", "POST"])
def checkout():
    # Debugging
    print(f"Request method: {request.method}")
    print(f"Request URL: {request.url}")
    print(f"Session cart: {session.get('cart', [])}")

    if request.method == "POST":
        cart = session.get("cart", [])
        if not cart:
            flash("Your cart is empty!", "danger")
            return redirect(url_for("cart_blueprint.view_cart"))

        total_price = sum(float(item["price"]) * item.get("quantity", 1) for item in cart)

        user_balance = session.get("balance", 0)
        if user_balance < total_price:
            flash("Insufficient balance to complete the purchase!", "danger")
            return redirect(url_for("cart_blueprint.view_cart"))

        session["balance"] = user_balance - total_price
        session.pop("cart", None)
        session.pop("discount", None)
        session.pop("used_coupons", None)
        session.modified = True

        flash(f"Purchase completed! Total: {total_price} SEK", "success")
        return redirect(url_for("checkout_blueprint.confirmation"))

    return render_template("checkout.html", cart=session.get("cart", []))


@checkout_blueprint.route("/confirmation")
def confirmation():
    return render_template("confirmation.html")
