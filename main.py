from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivy.core.window import Window

from shoppingcart import ShoppingCartScreen
from freeview import FreeViewScreen
from settings import SettingsScreen

import pickle
import os

from info import Info


class MyApp(MDApp):

    def build(self):
        self.title = "TheCart"
        self.theme_cls.primary_palette = "Cyan"
        self.theme_cls.theme_style = "Light"
        Window.size = (315, 700)
        Window.set_icon("cart.jpg")

        self.save_file = "info.dat"

        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'rb') as f:
                    self.info = pickle.load(f)
            except Exception as e:
                self.info = Info()
        else:
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
    
    def on_stop(self):
        with open(self.save_file, 'wb') as f:
            pickle.dump(self.info, f)

if __name__ == "__main__":
    MyApp().run()
