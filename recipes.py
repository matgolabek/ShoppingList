from recipe import Recipe
from product import Product
import xml.etree.ElementTree as ET

def load_recipes_from_xml(filename: str, language: str = "en") -> list[Recipe]:
    """
    Parses the recipes from xml file with selected language.
    """
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
    except FileNotFoundError as e:
        print(f"File not found - {e}")
        return []
    except ET.ParseError as e:
        print(f"Not a valid XML error - {e}")
        return []

    recipes = []

    for recipe_xml in root.findall("recipe"):
        id_xml = recipe_xml.find("id")
        id_ = int(id_xml.text) if id_xml is not None else -1
        duration_xml = recipe_xml.find("duration")
        duration = duration_xml.text if duration_xml is not None else "0 min"
        name_xml = recipe_xml.find(f"name[@lang='{language}']")
        name = name_xml.text if name_xml is not None else recipe_xml.find("name").text
        portions_xml = recipe_xml.find(f"portions[@lang='{language}']")
        portions = int(portions_xml.text) if portions_xml is not None else int(recipe_xml.find("portions").text)
        mealtype_xml = recipe_xml.find(f"type[@lang='{language}']")
        mealtype = mealtype_xml.text if mealtype_xml is not None else recipe_xml.find("type").text
        vegetarian_xml = recipe_xml.find("vegetarian")
        vegetarian = vegetarian_xml.text.lower() == "true" if vegetarian_xml is not None else False
        instructions_xml = recipe_xml.find(f"instructions[@lang='{language}']")
        instructions = instructions_xml.text if instructions_xml is not None else recipe_xml.find("instructions").text

        recipe = Recipe(id_, duration, name, portions, mealtype, vegetarian, instructions)

        for ingrident_xml in recipe_xml.findall("ingredients/ingredient"):
            ing_name_xml = ingrident_xml.find(f"name[@lang='{language}']")
            ing_name  = ing_name_xml.text if ing_name_xml is not None else recipe_xml.find("name").text
            ing_quantity_xml = ingrident_xml.find(f"quantity[@lang='{language}']")
            ing_quantity  = ing_quantity_xml.text if ing_quantity_xml is not None else ingrident_xml.find("quantity").text

            ingrident = Product(ing_name, ing_quantity)
            recipe.add_product(ingrident)
        
        recipes.append(recipe)

    return recipes
    

if __name__ == "__main__":  # quick test
    r = load_recipes_from_xml("recipes.xml", "pl")
    print(r)
