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
from kivymd.uix.relativelayout import MDRelativeLayout
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

from plyer import filechooser
import smtplib
import ssl
from email.message import EmailMessage
import json
import os
import numpy as np
from info import Info
from recipe import Recipe
from datetime import date


class RightTextFieldContainer(IRightBodyTouch, MDBoxLayout):
    adaptive_width = True


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    """
    Custom container for a checkbox on the right side of the list.
    """
    pass


class FilterDialogContent(MDBoxLayout):
    """
    Custom content for the filter dialog, using only reliable checkboxes.
    """
    def __init__(self, all_recipes, lang, current_meal_types, current_time_ranges, current_vegetarian_filter, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.lang = lang
        self.height = Window.height * 0.5
        self.orientation = "vertical"
        scroll_view = MDScrollView()
        content_layout = MDBoxLayout(
            orientation="vertical", spacing="15dp", padding="15dp", adaptive_height=True
        )

            # --- SECTION 1: CHECKBOXES FOR MEAL TYPE ---
        content_layout.add_widget(MDLabel(text=self.lang.get_string("meal_type"), bold=True, adaptive_height=True))
        self.meal_type_checkboxes = {}
        meal_types = sorted(list(set([r.mealtype for r in all_recipes])))
        for meal_type in meal_types:
            item_layout = MDBoxLayout(adaptive_height=True)
            checkbox = MDCheckbox(size_hint_x=None, width="48dp", active=meal_type in current_meal_types)
            self.meal_type_checkboxes[meal_type] = checkbox
            item_layout.add_widget(checkbox)
            item_layout.add_widget(MDLabel(text=self.lang.get_string(meal_type), adaptive_height=True))
            content_layout.add_widget(item_layout)

        # --- SECTION 2: CHECKBOXES FOR TIME RANGES ---
        content_layout.add_widget(MDLabel(text=self.lang.get_string("preparation_time"), bold=True, adaptive_height=True))

        # Define our time ranges
        self.time_ranges = {
            "0-15 min": (0, 15),
            "15-30 min": (15, 30),
            "30-60 min": (30, 60),
            "60+ min": (60, 9999) # We use a large number as "infinity"
        }
        self.time_range_checkboxes = {}

        for text, (min_val, max_val) in self.time_ranges.items():
            item_layout = MDBoxLayout(adaptive_height=True)
            checkbox = MDCheckbox(
                size_hint_x=None, 
                width="48dp",
                active=(min_val, max_val) in current_time_ranges # Check if this range was already selected
            )
            # Store a reference to the checkbox
            self.time_range_checkboxes[text] = checkbox
            
            item_layout.add_widget(checkbox)
            item_layout.add_widget(MDLabel(text=text, adaptive_height=True))
            content_layout.add_widget(item_layout)

        # --- SECTION 3: CHECKBOXES FOR VEGETARIAN OPTIONS ---
        content_layout.add_widget(MDLabel(text=self.lang.get_string("vegetarian"), bold=True, adaptive_height=True))
        item_layout = MDBoxLayout(adaptive_height=True)
        self.vegetarian_checkbox = MDCheckbox(
            size_hint_x=None,
            width="48dp",
            active=current_vegetarian_filter
        )
        item_layout.add_widget(self.vegetarian_checkbox)
        item_layout.add_widget(MDLabel(text=self.lang.get_string("yes"), adaptive_height=True))
        content_layout.add_widget(item_layout)

        scroll_view.add_widget(content_layout)
        self.add_widget(scroll_view)


class SummaryDialogContent(MDBoxLayout):
    """
    Custom content for the summary dialog.
    """
    def __init__(self, all_recipes, checked_recipes, lang, **kwargs):
        super().__init__(**kwargs)
        self.checked_recipes = checked_recipes
        self.all_recipes = all_recipes
        self.text_fields = {}
        self.size_hint_y = None
        self.lang = lang
        self.height = Window.height * 0.5
        self.orientation = "vertical"
        scroll_view = MDScrollView()
        content_layout = MDBoxLayout(
            orientation="vertical", spacing="40dp", padding="15dp", adaptive_height=True
        )

        for recipe_id in self.checked_recipes:
            recipe = self.all_recipes[recipe_id]
            image_path = f"imgs/recipe{recipe.id}/0.png"
            image_widget = ImageLeftWidget(source=image_path)

            main_ingredients = f"{list(recipe.ingredients.keys())[0]}, {list(recipe.ingredients.keys())[1]}, {list(recipe.ingredients.keys())[2]}..." if len(recipe.ingredients) > 3 else ", ".join(list(recipe.ingredients.keys()))

            list_item = MDBoxLayout(
                adaptive_height=True,
                spacing=dp(10)
            )

            list_item.add_widget(image_widget)

            text_container = MDBoxLayout(
                orientation='vertical',
                adaptive_height=True,
                pos_hint={'center_y': 0.5}
            )
            text_container.add_widget(
                MDLabel(text=f"{recipe.name}", adaptive_height=True)
            )
            main_ingredients = f"{list(recipe.ingredients.keys())[0]}, {list(recipe.ingredients.keys())[1]}, ..." if len(recipe.ingredients) > 2 else ", ".join(list(recipe.ingredients.keys()))
            text_container.add_widget(
                MDLabel(
                    text=f"{main_ingredients}",
                    theme_text_color="Secondary",
                    font_style="Caption",
                    adaptive_height=True
                )
            )
            list_item.add_widget(text_container)

            portions_field = MDTextField(
                text="1",
                size_hint_x=None,
                width=dp(30),
                max_text_length=1,
                halign="center",
                input_filter="int",
                pos_hint={'center_y': 0.5}
            )
            self.text_fields[recipe.id] = portions_field
            list_item.add_widget(portions_field)

            content_layout.add_widget(list_item)
        scroll_view.add_widget(content_layout)
        self.add_widget(scroll_view)


class DialogContent(MDBoxLayout):
    """
    Updated custom dialog content with image gallery, working markdown, and responsive height.
    """
    def __init__(self, recipe, lang, **kwargs):
        super().__init__(**kwargs)

        # Downloading the running app to get their theme
        app = MDApp.get_running_app()
        # Converting the theme colors to HEX format understood by markup
        primary_hex_color = get_hex_from_color(app.theme_cls.primary_color)
        secondary_hex_color = get_hex_from_color(app.theme_cls.secondary_text_color)
        
        self.lang = lang
        self.size_hint_y = None
        self.height = Window.height * 0.6
        self.orientation = "vertical"
        self.spacing = "12dp"

        # --- SECTION 1: IMAGE GALLERY ---
        gallery_path = f"imgs/recipe{recipe.id}/"
        if os.path.exists(gallery_path):
            # The gallery container with a fixed height
            gallery_scroll = MDScrollView(
                size_hint_y=None,
                height="120dp",
                do_scroll_x=True, # Enable horizontal scrolling
                do_scroll_y=False # Disable vertical scrolling
            )
            # Inner layout that will expand horizontally
            gallery_layout = MDBoxLayout(
                orientation='horizontal',
                adaptive_width=True, # Width will adapt to the number of images
                spacing="10dp"
            )

            for image_name in os.listdir(gallery_path):
                image_path = os.path.join(gallery_path, image_name)
                gallery_layout.add_widget(
                    FitImage(
                        source=image_path,
                        size_hint_x=None,
                        width="120dp" # Same width for all images
                    )
                )
            
            gallery_scroll.add_widget(gallery_layout)
            self.add_widget(gallery_scroll)

        # --- SECTION 2: VERTICAL RECIPE DETAILS (SCROLLABLE) ---
        # This ScrollView will take up the remaining available space
        details_scroll = MDScrollView()
        content = MDBoxLayout(orientation='vertical', adaptive_height=True, padding="15dp", spacing="10dp")

        ingredients_text = "\n".join([f"- {key}: {value}" for key, value in recipe.ingredients.items()]) or self.lang.get_string("no_ingredients")

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
        self.summary_text_fields = {}

        # Store the current filter states
        self.active_meal_type_filters = []
        self.active_time_ranges = [] 
        self.active_vegetarian_filter = False
        self.search_query = ""

        self.layout = MDBoxLayout(orientation='vertical', padding=(dp(10), dp(10), dp(10), dp(10)))

        self.toolbar = MDTopAppBar(
            elevation=4,
        )
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
        """
        Sets the default icons on the toolbar.
        """
        self.toolbar.right_action_items = [["filter-variant", lambda x: self.open_filter_dialog()]]
        self.toolbar.left_action_items = [["magnify", lambda x: self.enter_search_mode()]]

    def enter_search_mode(self, *args):
        """
        Changes the title and icons to a search text field.
        """
        self.toolbar.left_action_items = []
        self.toolbar.right_action_items = []

        self.middle_layout = MDBoxLayout(orientation="horizontal")

        go_back_button = MDIconButton(icon="arrow-left", pos_hint={"center_y": 1},
                                       on_release=self.exit_search_mode)
        self.middle_layout.add_widget(go_back_button)

        self.search_field = MDTextField(
            hint_text=self.lang.get_string("search_hint"),
            mode="round",
            size_hint_x=0.9,
            multiline=False,
            pos_hint={"center_y": 1},
            on_text_validate=self.perform_search,
            text=self.search_query,
            )
        # Respond for text changes
        self.search_field.bind(text=self.perform_search)

        self.middle_layout.add_widget(self.search_field)
        self.toolbar.add_widget(self.middle_layout)

    def exit_search_mode(self, *args):
        """
        Restores the default appearance of the toolbar.
        """
        self.toolbar.remove_widget(self.middle_layout)
        self.set_default_toolbar_items()

    def perform_search(self, instance, text=""):
        """
        Saves the query and triggers filtering.
        """
        self.search_query = instance.text.lower()
        self.apply_filters_and_search()

    def open_filter_dialog(self):
        """
        Opens a dialog with advanced filters.
        """
        # Create and store a reference to the dialog content
        self.current_filter_content = FilterDialogContent(
            all_recipes=self.all_recipes,
            lang=self.lang,
            current_meal_types=self.active_meal_type_filters,
            current_time_ranges=self.active_time_ranges,
            current_vegetarian_filter=self.active_vegetarian_filter
        )
        
        self.filter_dialog = MDDialog(
            title=self.lang.get_string("filters"),
            type="custom",
            content_cls=self.current_filter_content, # Użyj zapisanej zawartości
            buttons=[
                MDFlatButton(text=self.lang.get_string("cancel"), on_release=lambda x: self.filter_dialog.dismiss()),
                MDRaisedButton(text=self.lang.get_string("apply"), on_release=self.apply_dialog_filters),
            ]
        )
        self.filter_dialog.open()

    def apply_dialog_filters(self, *args):
        """
        Gets the data from the saved dialog content and updates the list.
        """
        content = self.current_filter_content

        # Read the state of the meal type checkboxes
        self.active_meal_type_filters = [
            meal_type for meal_type, checkbox in content.meal_type_checkboxes.items() if checkbox.active
        ]

        # Read the state of the time range checkboxes
        self.active_time_ranges = []
        for text, checkbox in content.time_range_checkboxes.items():
            if checkbox.active:
                self.active_time_ranges.append(content.time_ranges[text])

        # Read the state of the vegetarian checkbox
        self.active_vegetarian_filter = content.vegetarian_checkbox.active

        self.apply_filters_and_search()
        self.filter_dialog.dismiss()


    def apply_filters_and_search(self):
        """
        Filters the list based on the selected meal types and time ranges.
        """
        results = self.all_recipes

        # 1. Filtering by meal type (now checks if type is in the list)
        if self.active_meal_type_filters:
            results = [
                recipe for recipe in results 
                if recipe.mealtype in self.active_meal_type_filters
            ]

        # 2. Filtering by preparation time
        if self.active_time_ranges:
            # Filter if any range is active
            filtered_results = []
            for recipe in results:
                # Check if the recipe's duration matches ANY of the selected ranges
                is_match = any(
                    min_t < recipe.duration_int <= max_t for min_t, max_t in self.active_time_ranges
                )
                if is_match:
                    filtered_results.append(recipe)
            results = filtered_results

        # 3. Filtering by vegetarian
        if self.active_vegetarian_filter:
            results = [
                recipe for recipe in results
                if recipe.vegetarian
            ]

        # 4. Searching by text
        if self.search_query:
            results = [
                recipe for recipe in results
                if self.search_query in recipe.name.lower() or 
                any(self.search_query in ingredient.lower() for ingredient in recipe.ingredients.keys())
            ]

        self.populate_list(results)

    def show_recipe_popup(self, recipe):
            """
            Creates and shows a popup with the recipe details.
            """
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
        Iterates through the list of recipes and adds them as widgets to MDList.
        """
        if recipes_to_display is None:
            recipes_to_display = self.all_recipes
        # Clear the list in case the method is called again
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

            # Add the image to the list item
            list_item.add_widget(image_widget)

            checkbox = RightCheckbox()
            checkbox.bind(active=lambda instance, value, r=recipe: self.on_checkbox_active(instance, value, r))
            if recipe.id in self.checkboxes.keys() and self.checkboxes[recipe.id].active:
                checkbox.active = True
            self.checkboxes[recipe.id] = checkbox
            list_item.add_widget(checkbox)
            # Add the completed item to our MDList
            self.recipe_list.add_widget(list_item)

    def toggle_checkbox_and_dismiss(self, recipe):
        """
        Finds the corresponding checkbox, toggles its state, and closes the dialog.
        """
        checkbox_to_toggle = self.checkboxes.get(recipe.id)
        if checkbox_to_toggle:
            # Toggle the checkbox state
            checkbox_to_toggle.active = not checkbox_to_toggle.active
        
        self.dialog.dismiss()

    def on_checkbox_active(self, checkbox, value, recipe):
        """
        Called when the checkbox is checked or unchecked.

        :param checkbox: instance of the checkbox that triggered the event
        :param value: True if checked, False if unchecked
        :param recipe: Recipe object associated with this checkbox
        """
        pass

    def update_translation(self):
        self.proceed_button.text = self.lang.get_string("proceed")
        self.all_recipes = self.info.get_recipes()
        self.apply_filters_and_search()

    def show_save_dialog(self, *args):
        """
        Exports the shopping list to a text file.
        """
        try:
            filechooser.save_file(
                title=self.lang.get_string("save_file"),
                filters=["*.txt"],
                on_selection=self.handle_save_selection
            )
        except Exception as e:
            return

    def handle_save_selection(self, selection):
        """
        Saves the shopping list to the selected file path.
        """
        if not selection:
            return

        save_path = selection[0]
        print(f"Wybrano ścieżkę: {save_path}")

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(self.text_field.text)
        except Exception as e:
            return

    def show_summary(self, *args):
        """
        Opens a dialog with summary information.
        """
        self.current_summary_content = SummaryDialogContent(
            all_recipes=self.all_recipes,
            checked_recipes=[recipe_id for (recipe_id, recipe_checkbox) in self.checkboxes.items() if recipe_checkbox.active],
            lang=self.lang,
        )

        self.summary_dialog = MDDialog(
            title=self.lang.get_string("summary"),
            type="custom",
            content_cls=self.current_summary_content,
            buttons=[
                MDFlatButton(text=self.lang.get_string("cancel"), on_release=lambda x: self.summary_dialog.dismiss()),
                MDRaisedButton(text=self.lang.get_string("show_list"), on_release=lambda x: self.show_list_popup()),
            ]
        )
        self.summary_dialog.open()

    def show_list_popup(self):
        """
        Generates and shows the shopping list based on selected recipes and portions.
        """
        content = self.current_summary_content
        text_fields = {recipe_id: field for recipe_id, field in content.text_fields.items()}
        checkboxes = {recipe_id: checkbox for recipe_id, checkbox in self.checkboxes.items()}

        self.shopping_list_text = self.generate_shopping_list(text_fields, checkboxes)

        self.text_field = MDTextField(
            text=self.shopping_list_text or self.lang.get_string("no_items_selected"),
            multiline=True,
            mode="fill",
            font_name="consola.ttf",
            size_hint_y=None,
        )
        self.text_field.bind(minimum_height=self.text_field.setter('height'))

        scroll_view = MDScrollView(
            size_hint_y=None,
            height=Window.height * 0.7
        )
        scroll_view.add_widget(self.text_field)

        # Show the generated shopping list in a dialog
        self.list_dialog = MDDialog(
            title=self.lang.get_string("shopping_list"),
            type="custom",
            content_cls=scroll_view,
            buttons=[
                MDFlatButton(
                    text=self.lang.get_string("close"),
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.list_dialog.dismiss()
                ),
                MDRaisedButton(
                    text=self.lang.get_string("export"),
                    theme_text_color="Custom",
                    on_release=lambda x: self.show_save_dialog()
                ),
                MDRaisedButton(
                    text=self.lang.get_string("send"),
                    theme_text_color="Custom",
                    on_release=lambda x: self.send_email()
                )
            ]
        )
        self.list_dialog.open()
        self.summary_dialog.dismiss()

    def generate_shopping_list(self, text_fields, checkboxes):
        """
        Generates a consolidated shopping list based on selected recipes and their portions.

        :param text_fields: Dictionary mapping recipe IDs to their corresponding portion text fields.
        :param checkboxes: Dictionary mapping recipe IDs to their corresponding checkbox states.
        :return: A formatted string representing the shopping list.
        """
        consolidated_ingredients = {}

        for recipe_id, checkbox in checkboxes.items():
            if checkbox.active:
                # Get the number of portions from the corresponding text field
                portions_field = text_fields.get(recipe_id)
                try:
                    portions = int(portions_field.text) if portions_field and portions_field.text.isdigit() else 1
                except ValueError:
                    portions = 1  # Default to 1 if conversion fails

                if portions < 0:
                    portions = 0

                recipe = self.all_recipes[recipe_id]

                for ingredient_name, ingredient_quantity in recipe.ingredients.items():
                    # Split the quantity into numeric and unit parts
                    parts = ingredient_quantity.split(' ', 1)
                    if len(parts) == 2:
                        try:
                            quantity = float(parts[0])
                            unit = parts[1]
                        except ValueError:
                            quantity = 0
                            unit = ingredient_quantity
                    else:
                        try:
                            quantity = float(parts[0])
                            unit = ""
                        except ValueError:
                            quantity = 0
                            unit = ingredient_quantity

                    total_quantity = quantity * portions

                    if ingredient_name in consolidated_ingredients:
                        existing_quantity, existing_unit = consolidated_ingredients[ingredient_name]
                        if existing_unit == unit:
                            consolidated_ingredients[ingredient_name] = (existing_quantity + total_quantity, unit)
                        else:
                            # If units differ, we can choose to concatenate or handle differently
                            consolidated_ingredients[ingredient_name] = (f"{existing_quantity} {existing_unit} + {total_quantity} {unit}", "")
                    else:
                        consolidated_ingredients[ingredient_name] = (total_quantity, unit)

        # Format the shopping list as a string
        shopping_list_lines = []
        for ingredient_name, (quantity, unit) in consolidated_ingredients.items():
            if isinstance(quantity, float) and quantity.is_integer():
                quantity = int(quantity)  # Convert to int if it's a whole number
                if quantity == 0:
                    continue
            shopping_list_lines.append(f"- {ingredient_name}: {quantity} {unit}".strip())

        constant_shopping_list_elements = self.info.get_constant_shopping_list_elements()

        return self.lang.get_string("shopping_list") + "\n=============\n" + "\n".join(sorted(shopping_list_lines)) + "\n" + constant_shopping_list_elements

    def send_email(self, *args):
        """
        Sends the shopping list via email.
        """
        if self.info.email == "" or self.info.send_option != "option-email":
            failure_dialog = MDDialog(
                title=self.lang.get_string("email_failed"),
                text=self.lang.get_string("wrong_email_settings"),
                buttons=[
                    MDRaisedButton(
                        text=self.lang.get_string("ok"),
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: failure_dialog.dismiss()
                    )
                ]
            )
            failure_dialog.open()
            return

        with open('password.json') as f:
            data = json.load(f)
        receiver_email = self.info.email
        sender_email = data.get("mail")
        password = data.get("password")

        msg = EmailMessage()

        today_str = date.today().strftime("%d-%m-%Y")
        msg['Subject'] = f"{self.lang.get_string('shopping_list')} {today_str}"
        msg['From'] = sender_email
        msg['To'] = receiver_email

        msg.set_content(
            self.lang.get_string("mail_greeting") + "\n\n" +
            self.text_field.text + "\n\n" +
            self.lang.get_string("mail_closing")
        )

        context = ssl.create_default_context()

        smtp_server = "smtp.gmail.com"
        smtp_port = 465

        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(sender_email, password)
                server.send_message(msg)
            
            confirmation_dialog = MDDialog(
                title=self.lang.get_string("email_sent"),
                text=self.lang.get_string("email_sent_success"),
                buttons=[
                    MDRaisedButton(
                        text=self.lang.get_string("ok"),
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: confirmation_dialog.dismiss()
                    )
                ]
            )
            confirmation_dialog.open()
        except Exception as e:
            failure_dialog = MDDialog(
                title=self.lang.get_string("email_failed"),
                text=self.lang.get_string("email_sent_failure"),
                buttons=[
                    MDRaisedButton(
                        text=self.lang.get_string("ok"),
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: failure_dialog.dismiss()
                    )
                ]
            )
            failure_dialog.open()
            return
