from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from routes.auth import auth_blueprint
from routes.cart import cart_blueprint
from routes.user import user_blueprint
from routes.products import products_blueprint
from routes.admin import admin_blueprint
from routes.checkout import checkout_blueprint
from models.database import init_db, reset_user_balance  # Tog bort reset_all_balances

app = Flask(__name__)
app.config.from_object("config.Config")

# Initialize the database
init_db()

# Register blueprints
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(cart_blueprint, url_prefix='/cart')
app.register_blueprint(user_blueprint, url_prefix='/user')
app.register_blueprint(products_blueprint, url_prefix='/products')
app.register_blueprint(admin_blueprint, url_prefix='/admin')  # Admin har nu reset_all_balances
app.register_blueprint(checkout_blueprint, url_prefix='/checkout')

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/reset_balance', methods=['POST'])
def reset_balance():
    """Nollställer en specifik användares balans."""
    data = request.json
    username = data.get('username')

    if not username:
        return jsonify({"error": "Username not provided"}), 400

    reset_user_balance(username)
    return jsonify({"message": f"Balance reset for user: {username}"}), 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
