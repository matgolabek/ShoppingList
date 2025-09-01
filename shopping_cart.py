from recipes import load_recpies_from_xml


class ShoppingCart:
    def __init__(self, file_path: str, language: str = "en"):
        self.recipes = load_recpies_from_xml(file_path, language)
        self.cart = []

    def add_to_cart(self, meal_name: str):
        for meal in self.recipes:
            if meal.name == meal_name:
                self.cart.append(meal)
                return f"{meal_name} added to cart."
        return f"Meal {meal_name} not found."

    def view_cart(self):
        return [meal.name for meal in self.cart]

    def clear_cart(self):
        self.cart = []