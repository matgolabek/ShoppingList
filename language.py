import xml.etree.ElementTree as ET

class Language:
    def __init__(self, filepath: str, current_language: str = "en"):
        self.translations = self._load_translations(filepath)
        self.current_language = current_language
        self.observers = []

    def _load_translations(self, filepath: str) -> dict:
        """
        Loading translations from XML.
        """
        translations = {}
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            for language in root.findall('language'):
                lang_name = language.get('name')
                translations[lang_name] = {}
                for string in language.findall('string'):
                    string_id = string.get('id')
                    translations[lang_name][string_id] = string.text
        except FileNotFoundError as e:
            print(f"Error: File not found {filepath} - {e}")
        except ET.ParseError as e:
            print(f"Error: Cannot parse file {filepath} - {e}")
        return translations

    def set_language(self, language):
        """
        Sets the current language.
        """
        if language in self.translations:
            self.current_language = language
            for observer in self.observers:
                observer.update_translation()
        else:
            print(f"Warning: Language '{language}' not found.")

    def register_observer(self, observer):
        """
        Registers a new UI element for notifications.
        """
        self.observers.append(observer)

    def unregister_observer(self, observer):
        """Unregisters a UI element."""
        self.observers.remove(observer)


    def get_string(self, string_id):
        """
        Retrieves the translated string for the current language.
        """
        if self.current_language and string_id in self.translations.get(self.current_language, {}):
            return self.translations[self.current_language][string_id]
        # Return key as fallback if translation does not exist
        return string_id