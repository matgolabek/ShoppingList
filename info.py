from language import Language
from recipes import load_recipes_from_xml


class Info:
    def __init__(self):
        self.languagepack_file = "languagepack.xml"
        self.current_language = "en"
        self.language = Language(self.languagepack_file, self.current_language)
        self.email = ""
        self.send_option = "option-email"
        self.constant_shopping_list_elements = "=============\n"
        self.recipes_file = "recipes.xml"

    def get_recipes(self):
        return load_recipes_from_xml(self.recipes_file, language=self.language.current_language)

    def get_constant_shopping_list_elements(self):
        return self.constant_shopping_list_elements
    
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['language']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.language = Language(self.languagepack_file, self.current_language)