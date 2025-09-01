from recipe import Recipe
from product import Product
import xml.etree.ElementTree as ET

def load_recpies_from_xml(filename: str, language: str = "en") -> list[Recipe]:
    """
    Parses the recpies from xml file with selected language.
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
        name_xml = recipe_xml.find(f"name[@lang='{language}']")
        name = name_xml.text if name_xml is not None else recipe_xml.find("name").text
        portions_xml = recipe_xml.find(f"portions[@lang='{language}']")
        portions = int(portions_xml.text) if portions_xml is not None else int(recipe_xml.find("portions").text)
        mealtype_xml = recipe_xml.find(f"type[@lang='{language}']")
        mealtype = mealtype_xml.text if mealtype_xml is not None else recipe_xml.find("type").text
        instructions_xml = recipe_xml.find(f"instructions[@lang='{language}']")
        instructions = instructions_xml.text if instructions_xml is not None else recipe_xml.find("instructions").text

        recipe = Recipe(name, portions, mealtype, instructions)

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
    r = load_recpies_from_xml("recipes.xml", "pl")
    print(r)
