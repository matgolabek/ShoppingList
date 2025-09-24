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
        self.duration_int = Recipe.convert_duration_to_int(dur)
        self.ingredients: dict[str, str] = {}

    @staticmethod
    def convert_duration_to_int(dur):
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

    @staticmethod
    def convert_int_to_duration(total_minutes: str) -> str:
        """
        Converts integer (in minutes) to duration string.
        """
        total_minutes = int(total_minutes)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        if hours > 0:
            return f"{hours}h {minutes}min" if minutes > 0 else f"{hours}h"
        else:
            return f"{minutes}min"

    def add_product(self, product: Product) -> None:
        """
        Adds a product to the meal.
        """
        self.ingredients[product.name] = product.quantity

    def __repr__(self) -> str:
        return f"Recipe {self.name}, {self.mealtype}, {self.portions}: {self.ingredients}; {self.instructions})"
