from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.button import MDIconButton
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.tab import MDTabs
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, OneLineAvatarIconListItem, IRightBodyTouch, TwoLineListItem, ImageLeftWidget
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_hex_from_color
from kivymd.uix.fitimage import FitImage

import os
import numpy as np
from info import Info
from recipe import Recipe


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    """Niestandardowy kontener na checkbox po prawej stronie listy."""
    pass


class FilterDialogContent(MDBoxLayout):
    """Niestandardowa, przewijalna zawartość dla okna dialogowego z filtrami."""
    def __init__(self, all_recipes, current_meal_types, current_min_time, current_max_time, **kwargs):
        super().__init__(**kwargs)
        self._is_updating = False
        self.size_hint_y = None
        self.height = Window.height * 0.5
        self.orientation = "vertical"
        scroll_view = MDScrollView()
        content_layout = MDBoxLayout(
            orientation="vertical", spacing="15dp", padding="15dp", adaptive_height=True
        )

        # --- SEKCJA 1: CHECKBOXY DLA TYPU POSIŁKU ---
        # Dodajemy widżety do WEWNĘTRZNEGO layoutu (content_layout)
        content_layout.add_widget(MDLabel(text="Typ posiłku:", bold=True, adaptive_height=True))
        
        self.meal_type_checkboxes = {}
        meal_types = sorted(list(set([r.mealtype for r in all_recipes])))
        for meal_type in meal_types:
            item_layout = MDBoxLayout(adaptive_height=True)
            checkbox = MDCheckbox(
                size_hint_x=None,
                width="48dp",
                active=meal_type in current_meal_types
            )
            self.meal_type_checkboxes[meal_type] = checkbox
            
            item_layout.add_widget(checkbox)
            item_layout.add_widget(MDLabel(text=meal_type, adaptive_height=True))
            content_layout.add_widget(item_layout)


