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
from kivymd.uix.list import MDList, OneLineIconListItem, OneLineAvatarIconListItem, IconLeftWidget, TwoLineListItem
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window

import numpy as np
from info import Info


class ShoppingCartScreen(MDScreen):
    def __init__(self, info, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.info = info
        self.lang = info.language
        self.lang.register_observer(self)

        self.layout = MDBoxLayout(orientation='vertical', padding=(dp(10), dp(10), dp(10), dp(10)))

        self.toolbar = MDTopAppBar()
        self.layout.add_widget(self.toolbar)

        self.scrollview = MDScrollView()
        self.layout.add_widget(self.scrollview)

        self.proceed_button = MDRaisedButton(text=self.lang.get_string("proceed"), size_hint=(1, None), on_release=self.show_summary, halign="center")
        self.layout.add_widget(self.proceed_button)

        self.add_widget(self.layout)

    def update_translation(self):
        self.proceed_button.text = self.lang.get_string("proceed")

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
            on_release=self.toggle_lang_options
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
            
            icon = IconLeftWidget(icon="radio-box-blank")
            item.add_widget(icon)
            
            self.lang_option_widgets.append({"item": item, "icon": icon, "code": code})
            
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
            self.update_radio_buttons()

    def select_language(self, lang_code):
        """
        Called after selecting a specific language from the expanded list.
        """
        self.lang.set_language(lang_code)
        # Po wybraniu języka, automatycznie schowaj opcje
        if self.lang_options_visible:
            self.toggle_lang_options(None)

    def update_radio_buttons(self):
        """
        Updates the state of the radio buttons.
        """
        for data in self.lang_option_widgets:
            is_selected = (data["code"] == self.lang.current_language)
            data["icon"].icon = "radio-box-marked" if is_selected else "radio-box-blank"

    def update_translation(self):
        """
        Updates all texts on the screen after changing the language.
        """
        self.title.text = self.lang.get_string("settings")
        
        self.language_button.text = self.lang.get_string("language")
        self.language_button.secondary_text = self.lang.get_string(self.languages_map[self.lang.current_language])

        for data in self.lang_option_widgets:
            string_id = self.languages_map[data["code"]]
            data["item"].text = self.lang.get_string(string_id)
        
        self.update_radio_buttons()

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
