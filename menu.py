from meal import Meal
from product import Product
import json


def load_meals(file_path: str) -> None:
    """
    Loads meals from a JSON file.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
        meals = []
        for meal_data in data.get('meals', []):
            meal = Meal(name=meal_data['name'], type=meal_data['type'])
            for product_data in meal_data.get('products', []):
                product = Product(
                    name=product_data['name'],
                    unit=product_data['unit'],
                    quantity=product_data['quantity']
                )
                meal.add_product(product)
            meals.append(meal)
    return meals