class FilterDialogContent(MDBoxLayout):
    """Zawartość okna z filtrami, używająca tylko niezawodnych checkboxów."""
    def __init__(self, all_recipes, current_meal_types, current_time_ranges, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = Window.height * 0.8
        self.orientation = "vertical"
        scroll_view = MDScrollView()
        content_layout = MDBoxLayout(
            orientation="vertical", spacing="15dp", padding="15dp", adaptive_height=True
        )

        # --- SEKCJA 1: CHECKBOXY DLA TYPU POSIŁKU (bez zmian) ---
        content_layout.add_widget(MDLabel(text="Typ posiłku:", bold=True, adaptive_height=True))
        self.meal_type_checkboxes = {}
        meal_types = sorted(list(set([r.mealtype for r in all_recipes])))
        for meal_type in meal_types:
            item_layout = MDBoxLayout(adaptive_height=True)
            checkbox = MDCheckbox(size_hint_x=None, width="48dp", active=meal_type in current_meal_types)
            self.meal_type_checkboxes[meal_type] = checkbox
            item_layout.add_widget(checkbox)
            item_layout.add_widget(MDLabel(text=meal_type, adaptive_height=True))
            content_layout.add_widget(item_layout)

        # --- SEKCJA 2: CHECKBOXY DLA PRZEDZIAŁÓW CZASOWYCH ---
        content_layout.add_widget(MDLabel(text="Czas przygotowania (min):", bold=True, adaptive_height=True))
        
        # Definiujemy nasze przedziały
        self.time_ranges = {
            "0-15 min": (0, 15),
            "15-30 min": (15, 30),
            "30-60 min": (30, 60),
            "60+ min": (60, 9999) # Używamy dużej liczby jako "nieskończoność"
        }
        self.time_range_checkboxes = {}

        for text, (min_val, max_val) in self.time_ranges.items():
            item_layout = MDBoxLayout(adaptive_height=True)
            checkbox = MDCheckbox(
                size_hint_x=None, 
                width="48dp",
                active=(min_val, max_val) in current_time_ranges # Sprawdź, czy ten przedział był już zaznaczony
            )
            # Przechowujemy referencję do checkboxa
            self.time_range_checkboxes[text] = checkbox
            
            item_layout.add_widget(checkbox)
            item_layout.add_widget(MDLabel(text=text, adaptive_height=True))
            content_layout.add_widget(item_layout)
        
        scroll_view.add_widget(content_layout)
        self.add_widget(scroll_view)


    def update_textfields_from_slider(self, instance, value):
        """Aktualizuje pola tekstowe, gdy użytkownik przesuwa suwak."""
        if self._is_updating:
            return
        self._is_updating = True
        self.min_time_textfield.text = f"{int(value[0])}"
        self.max_time_textfield.text = f"{int(value[1])}"
        self._is_updating = False

    def update_slider_from_textfields(self, instance, text):
        """Aktualizuje suwak, gdy użytkownik wpisuje tekst w polach."""
        if self._is_updating:
            return
        self._is_updating = True
        try:
            min_val = int(self.min_time_textfield.text) if self.min_time_textfield.text else self.time_slider.min
            max_val = int(self.max_time_textfield.text) if self.max_time_textfield.text else self.time_slider.max
            
            # Zapewnij, że min <= max
            if min_val > max_val:
                min_val, max_val = max_val, min_val
                
            self.time_slider.value = [min_val, max_val]
        except ValueError:
            pass
        self._is_updating = False



class DialogContent(MDBoxLayout):
    """
    Ulepszona, niestandardowa zawartość okienka dialogowego z galerią zdjęć,
    działającym markdownem i responsywną wysokością.
    """
    def __init__(self, recipe, lang, **kwargs):
        super().__init__(**kwargs)

        # Pobieramy aktualnie uruchomioną aplikację, aby dostać się do jej motywu
        app = MDApp.get_running_app()
        # Konwertujemy kolory motywu na format HEX, zrozumiały dla markup
        primary_hex_color = get_hex_from_color(app.theme_cls.primary_color)
        secondary_hex_color = get_hex_from_color(app.theme_cls.secondary_text_color)
        
        self.lang = lang
        self.size_hint_y = None
        self.height = Window.height * 0.6
        self.orientation = "vertical"
        self.spacing = "12dp"
        # Usunęliśmy adaptive_height, aby pozwolić ScrollView na rozciągnięcie się
        
        # --- SEKCJA 1: POZIOMA GALERIA ZDJĘĆ ---
        gallery_path = f"imgs/recipe{recipe.id}/"
        if os.path.exists(gallery_path):
            # Kontener na galerię, o stałej wysokości
            gallery_scroll = MDScrollView(
                size_hint_y=None,
                height="120dp",
                do_scroll_x=True, # Włącz przewijanie w poziomie
                do_scroll_y=False # Wyłącz przewijanie w pionie
            )
            # Layout wewnątrz, który będzie się rozszerzał w poziomie
            gallery_layout = MDBoxLayout(
                orientation='horizontal',
                adaptive_width=True, # Szerokość dopasuje się do liczby zdjęć
                spacing="10dp"
            )

            for image_name in os.listdir(gallery_path):
                image_path = os.path.join(gallery_path, image_name)
                gallery_layout.add_widget(
                    FitImage(
                        source=image_path,
                        size_hint_x=None,
                        width="120dp" # Każde zdjęcie ma taką samą szerokość
                    )
                )
            
            gallery_scroll.add_widget(gallery_layout)
            self.add_widget(gallery_scroll)

        # --- SEKCJA 2: PIONOWE SZCZEGÓŁY PRZEPISU (PRZEWIJANE) ---
        # Ten ScrollView zajmie resztę dostępnego miejsca
        details_scroll = MDScrollView()
        content = MDBoxLayout(orientation='vertical', adaptive_height=True, padding="15dp", spacing="10dp")

        ingredients_text = "\n".join([f"- {key}: {value}" for key, value in recipe.ingredients.items()]) or self.lang.get_string("no_ingredients")

        # Tworzymy etykiety z włączoną opcją MARKUP=TRUE
        portions_text = f"[color={primary_hex_color}]{self.lang.get_string('portions')}:[/color] [color={secondary_hex_color}]{recipe.portions}[/color]"
        content.add_widget(MDLabel(text=portions_text, markup=True, adaptive_height=True))
        duration_text = f"[color={primary_hex_color}]{self.lang.get_string('duration')}:[/color] [color={secondary_hex_color}]{recipe.duration}[/color]"
        content.add_widget(MDLabel(text=duration_text, markup=True, adaptive_height=True))
        ingredients_pretext = f"[color={primary_hex_color}]{self.lang.get_string('ingredients')}:\n[/color] [color={secondary_hex_color}]{ingredients_text}[/color]"
        content.add_widget(MDLabel(text=ingredients_pretext, markup=True, adaptive_height=True))
        instructions_text = f"[color={primary_hex_color}]{self.lang.get_string('instructions')}:[/color]"
        content.add_widget(MDLabel(text=instructions_text, markup=True, adaptive_height=True))
        content.add_widget(MDLabel(text=recipe.instructions or self.lang.get_string("no_instructions"), markup=True, adaptive_height=True))

        details_scroll.add_widget(content)
        self.add_widget(details_scroll)


class ShoppingCartScreen(MDScreen):
    def __init__(self, info, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.dialog = None
        self.info = info
        self.lang = info.language
        self.lang.register_observer(self)

        self.recipes = info.get_recipes()
        self.all_recipes = info.get_recipes()
        self.checkboxes = {}

        # Przechowujemy aktualny stan filtrów
        self.active_meal_type_filters = [] # Zamiast pojedynczej wartości
        self.active_time_ranges = [] 
        self.search_query = ""

        self.layout = MDBoxLayout(orientation='vertical', padding=(dp(10), dp(10), dp(10), dp(10)))

        self.toolbar = MDTopAppBar(elevation=4)
        self.set_default_toolbar_items()
        self.layout.add_widget(self.toolbar)

        self.recipe_list = MDList()

        self.scrollview = MDScrollView()
        self.scrollview.add_widget(self.recipe_list)
        self.layout.add_widget(self.scrollview)

        self.proceed_button = MDRaisedButton(text=self.lang.get_string("proceed"), size_hint=(1, None), on_release=self.show_summary, halign="center")
        self.layout.add_widget(self.proceed_button)

        self.add_widget(self.layout)

        self.populate_list(self.all_recipes)

    def set_default_toolbar_items(self):
        """Ustawia standardowe ikony na pasku narzędzi."""
        self.toolbar.right_action_items = [
            ["magnify", lambda x: self.enter_search_mode()],
            ["filter-variant", lambda x: self.open_filter_dialog()], # <-- ZMIANA
        ]
        self.toolbar.left_action_items = []

    def enter_search_mode(self, *args):
        """Zamienia tytuł i ikony na pole tekstowe do wyszukiwania."""
        self.toolbar.left_action_items = [
            ["arrow-left", lambda x: self.exit_search_mode()]
        ]
        self.toolbar.right_action_items = []
        
        self.search_field = MDTextField(
            hint_text="Szukaj dań lub składników...",
            mode="fill",
            pos_hint={'center_y': 0.5},
            on_text_validate=self.perform_search, # Opcjonalnie: szukaj po naciśnięciu Enter
            text=self.search_query # Przywróć poprzednie zapytanie
        )
        # Reaguj na każdą zmianę tekstu
        self.search_field.bind(text=self.perform_search)
        
        self.toolbar.title = ""
        self.toolbar.add_widget(self.search_field)

    def exit_search_mode(self, *args):
        """Przywraca domyślny wygląd paska narzędzi."""
        self.toolbar.remove_widget(self.search_field)
        self.toolbar.title = "Shopping Cart"
        self.set_default_toolbar_items()

    def perform_search(self, instance, text=""):
        """Zapisuje frazę i uruchamia filtrowanie."""
        self.search_query = instance.text.lower()
        self.apply_filters_and_search()

    def open_filter_dialog(self):
        """Otwiera okno dialogowe z zaawansowanymi filtrami."""
        # Stwórz i zapisz referencję do zawartości okna
        self.current_filter_content = FilterDialogContent(
            all_recipes=self.all_recipes,
            current_meal_types=self.active_meal_type_filters,
            current_time_ranges=self.active_time_ranges
        )
        
        self.filter_dialog = MDDialog(
            title="Filtry",
            type="custom",
            content_cls=self.current_filter_content, # Użyj zapisanej zawartości
            buttons=[
                MDFlatButton(text="ANULUJ", on_release=lambda x: self.filter_dialog.dismiss()),
                # Przycisk teraz bezpośrednio wywołuje metodę, bez przekazywania argumentów
                MDRaisedButton(text="ZASTOSUJ", on_release=self.apply_dialog_filters),
            ]
        )
        self.filter_dialog.open()

    def apply_dialog_filters(self, *args): # Przyjmuje teraz *args, bo jest wywoływana przez on_release
        """Pobiera dane z zapisanej zawartości okna i aktualizuje listę."""
        # Odwołaj się do zapisanej zawartości zamiast argumentu
        content = self.current_filter_content
        
        # Odczytaj stan checkboxów typu posiłku
        self.active_meal_type_filters = [
            meal_type for meal_type, checkbox in content.meal_type_checkboxes.items() if checkbox.active
        ]
        
        # Odczytaj stan checkboxów z przedziałami czasu
        self.active_time_ranges = []
        for text, checkbox in content.time_range_checkboxes.items():
            if checkbox.active:
                self.active_time_ranges.append(content.time_ranges[text])
        
        self.apply_filters_and_search()
        self.filter_dialog.dismiss()


    def apply_filters_and_search(self):
        """Filtruje listę na podstawie listy typów i suwaka czasu."""
        results = self.all_recipes

        # 1. Filtrowanie po typie posiłku (teraz sprawdza, czy typ jest na liście)
        if self.active_meal_type_filters:
            results = [
                recipe for recipe in results 
                if recipe.mealtype in self.active_meal_type_filters
            ]

        # 2. Filtrowanie po czasie przygotowania
        if self.active_time_ranges:
            # Przefiltruj, jeśli jakikolwiek przedział jest aktywny
            filtered_results = []
            for recipe in results:
                # Sprawdź, czy czas przepisu pasuje do KTÓREGOKOLWIEK z zaznaczonych przedziałów
                is_match = any(
                    min_t < recipe.duration_int <= max_t for min_t, max_t in self.active_time_ranges
                )
                if is_match:
                    filtered_results.append(recipe)
            results = filtered_results
            
        # 3. Wyszukiwanie tekstowe (bez zmian)
        if self.search_query:
            results = [
                recipe for recipe in results
                if self.search_query in recipe.name.lower() or 
                any(self.search_query in ingredient.lower() for ingredient in recipe.ingredients.keys())
            ]

        self.populate_list(results)

    def show_recipe_popup(self, recipe):
            """Tworzy i wyświetla popup ze szczegółami przepisu."""
            checkbox = self.checkboxes.get(recipe.id)
            button_text = self.lang.get_string("add_to_list") if checkbox and not checkbox.active else self.lang.get_string("remove_from_list")
            self.dialog = MDDialog(
                title=recipe.name,
                type="custom",
                content_cls=DialogContent(recipe=recipe, lang=self.lang),
                buttons=[
                    MDRaisedButton(
                        text=button_text,
                        md_bg_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.toggle_checkbox_and_dismiss(recipe)
                    ),
                    MDFlatButton(
                        text=self.lang.get_string("close"),
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ],
            )
            self.dialog.title = recipe.name
            self.dialog.content_cls = DialogContent(recipe=recipe, lang=self.lang)
            self.dialog.open()

    def populate_list(self, recipes_to_display: list[Recipe] = None):
        """
        Iteruje przez listę przepisów i dodaje je jako widżety do MDList.
        """
        if recipes_to_display is None:
            recipes_to_display = self.all_recipes
        # Czyścimy listę na wypadek, gdyby metoda była wywoływana ponownie
        self.recipe_list.clear_widgets()
        
        for recipe in recipes_to_display:
            image_path = f"imgs/recipe{recipe.id}/0.png"      
            image_widget = ImageLeftWidget(source=image_path)

            main_ingredients = f"{list(recipe.ingredients.keys())[0]}, {list(recipe.ingredients.keys())[1]}, {list(recipe.ingredients.keys())[2]}..." if len(recipe.ingredients) > 3 else ", ".join(list(recipe.ingredients.keys()))

            list_item = TwoLineAvatarIconListItem(
                text=f"{recipe.name}",
                secondary_text=f"{main_ingredients}",
            )

            list_item.on_release = lambda rec=recipe: self.show_recipe_popup(rec)
            list_item.secondary_font_style = "Caption"

            # Dodajemy ikonę do elementu listy
            list_item.add_widget(image_widget)

            checkbox = RightCheckbox()
            checkbox.bind(active=lambda instance, value, r=recipe: self.on_checkbox_active(instance, value, r))
            if recipe.id in self.checkboxes.keys() and self.checkboxes[recipe.id].active:
                checkbox.active = True
            self.checkboxes[recipe.id] = checkbox
            list_item.add_widget(checkbox)
            # Dodajemy gotowy element do naszej listy MDList
            self.recipe_list.add_widget(list_item)

    def toggle_checkbox_and_dismiss(self, recipe):
        """Znajduje odpowiedni checkbox, przełącza jego stan i zamyka dialog."""
        checkbox_to_toggle = self.checkboxes.get(recipe.id)
        if checkbox_to_toggle:
            # Przełącz stan checkboxa na przeciwny
            checkbox_to_toggle.active = not checkbox_to_toggle.active
        
        self.dialog.dismiss()

    def on_checkbox_active(self, checkbox, value, recipe):
        """
        Wywoływana, gdy checkbox zostaje zaznaczony lub odznaczony.
        
        :param checkbox: instancja checkboxa, która wywołała zdarzenie
        :param value: True, jeśli zaznaczony, False, jeśli odznaczony
        :param recipe: obiekt Recipe powiązany z tym checkboxem
        """
        pass

    def update_translation(self):
        self.proceed_button.text = self.lang.get_string("proceed")
        self.recipes = self.info.get_recipes()
        self.populate_list()

    def show_summary(self, *args):
        pass

class FreeViewScreen(MDScreen):
    def __init__(self, info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.info = info
        self.lang = info.language
        self.lang.register_observer(self)

        self.layout = MDBoxLayout(orientation='vertical', padding=(dp(10), dp(10), dp(10), dp(10)))

        self.title = MDLabel(text=self.lang.get_string("free_view"), halign='center', font_style='H4')
        self.layout.add_widget(self.title)

        self.add_widget(self.layout)

    def update_translation(self):
        self.title.text = self.lang.get_string("free_view")


class SettingsScreen(MDScreen):
    def __init__(self, info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.info = info
        self.lang = info.language
        self.lang.register_observer(self)

        self.lang_options_visible = False

        self.layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))

        self.title = MDLabel(
            text=self.lang.get_string("settings"),
            halign='center',
            font_style='H4'
        )
        self.layout.add_widget(self.title)
        
        self.scrollview = MDScrollView()
        self.settings_list = MDList()

        self.language_button = TwoLineListItem(
            text=self.lang.get_string("language"),
            secondary_text=self.lang.get_string(f"{self.lang.current_language}"),
            on_release=self.toggle_lang_options
        )
        self.settings_list.add_widget(self.language_button)

        self.email_button = TwoLineListItem(
            text=self.lang.get_string("email"),
            secondary_text=self.lang.get_string(f"{self.info.email}"),
            # on_release=self.toggle_email_options
        )
        self.settings_list.add_widget(self.email_button)

        self.languages_map = {"pl": "polski", "en": "english"}
        self.lang_option_widgets = []
        
        for code, string_id in self.languages_map.items():
            item = OneLineAvatarIconListItem(
                text=self.lang.get_string(string_id),
                on_release=lambda x, lang_code=code: self.select_language(lang_code)
            )
            item.ids._left_container.padding = (dp(30), 0, 0, 0)
        
            
            self.lang_option_widgets.append({"item": item, "code": code})
            
        self.scrollview.add_widget(self.settings_list)
        self.layout.add_widget(self.scrollview)
        self.add_widget(self.layout)

    def toggle_lang_options(self, *args):
        """
        Shows or hides the language selection options.
        """
        if self.lang_options_visible:
            for widget_data in self.lang_option_widgets:
                self.settings_list.remove_widget(widget_data["item"])
            self.lang_options_visible = False
        else:
            button_index = self.settings_list.children.index(self.language_button)
            for widget_data in reversed(self.lang_option_widgets): # Dodajemy w odwróconej kolejności
                self.settings_list.add_widget(widget_data["item"], index=button_index)
            
            self.lang_options_visible = True

    def select_language(self, lang_code):
        """
        Called after selecting a specific language from the expanded list.
        """
        self.lang.set_language(lang_code)
        # Po wybraniu języka, automatycznie schowaj opcje
        if self.lang_options_visible:
            self.toggle_lang_options(None)

    def update_translation(self):
        """
        Updates all texts on the screen after changing the language.
        """
        self.title.text = self.lang.get_string("settings")
        
        self.language_button.text = self.lang.get_string("language")
        self.language_button.secondary_text = self.lang.get_string(self.languages_map[self.lang.current_language])

        self.email_button.text = self.lang.get_string("email")

        for data in self.lang_option_widgets:
            string_id = self.languages_map[data["code"]]
            data["item"].text = self.lang.get_string(string_id)
        

class MyApp(MDApp):

    def build(self):
        self.title = "TheCart"
        self.theme_cls.primary_palette = np.random.choice(["Cyan"])
        self.theme_cls.theme_style = np.random.choice(["Light"])
        Window.size = (315, 700)
        # Window.set_icon("cart.jpg")
        # Window.maximize()

        self.info = Info()

        shopping_cart_item = MDBottomNavigationItem(name="Shopping Cart", icon="cart-outline")
        shopping_cart_item.add_widget(ShoppingCartScreen(info=self.info, name="Shoping Cart"))

        free_view_item = MDBottomNavigationItem(name="Free View", icon="magnify")
        free_view_item.add_widget(FreeViewScreen(info=self.info, name="Free View"))

        settings_item = MDBottomNavigationItem(name="Settings", icon="cog-outline")
        settings_item.add_widget(SettingsScreen(info=self.info, name="Settings"))

        self.nav = MDBottomNavigation(panel_color=self.theme_cls.primary_color)
        
        self.nav.add_widget(shopping_cart_item)
        self.nav.add_widget(free_view_item)
        self.nav.add_widget(settings_item)

        return self.nav
    
MyApp().run()
