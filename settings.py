from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, OneLineAvatarIconListItem, TwoLineListItem, OneLineListItem
from kivy.metrics import dp
from kivy.core.window import Window

import os
import shutil


class SettingsScreen(MDScreen):
    def __init__(self, info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.info = info
        self.lang = info.language

        self.dialog = None
        self.email_dialog = None
        self.lang_options_visible = False
        self.sending_options_visible = False

        self.layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))

        self.title = MDLabel(
            text=self.lang.get_string("settings"),
            halign='center',
            font_style='H4',
            size_hint_y=None,
            height=dp(50)
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
            secondary_text=self.info.email,
            on_release=self.provide_email_info
        )
        self.settings_list.add_widget(self.email_button)

        self.sending_button = TwoLineListItem(
            text=self.lang.get_string("sending_option"),
            secondary_text=self.lang.get_string(self.info.send_option),
            on_release=self.toggle_sending_options
        )
        self.settings_list.add_widget(self.sending_button)

        self.default_list_button = TwoLineListItem(
            text=self.lang.get_string("default_list_elements"),
            secondary_text=self.lang.get_string(self.info.constant_shopping_list_elements.split()[0]),
            on_release=self.toggle_default_list_options
        )
        self.settings_list.add_widget(self.default_list_button)

        self.languages_map = {"pl": "polski", "en": "english"}
        self.lang_option_widgets = []
        
        for code, string_id in self.languages_map.items():
            item = OneLineAvatarIconListItem(
                text=self.lang.get_string(string_id),
                on_release=lambda x, lang_code=code: self.select_language(lang_code)
            )
            item.ids._left_container.padding = (dp(30), 0, 0, 0)
        
            
            self.lang_option_widgets.append({"item": item, "code": code})

        self.sending_option_widgets = []
        sending_options = ["option-none", "option-email"]

        for option_name in sending_options:
            item = OneLineAvatarIconListItem(
                text=self.lang.get_string(option_name),
                on_release=lambda x, option=option_name: self.select_sending_option(option),
                id=option_name
            )
            item.ids._left_container.padding = (dp(30), 0, 0, 0)
            self.sending_option_widgets.append(item)
        self.reset_option = OneLineListItem(text=self.lang.get_string("reset_database_title"), on_release=self.reset_the_database)
        self.settings_list.add_widget(self.reset_option)
            
        self.scrollview.add_widget(self.settings_list)
        self.layout.add_widget(self.scrollview)
        self.add_widget(self.layout)

    def reset_the_database(self, *args):
        """
        Resets the recipes database by deleting the XML file.
        """
        self.dialog = MDDialog(
            title=self.lang.get_string("reset_database_title"),
            text=self.lang.get_string("reset_database_confirm"),
            buttons=[
                MDFlatButton(
                    text=self.lang.get_string("cancel"),
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text=self.lang.get_string("reset"),
                    on_release=lambda x: self._reset_database_confirm()
                ),
            ],
        )
        self.dialog.open()

    def _reset_database_confirm(self):
        if os.path.exists("recipes.xml"):
            shutil.copyfile("recipes_original.xml", "recipes.xml")
        for folder in os.listdir("imgs"):
            if folder.startswith("recipe"):
                try:
                    n = int(folder.replace("recipe", ""))
                    if n >= 1000 and os.path.isdir(os.path.join("imgs", folder)):
                        for filename in os.listdir(os.path.join("imgs", folder)):
                            file_path = os.path.join("imgs", folder, filename)
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                        shutil.rmtree(os.path.join("imgs", folder))
                except ValueError:
                    continue

        all_recipes = self.info.get_recipes()
        MDApp.get_running_app().scs.populate_list(all_recipes)
        MDApp.get_running_app().fvi.populate_list(all_recipes)
        self.dialog.dismiss()
        self.dialog = None

    def toggle_default_list_options(self, *args):
        """
        Creates and opens a popup dialog to edit constant shopping list elements.
        """

        text_field = MDTextField(
            text=self.info.constant_shopping_list_elements,
            multiline=True,
            mode="fill",
            font_name="consola.ttf",
            size_hint_y=None
        )
        text_field.bind(minimum_height=text_field.setter('height'))

        scroll_view = MDScrollView(
            size_hint_y=None,
            height=Window.height * 0.6  # Wysokość okna, można dostosować
        )
        scroll_view.add_widget(text_field)

        self.dialog = MDDialog(
            title=self.lang.get_string("default_list_elements"),
            type="custom",
            content_cls=scroll_view,
            buttons=[
                MDFlatButton(
                    text=self.lang.get_string("cancel"),
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text=self.lang.get_string("save"),
                    on_release=lambda x: self.save_default_list(text_field)
                ),
            ],
        )

        self.dialog.open()

    def save_default_list(self, text_field):
        """
        Saves the edited constant shopping list elements and updates the main button text.
        """
        self.info.constant_shopping_list_elements = text_field.text

        self.default_list_button.secondary_text = self.info.constant_shopping_list_elements.split()[0] if self.info.constant_shopping_list_elements else ""

        self.dialog.dismiss()
        self.dialog = None

    def toggle_sending_options(self, *args):
        """
        Pokazuje lub ukrywa opcje wyboru sposobu wysyłania.
        """
        if self.sending_options_visible:
            for widget in self.sending_option_widgets:
                self.settings_list.remove_widget(widget)
            self.sending_options_visible = False
        else:
            button_index = self.settings_list.children.index(self.sending_button)
            for widget in reversed(self.sending_option_widgets):
                self.settings_list.add_widget(widget, index=button_index)
            
            self.sending_options_visible = True

    def select_sending_option(self, option):
        self.info.send_option = option
        self.sending_button.secondary_text = self.lang.get_string(option.lower())
        self.toggle_sending_options()

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
        self.info.current_language = lang_code
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
        if self.email_dialog is not None:
            self.email_dialog.title = self.lang.get_string("provide_email")
            self.email_field.hint_text = self.lang.get_string("email")
            self.email_dialog.buttons[0].text = self.lang.get_string("cancel")
            self.email_dialog.buttons[1].text = self.lang.get_string("apply")


        self.sending_button.text = self.lang.get_string("sending_option")
        self.sending_button.secondary_text = self.lang.get_string(self.info.send_option)

        self.default_list_button.text = self.lang.get_string("default_list_elements")

        for data in self.lang_option_widgets:
            string_id = self.languages_map[data["code"]]
            data["item"].text = self.lang.get_string(string_id)

        for widget in self.sending_option_widgets:
            widget.text = self.lang.get_string(widget.id)

        self.reset_option.text = self.lang.get_string("reset_database_title")

    def provide_email_info(self, *args):
        """
        Tworzy i wyświetla okno popup do wprowadzenia adresu e-mail.
        """
        if not self.email_dialog:
            self.email_field = MDTextField(
                hint_text=self.lang.get_string("email"),
                text=self.info.email,
                icon_right="email",
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                size_hint_x=None,
                width=300
            )

            self.email_dialog = MDDialog(
                title=self.lang.get_string("provide_email"),
                type="custom",
                content_cls=self.email_field,
                buttons=[
                    MDFlatButton(
                        text=self.lang.get_string("cancel"),
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.email_dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text=self.lang.get_string("apply"),
                        theme_text_color="Custom",
                        md_bg_color=self.theme_cls.primary_color,
                        on_release=self.get_email_and_close
                    ),
                ],
            )
        self.email_dialog.open()

    def get_email_and_close(self, instance):
        """
        Funkcja pomocnicza do pobierania e-maila i zamykania okna.
        """
        self.info.email = self.email_field.text
        self.email_button.secondary_text = self.info.email
        self.email_dialog.dismiss()

    def on_stop(self):
        """
        Metoda wywoływana przy zamykaniu aplikacji, aby wyczyścić dialog.
        """
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if self.email_dialog:
            self.email_dialog.dismiss()
            self.email_dialog = None