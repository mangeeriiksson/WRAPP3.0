import sqlite3
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash

products_blueprint = Blueprint("products_blueprint", __name__)

# Ange den korrekta sökvägen till din databas
database_path = os.path.abspath("data/WRAPP.db")

@products_blueprint.route('/shop')
def shop():
    """Hämtar alla produkter från databasen och visar dem i shoppen."""
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row  # Gör att vi kan använda kolumnnamn i templaten
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, description, image FROM products")
        products = cursor.fetchall()

    return render_template("shop.html", products=products)

@products_blueprint.route('/shop/search')
def search():
    """Söker efter produkter med flera SQL-injection sårbarheter"""
    query = request.args.get("query", "")
    
    # ⚠️ Blacklist-strippning - men kan kringgås!
    blacklist = ["UNION", "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "OR", "AND", "--", "#", ";", "'"]
    for word in blacklist:
        query = query.replace(word, "")  # Strippning men kan kringgås genom case variationer

    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # ⚠️ Osäker SQL-fråga - sårbar för UNION-baserad SQL-injection
        sql_query = f"SELECT id, name, price, description, image FROM products WHERE name LIKE '%{query}%'"
        print(f"Executing: {sql_query}")  # Debugging - skriver ut SQL-frågan
        cursor.execute(sql_query)  # ⚠️ INTE SÄKER! Används för att testa SQL-injection.
        
        products = cursor.fetchall()

    return render_template("shop.html", products=products)

@products_blueprint.route('/add_product', methods=['GET', 'POST'])
def add_product_view():
    """Lägger till en ny produkt i databasen."""
    if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")
        description = request.form.get("description")
        image = request.form.get("image")

        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO products (name, price, description, image) VALUES (?, ?, ?, ?)",
                (name, price, description, image)
            )
            conn.commit()

        flash("Product added successfully!", "success")
        return redirect(url_for("products_blueprint.shop"))

    return render_template("add_product.html")
