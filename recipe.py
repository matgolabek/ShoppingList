from product import Product


class Recipe:
    """
    Represents a meal in the shopping list.
    """
    def __init__(self, name: str, portions: int, mealtype: str, instructions: str = None):
        self.name = name
        self.mealtype = mealtype
        self.portions = portions
        self.instructions = instructions
        self.ingredients: dict[str, str] = {}

    def add_product(self, product: Product) -> None:
        """
        Adds a product to the meal.
        """
        self.ingredients[product.name] = product.quantity

    def __repr__(self) -> str:
        return f"Recipe {self.name}, {self.mealtype}, {self.portions}: {self.ingredients}; {self.instructions})"
