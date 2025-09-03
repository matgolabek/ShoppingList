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