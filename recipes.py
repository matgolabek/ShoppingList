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


def append_recipe_to_xml(filename: str, recipe: Recipe, language: str = "en") -> None:
    """
    Appends a new recipe to the xml file.
    """
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
    except FileNotFoundError as e:
        print(f"File not found - {e}")
        return
    except ET.ParseError as e:
        print(f"Not a valid XML error - {e}")
        return

    recipe_xml = ET.SubElement(root, "recipe")

    id_xml = ET.SubElement(recipe_xml, "id")
    id_xml.text = str(recipe.id)

    duration_xml = ET.SubElement(recipe_xml, "duration")
    duration_xml.text = recipe.duration

    name_xml = ET.SubElement(recipe_xml, "name", lang=language)
    name_xml.text = recipe.name

    portions_xml = ET.SubElement(recipe_xml, "portions", lang=language)
    portions_xml.text = str(recipe.portions)

    type_xml = ET.SubElement(recipe_xml, "type", lang=language)
    type_xml.text = recipe.mealtype

    vegetarian_xml = ET.SubElement(recipe_xml, "vegetarian")
    vegetarian_xml.text = "true" if recipe.vegetarian else "false"

    instructions_xml = ET.SubElement(recipe_xml, "instructions", lang=language)
    instructions_xml.text = recipe.instructions if recipe.instructions else ""

    ingredients_xml = ET.SubElement(recipe_xml, "ingredients")

    for product_name, product_quantity in recipe.ingredients.items():
        ingredient_xml = ET.SubElement(ingredients_xml, "ingredient")

        ing_name_xml = ET.SubElement(ingredient_xml, "name", lang=language)
        ing_name_xml.text = product_name

        ing_quantity_xml = ET.SubElement(ingredient_xml, "quantity", lang=language)
        ing_quantity_xml.text = product_quantity

    with open(filename, 'wb') as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)


def update_recipe_in_xml(filename: str, recipe: Recipe, language: str = "en") -> None:
    """
    Updates an existing recipe in the xml file.
    """
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
    except FileNotFoundError as e:
        print(f"File not found - {e}")
        return
    except ET.ParseError as e:
        print(f"Not a valid XML error - {e}")
        return

    recipe_xml = root.find(f"recipe[id='{recipe.id}']")
    if recipe_xml is None:
        print(f"Recipe with id {recipe.id} not found.")
        return

    duration_xml = recipe_xml.find("duration")
    if duration_xml is not None:
        duration_xml.text = recipe.duration

    name_xml = recipe_xml.find(f"name[@lang='{language}']")
    if name_xml is not None:
        name_xml.text = recipe.name
    else:
        name_xml = ET.SubElement(recipe_xml, "name", lang=language)
        name_xml.text = recipe.name

    portions_xml = recipe_xml.find(f"portions[@lang='{language}']")
    if portions_xml is not None:
        portions_xml.text = str(recipe.portions)
    else:
        portions_xml = ET.SubElement(recipe_xml, "portions", lang=language)
        portions_xml.text = str(recipe.portions)

    type_xml = recipe_xml.find(f"type[@lang='{language}']")
    if type_xml is not None:
        type_xml.text = recipe.mealtype
    else:
        type_xml = ET.SubElement(recipe_xml, "type", lang=language)
        type_xml.text = recipe.mealtype

    vegetarian_xml = recipe_xml.find("vegetarian")
    if vegetarian_xml is not None:
        vegetarian_xml.text = "true" if recipe.vegetarian else "false"

    instructions_xml = recipe_xml.find(f"instructions[@lang='{language}']")
    if instructions_xml is not None:
        instructions_xml.text = recipe.instructions if recipe.instructions else ""
    else:
        instructions_xml = ET.SubElement(recipe_xml, "instructions", lang=language)
        instructions_xml.text = recipe.instructions if recipe.instructions else ""

    ingredients_xml = recipe_xml.find("ingredients")
    if ingredients_xml is not None:
        ingredients_xml.clear()
    else:
        ingredients_xml = ET.SubElement(recipe_xml, "ingredients")

    for product_name, product_quantity in recipe.ingredients.items():
        ingredient_xml = ET.SubElement(ingredients_xml, "ingredient")
        ing_name_xml = ET.SubElement(ingredient_xml, "name", lang=language)
        ing_name_xml.text = product_name
        ing_quantity_xml = ET.SubElement(ingredient_xml, "quantity", lang=language)
        ing_quantity_xml.text = product_quantity

    with open(filename, 'wb') as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)


def delete_recipe_from_xml(filename: str, recipe: Recipe) -> None:
    """
    Deletes a recipe from the xml file by its id.
    """
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
    except FileNotFoundError as e:
        print(f"File not found - {e}")
        return
    except ET.ParseError as e:
        print(f"Not a valid XML error - {e}")
        return

    recipe_xml = root.find(f"recipe[id='{recipe.id}']")
    if recipe_xml is not None:
        root.remove(recipe_xml)
    else:
        print(f"Recipe with id {recipe.id} not found.")
        return

    with open(filename, 'wb') as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":  # quick test
    r = load_recipes_from_xml("recipes.xml", "pl")
    print(r)
