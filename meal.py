from product import Product


class Meal:
    """
    Represents a meal in the shopping list.
    """
    def __init__(self, name: str, type: list[str]):
        self.name = name
        self.type = type
        self.products = {}

    def add_product(self, product: Product) -> None:
        """
        Adds a product to the meal.
        """
        self.products[product.name] = product

    def __repr__(self) -> str:
        return f"Meal(name={self.name})"
