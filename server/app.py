#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants")
def restaurants():
    restaurants = Restaurant.query.all()
    restaurant_list = [{
        "name": restaurant.name,
        "id": restaurant.id,
        "address": restaurant.address
    } for restaurant in restaurants]
    return make_response((restaurant_list), 200)

@app.route("/restaurants/<int:id>", methods=["GET", "DELETE"])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        if request.method == "GET":
            restaurant_dict = restaurant.to_dict()
            return make_response(restaurant_dict), 200
        elif request.method == "DELETE":
            db.session.delete(restaurant)
            db.session.commit()
            return {}, 204
    else:
        return {"error": "Restaurant not found"}, 404

@app.route('/pizzas')
def pizzas():
    pizza_list = []
    pizzas = Pizza.query.all()
    for pizza in pizzas:
        pizza_dict = {
            "id": pizza.id,
            "ingredients": pizza.ingredients,
            "name": pizza.name
        }
        pizza_list.append(pizza_dict)
    return make_response(pizza_list), 200

@app.route('/restaurant_pizzas', methods=['POST'])
def add_restaurant_pizza():
    data = request.get_json()
    try:
        price = data["price"]
        pizza_id = data["pizza_id"]
        restaurant_id = data["restaurant_id"]

        new_restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        return make_response(new_restaurant_pizza.to_dict()), 201
        
    except ValueError as e:
        db.session.rollback()
        return make_response({"errors": ["validation errors"]}, 400)
    except Exception as e:
        db.session.rollback()
        return make_response({"errors": ["validation errors"]}, 400)
    
if __name__ == "__main__":
    app.run(port=5555, debug=True)
