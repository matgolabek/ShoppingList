from product import Product


class Recipe:
    """
    Represents a meal in the shopping list.
    """
    def __init__(self, id_: int, dur: str, name: str, portions: int, mealtype: str, vegetarian: bool, instructions: str = None):
        self.id = id_
        self.name = name
        self.mealtype = mealtype
        self.portions = portions
        self.vegetarian = vegetarian
        self.instructions = instructions
        self.duration = dur
        self.duration_int = self.convert_duration_to_int(dur)
        self.ingredients: dict[str, str] = {}

    def convert_duration_to_int(self, dur):
        """
        Converts duration string to integer (in minutes).
        """
        try:
            if "h" in dur:
                parts = dur.split("h")
                hours = int(parts[0].strip())
                if parts[1].strip() == "":
                    minutes = 0
                else:
                    minutes = int(parts[1].replace("min", "").strip()) if len(parts) > 1 else 0
                total_minutes = hours * 60 + minutes
            else:
                total_minutes = int(dur.replace("min", "").strip())
            return total_minutes
        except ValueError:
            return 0

    def add_product(self, product: Product) -> None:
        """
        Adds a product to the meal.
        """
        self.ingredients[product.name] = product.quantity

    def __repr__(self) -> str:
        return f"Recipe {self.name}, {self.mealtype}, {self.portions}: {self.ingredients}; {self.instructions})"
