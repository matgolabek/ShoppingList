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
from kivy.properties import StringProperty
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, OneLineAvatarIconListItem, IRightBodyTouch, TwoLineListItem, ImageLeftWidget
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_hex_from_color
from kivymd.uix.fitimage import FitImage

import os
import numpy as np
from info import Info


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    """Niestandardowy kontener na checkbox po prawej stronie listy."""
    pass


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
        self.checkboxes = {}

        self.layout = MDBoxLayout(orientation='vertical', padding=(dp(10), dp(10), dp(10), dp(10)))

        self.toolbar = MDTopAppBar()
        self.layout.add_widget(self.toolbar)

        self.recipe_list = MDList()

        self.scrollview = MDScrollView()
        self.scrollview.add_widget(self.recipe_list)
        self.layout.add_widget(self.scrollview)

        self.proceed_button = MDRaisedButton(text=self.lang.get_string("proceed"), size_hint=(1, None), on_release=self.show_summary, halign="center")
        self.layout.add_widget(self.proceed_button)

        self.add_widget(self.layout)

        self.populate_list()

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

    def populate_list(self):
        """
        Iteruje przez listę przepisów i dodaje je jako widżety do MDList.
        """
        # Czyścimy listę na wypadek, gdyby metoda była wywoływana ponownie
        self.recipe_list.clear_widgets()
        
        for recipe in self.recipes:
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
