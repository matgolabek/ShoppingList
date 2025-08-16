class Product:
    """
    Represents a product of the meal in the shopping list.
    """
    def __init__(self, name, unit, quantity):
        self.name = name
        self.unit = unit
        self.quantity = quantity

    def __repr__(self) -> str:
        return f"Product(name={self.name}, unit={self.unit}, quantity={self.quantity})"
