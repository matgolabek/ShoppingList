class Product:
    """
    Represents a product of the recipe in the shopping list.
    """
    def __init__(self, name: str, quantity: str):
        self.name = name
        self.quantity = quantity

    def __repr__(self) -> str:
        return f"Product({self.name} {self.quantity})"
