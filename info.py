from language import Language
from recipes import load_recipes_from_xml


class Info:
    def __init__(self):
        self.language = Language("languagepack.xml")
        self.email = ""
        self.constant_shopping_list_elements = ""

    def get_recipes(self):
        return load_recipes_from_xml("recipes.xml", language=self.language.current_language)
    
    def get_constant_shopping_list_elements(self):
        return self.constant_shopping_list_elements