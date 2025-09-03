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
        