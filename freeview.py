from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.button import MDIconButton, MDRaisedButton
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
from kivymd.uix.filemanager import MDFileManager
from kivy.properties import ObjectProperty
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_hex_from_color
from kivymd.uix.fitimage import FitImage

import os
import numpy as np
from info import Info
from recipe import Recipe
from product import Product
from recipes import append_recipe_to_xml, update_recipe_in_xml, delete_recipe_from_xml
from kivymd.uix.list import OneLineAvatarIconListItem

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



class RecipeDialogContent(MDBoxLayout):
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

        details_scroll = MDScrollView()
        content = MDBoxLayout(orientation='vertical', adaptive_height=True, padding="15dp", spacing="10dp")

        ingredients_text = "\n".join([f"- {key}: {value}" for key, value in recipe.ingredients.items()]) or self.lang.get_string("no_ingredients")

        portions_text = f"[color={primary_hex_color}]{self.lang.get_string('portions')}:[/color] [color={secondary_hex_color}]{recipe.portions}[/color]"
        content.add_widget(MDLabel(text=portions_text, markup=True, adaptive_height=True))
        duration_text = f"[color={primary_hex_color}]{self.lang.get_string('duration')}:[/color] [color={secondary_hex_color}]{recipe.duration}[/color]"
        content.add_widget(MDLabel(text=duration_text, markup=True, adaptive_height=True))
        ingredients_pretext = f"[color={primary_hex_color}]{self.lang.get_string('ingredients')}:\n[/color][color={secondary_hex_color}]{ingredients_text}[/color]"
        content.add_widget(MDLabel(text=ingredients_pretext, markup=True, adaptive_height=True))
        instructions_text = f"[color={primary_hex_color}]{self.lang.get_string('instructions')}:[/color]"
        content.add_widget(MDLabel(text=instructions_text, markup=True, adaptive_height=True))
        content.add_widget(MDLabel(text=recipe.instructions or self.lang.get_string("no_instructions"), markup=True, adaptive_height=True))

        details_scroll.add_widget(content)
        self.add_widget(details_scroll)


class EditRecipeDialogContent(MDBoxLayout):
    """
    Class creating the content of the dialog window for editing recipes.
    """
    def __init__(self, lang, recipe, **kwargs):
        super().__init__(**kwargs)
        self.lang = lang
        self.recipe = recipe
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = Window.height * 0.8    

        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True
        )

        self.ingredient_rows = []
        self.dir_path = os.path.dirname(os.path.abspath(__file__))
        self.image_paths = []
        self.to_remove = []

        self.content = MDBoxLayout(orientation='vertical', spacing="10dp", adaptive_height=True)
        self.name_input = MDTextField(
            text=recipe.name,
            hint_text=self.lang.get_string("recipe_name"),
            mode="rectangle"
        )
        self.content.add_widget(self.name_input)

        self.duration_input = MDTextField(
            text=str(recipe.duration_int),
            hint_text=self.lang.get_string("preparation_time"),
            mode="rectangle",
            input_filter='int',
            max_text_length=3
        )
        self.content.add_widget(self.duration_input)

        self.type_field = MDTextField(
            text=recipe.mealtype,
            hint_text=self.lang.get_string("meal_type"),
            mode="rectangle",
            on_text_validate=self.validate_type,
            on_focus=self.validate_type
        )

        self.content.add_widget(self.type_field)

        self.portions_and_vege_layout = MDBoxLayout(orientation='horizontal', spacing="10dp", size_hint_y=None, height=self.name_input.height + 2*dp(10))

        self.portions_input = MDTextField(
            text=str(recipe.portions),
            hint_text=self.lang.get_string("portions"),
            mode="rectangle",
            input_filter='int',
            max_text_length=1
        )
        self.portions_and_vege_layout.add_widget(self.portions_input)

        self.vegetarian_checkbox = MDCheckbox()
        self.vegetarian_checkbox.active = recipe.vegetarian
        self.portions_and_vege_layout.add_widget(MDLabel(text=self.lang.get_string("vegetarianshort"), halign="right", valign="middle"))
        self.portions_and_vege_layout.add_widget(self.vegetarian_checkbox)
        self.content.add_widget(self.portions_and_vege_layout)

        self.ingredients_label = MDLabel(
            text=self.lang.get_string("ingredients"),
            adaptive_height=True
        )
        self.content.add_widget(self.ingredients_label)
    
        self.ingredients_container = MDBoxLayout(
            orientation='vertical',
            adaptive_height=True,
            spacing="5dp"
        )

        for name, quantity in recipe.ingredients.items():
            ingredient_row_layout = MDBoxLayout(
                orientation='horizontal',
                spacing="10dp",
                size_hint_y=None,
                height="48dp"
            )

            # Field for ingredient name
            name_field = MDTextField(
                text=name,
                hint_text=self.lang.get_string("ingredient_name"),
                mode="line",
                size_hint_x=0.7 # Takes up 70% of the width
            )

            # Field for quantity
            quantity_field = MDTextField(
                text=quantity,
                hint_text=self.lang.get_string("ingredient_quantity"),
                mode="line",
                size_hint_x=0.3 # Takes up 30% of the width
            )

            self.ingredient_rows.append(
                {'name': name_field, 'quantity': quantity_field}
            )

            ingredient_row_layout.add_widget(name_field)
            ingredient_row_layout.add_widget(quantity_field)
            
            self.ingredients_container.add_widget(ingredient_row_layout)
        self.content.add_widget(self.ingredients_container)

        add_ingredient_button = MDIconButton(
            icon="plus",
            on_release=self.add_ingredient_row
        )
        self.content.add_widget(add_ingredient_button)

        self.instructions_input = MDTextField(
            text=recipe.instructions,
            hint_text=self.lang.get_string("instructions"),
            mode="rectangle",
            multiline=True
        )
        self.content.add_widget(self.instructions_input)

        self.image_buttons_box = MDBoxLayout(orientation='horizontal', spacing="10dp", size_hint_y=None, height="48dp")

        self.image_button = MDRaisedButton(
            text=self.lang.get_string("select_image"),
            on_release=self.open_file_manager
        )
        self.image_buttons_box.add_widget(self.image_button)

        self.remove_image_button = MDFlatButton(
            text=self.lang.get_string("remove_images"),
            on_release=self.remove_image_popup
        )
        self.image_buttons_box.add_widget(self.remove_image_button)
        self.content.add_widget(self.image_buttons_box)

        self.selected_image_box = MDBoxLayout(
            orientation='horizontal',
            height="120dp",
            padding="10dp",
            spacing="10dp",
            size_hint_x=None
        )

        image_dir = os.path.join("imgs", f"recipe{recipe.id}")
        if os.path.isdir(image_dir):
            for img_name in os.listdir(image_dir):
                img_path = os.path.join(image_dir, img_name)
                if os.path.isfile(img_path):
                    self.selected_image_box.add_widget(
                        FitImage(
                            source=img_path,
                            size_hint_x=None,
                            width="120dp"
                        )
                    )   

        self.image_scroll = MDScrollView(
            size_hint_y=None,
            height="120dp",
            do_scroll_x=True,
            do_scroll_y=False
        )

        self.image_scroll.add_widget(self.selected_image_box)
        self.content.add_widget(self.image_scroll)

        self.scrollview = MDScrollView()
        self.scrollview.add_widget(self.content)
        self.add_widget(self.scrollview)


    def add_ingredient_row(self, *args):
        """
        Tworzy nowy wiersz składający się z dwóch pól tekstowych (nazwa, ilość)
        i dodaje go do kontenera na składniki.
        """
        ingredient_row_layout = MDBoxLayout(
            orientation='horizontal',
            spacing="10dp",
            size_hint_y=None,
            height="48dp"
        )

        # Pole na nazwę składnika
        name_field = MDTextField(
            hint_text=self.lang.get_string("ingredient_name"),
            mode="line",
            size_hint_x=0.7 # Zajmuje 70% szerokości
        )

        # Pole na ilość
        quantity_field = MDTextField(
            hint_text=self.lang.get_string("ingredient_quantity"),
            mode="line",
            size_hint_x=0.3 # Zajmuje 30% szerokości
        )

        ingredient_row_layout.add_widget(name_field)
        ingredient_row_layout.add_widget(quantity_field)
        
        self.ingredients_container.add_widget(ingredient_row_layout)
        
        self.ingredient_rows.append(
            {'name': name_field, 'quantity': quantity_field}
        )

    def validate_type(self, instance):
        """Waliduje wpisany typ posiłku."""
        valid_types = [self.lang.get_string("Breakfast"), self.lang.get_string("Lunch"), self.lang.get_string("Dinner"), self.lang.get_string("Snack"), self.lang.get_string("Dessert"), self.lang.get_string("Supper")]
        input_type = instance.text.strip().lower()
        if input_type not in {vt.lower() for vt in valid_types}:
            instance.error = True
        else:
            instance.error = False
            instance.text = next(vt for vt in valid_types if vt.lower() == input_type)

    def open_file_manager(self, instance):
        """Otwiera menedżer plików do wyboru zdjęcia."""
        self.file_manager.show(self.dir_path)

    
    def remove_image_popup(self, instance):
        def remove_selected_images(instance):
            # Find checked images
            for i, (img_name, checkbox) in enumerate(image_checkboxes.items()):
                if checkbox.active:
                    self.to_remove.append(img_name)
            # Remove from UI and disk
            for img_name in self.to_remove:
                img_path = os.path.join("imgs", f"recipe{self.recipe.id}", img_name)
                # Remove from selected_image_box
                for widget in list(self.selected_image_box.children):
                    if hasattr(widget, "source") and os.path.basename(widget.source) == img_name:
                        self.selected_image_box.remove_widget(widget)
            # Close dialog
            dialog.dismiss()

        # Gather image names
        image_dir = os.path.join("imgs", f"recipe{self.recipe.id}")
        image_names = []
        if os.path.isdir(image_dir):
            image_names = [img for img in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, img))]
        if not image_names:
            return

        image_checkboxes = {}
        content = MDBoxLayout(orientation="vertical", spacing="10dp", adaptive_height=True)
        for img_name in image_names:
            row = MDBoxLayout(orientation="horizontal", adaptive_height=True)
            checkbox = MDCheckbox()
            image_checkboxes[img_name] = checkbox
            row.add_widget(checkbox)
            row.add_widget(MDLabel(text=img_name, adaptive_height=True))
            content.add_widget(row)

        dialog = MDDialog(
            title=self.lang.get_string("remove_images"),
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text=self.lang.get_string("cancel"), on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text=self.lang.get_string("remove"), on_release=remove_selected_images)
            ]
        )
        dialog.open()


    def select_path(self, path: str):
        """
        Metoda wywoływana po wybraniu pliku.
        Sprawdza, czy ścieżka jest plikiem, aktualizuje obraz i zamyka menedżer.
        """
        if os.path.isfile(path):
            self.image_paths.append(path)

            self.selected_image_box.add_widget(
                FitImage(
                    source=path,
                    size_hint_x=None,
                    width="120dp"
                )
            )

        self.exit_manager()

    def exit_manager(self, *args):
        self.file_manager.close()

class AddRecipeDialogContent(MDBoxLayout):
    """
    Klasa tworząca zawartość okna dialogowego do dodawania przepisów.
    """
    portions_input = ObjectProperty(None)
    duration_input = ObjectProperty(None)
    ingredients_input = ObjectProperty(None)
    instructions_input = ObjectProperty(None)
    
    def __init__(self, lang, **kwargs):
        super().__init__(**kwargs)
        self.lang = lang
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = Window.height * 0.8    

        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True
        )

        self.ingredient_rows = []
        self.dir_path = os.path.dirname(os.path.abspath(__file__))
        self.image_paths = []

        self.content = MDBoxLayout(orientation='vertical', spacing="10dp", adaptive_height=True)
        self.name_input = MDTextField(
            hint_text=self.lang.get_string("recipe_name"),
            mode="rectangle"
        )
        self.content.add_widget(self.name_input)

        self.duration_input = MDTextField(
            hint_text=self.lang.get_string("preparation_time"),
            mode="rectangle",
            input_filter='int',
            max_text_length=3
        )
        self.content.add_widget(self.duration_input)

        self.type_field = MDTextField(
            hint_text=self.lang.get_string("meal_type"),
            mode="rectangle",
            on_text_validate=self.validate_type,
            on_focus=self.validate_type
        )

        self.content.add_widget(self.type_field)

        self.portions_and_vege_layout = MDBoxLayout(orientation='horizontal', spacing="10dp", size_hint_y=None, height=self.name_input.height + 2*dp(10))

        self.portions_input = MDTextField(
            hint_text=self.lang.get_string("portions"),
            mode="rectangle",
            input_filter='int',
            max_text_length=1
        )
        self.portions_and_vege_layout.add_widget(self.portions_input)

        self.vegetarian_checkbox = MDCheckbox()
        self.vegetarian_checkbox.active = False
        self.portions_and_vege_layout.add_widget(MDLabel(text=self.lang.get_string("vegetarianshort"), halign="right", valign="middle"))
        self.portions_and_vege_layout.add_widget(self.vegetarian_checkbox)
        self.content.add_widget(self.portions_and_vege_layout)

        self.ingredients_label = MDLabel(
            text=self.lang.get_string("ingredients"),
            adaptive_height=True
        )
        self.content.add_widget(self.ingredients_label)
    
        self.ingredients_container = MDBoxLayout(
            orientation='vertical',
            adaptive_height=True,
            spacing="5dp"
        )
        self.content.add_widget(self.ingredients_container)
        
        self.add_ingredient_row()

        add_ingredient_button = MDIconButton(
            icon="plus",
            on_release=self.add_ingredient_row
        )
        self.content.add_widget(add_ingredient_button)

        self.instructions_input = MDTextField(
            hint_text=self.lang.get_string("instructions"),
            mode="rectangle",
            multiline=True
        )
        self.content.add_widget(self.instructions_input)

        self.image_button = MDRaisedButton(
            text=self.lang.get_string("select_image"),
            pos_hint={'center_x': 0.5}
        )
        self.image_button.bind(on_release=self.open_file_manager)
        self.content.add_widget(self.image_button)

        self.selected_image_box = MDBoxLayout(
            orientation='horizontal',
            height="120dp",
            padding="10dp",
            spacing="10dp",
            size_hint_x=None
        )

        self.selected_image_box.add_widget(
            MDLabel(
                text=self.lang.get_string("no_image_selected"),
                halign="center"
            )
        )

        self.image_scroll = MDScrollView(
            size_hint_y=None,
            height="120dp",
            do_scroll_x=True,
            do_scroll_y=False
        )

        self.image_scroll.add_widget(self.selected_image_box)
        self.content.add_widget(self.image_scroll)

        self.scrollview = MDScrollView()
        self.scrollview.add_widget(self.content)
        self.add_widget(self.scrollview)

    def add_ingredient_row(self, *args):
        """
        Tworzy nowy wiersz składający się z dwóch pól tekstowych (nazwa, ilość)
        i dodaje go do kontenera na składniki.
        """
        ingredient_row_layout = MDBoxLayout(
            orientation='horizontal',
            spacing="10dp",
            size_hint_y=None,
            height="48dp"
        )

        # Pole na nazwę składnika
        name_field = MDTextField(
            hint_text=self.lang.get_string("ingredient_name"),
            mode="line",
            size_hint_x=0.7 # Zajmuje 70% szerokości
        )

        # Pole na ilość
        quantity_field = MDTextField(
            hint_text=self.lang.get_string("ingredient_quantity"),
            mode="line",
            size_hint_x=0.3 # Zajmuje 30% szerokości
        )

        ingredient_row_layout.add_widget(name_field)
        ingredient_row_layout.add_widget(quantity_field)
        
        self.ingredients_container.add_widget(ingredient_row_layout)
        
        self.ingredient_rows.append(
            {'name': name_field, 'quantity': quantity_field}
        )

    def validate_type(self, instance):
        """Waliduje wpisany typ posiłku."""
        valid_types = [self.lang.get_string("Breakfast"), self.lang.get_string("Lunch"), self.lang.get_string("Dinner"), self.lang.get_string("Snack"), self.lang.get_string("Dessert"), self.lang.get_string("Supper")]
        input_type = instance.text.strip().lower()
        if input_type not in {vt.lower() for vt in valid_types}:
            instance.error = True
        else:
            instance.error = False
            instance.text = next(vt for vt in valid_types if vt.lower() == input_type)

    def open_file_manager(self, instance):
        """Otwiera menedżer plików do wyboru zdjęcia."""
        # Show file manager starting at the app's directory
        self.file_manager.show(self.dir_path)


    def select_path(self, path: str):
        """
        Metoda wywoływana po wybraniu pliku.
        Sprawdza, czy ścieżka jest plikiem, aktualizuje obraz i zamyka menedżer.
        """
        if os.path.isfile(path):
            self.image_paths.append(path)
    
            if self.selected_image_box.children[0].__class__ == MDLabel:
                self.selected_image_box.remove_widget(self.selected_image_box.children[0])

            self.selected_image_box.add_widget(
                FitImage(
                    source=path,
                    size_hint_x=None,
                    width="120dp"
                )
            )

        # 4. Niezależnie od wyniku, zamknij menedżer plików
        self.exit_manager()

    def exit_manager(self, *args):
        self.file_manager.close()


class FreeViewScreen(MDScreen):
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

        self.add_button = MDRaisedButton(text=self.lang.get_string("add_recipe"), size_hint=(1, None), on_release=self.add_new_recipe, halign="center")
        self.layout.add_widget(self.add_button)

        self.add_widget(self.layout)

        self.populate_list(self.all_recipes)

    def add_new_recipe(self, *args):
        self.dialog = MDDialog(
            title=self.lang.get_string("add_recipe"),
            type="custom",
            content_cls=AddRecipeDialogContent(self.lang),
            buttons=[
                MDFlatButton(text=self.lang.get_string("cancel"), on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text=self.lang.get_string("add_recipe"), on_release=self.add_recipe)
            ]
        )
        self.dialog.open()

    def add_recipe(self, *args):
        recipe = Recipe(
            id_=1000 + len(self.all_recipes),
            dur=f"{Recipe.convert_int_to_duration(self.dialog.content_cls.duration_input.text)}" if self.dialog.content_cls.duration_input.text else "0 min",
            name=self.dialog.content_cls.name_input.text.capitalize() or self.lang.get_string("unnamed_recipe"),
            portions=int(self.dialog.content_cls.portions_input.text) if self.dialog.content_cls.portions_input.text.isdigit() else 1,
            mealtype=self.dialog.content_cls.type_field.text or self.lang.get_string("unknown"),
            vegetarian=self.dialog.content_cls.vegetarian_checkbox.active,
            instructions=self.dialog.content_cls.instructions_input.text or self.lang.get_string("no_instructions"),
        )

        for row in self.dialog.content_cls.ingredient_rows:
            product = Product(
                name=row['name'].text.capitalize() or self.lang.get_string("unnamed_product"),
                quantity=row['quantity'].text or "1",
            )
            recipe.add_product(product)

        for i, image in enumerate(self.dialog.content_cls.image_paths):
            image_dir = f"imgs/recipe{recipe.id}/"
            os.makedirs(image_dir, exist_ok=True)
            dest_path = os.path.join(image_dir, f"{i}.png")
            try:
                with open(image, 'rb') as src_file:
                    with open(dest_path, 'wb') as dest_file:
                        dest_file.write(src_file.read())
            except Exception as e:
                continue

        append_recipe_to_xml("recipes.xml", recipe, language=self.lang.current_language)
        self.all_recipes.append(recipe)
        self.populate_list(self.all_recipes)
        MDApp.get_running_app().scs.populate_list(self.all_recipes)
        self.dialog.dismiss()

    def edit_the_recipe(self, recipe):
        self.dialog.dismiss()
        self.dialog = MDDialog(
            title=self.lang.get_string("edit_recipe"),
            type="custom",
            content_cls=EditRecipeDialogContent(self.lang, recipe),
            buttons=[
                MDFlatButton(text=self.lang.get_string("cancel"), on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text=self.lang.get_string("save"), on_release=self.save_edited_recipe)
            ]
        )
        self.dialog.open()

    def delete_the_recipe(self, recipe):
        delete_recipe_from_xml("recipes.xml", recipe)
        self.all_recipes.remove(recipe)
        self.populate_list(self.all_recipes)
        MDApp.get_running_app().scs.populate_list(self.all_recipes)
        self.dialog.dismiss()

    def save_edited_recipe(self, *args):
        content = self.dialog.content_cls
        recipe = content.recipe

        recipe.name = content.name_input.text.capitalize() if content.name_input.text else content.name_input.hint_text
        recipe.duration_int = int(content.duration_input.text) if content.duration_input.text and content.duration_input.text.isdigit() else content.duration_input.hint_text
        recipe.duration = Recipe.convert_int_to_duration(recipe.duration_int)
        recipe.mealtype = content.type_field.text if content.type_field.text else content.type_field.hint_text
        recipe.portions = int(content.portions_input.text) if content.portions_input.text and content.portions_input.text.isdigit() else content.portions_input.hint_text
        recipe.vegetarian = content.vegetarian_checkbox.active
        recipe.instructions = content.instructions_input.text if content.instructions_input.text else content.instructions_input.hint_text

        # Clear existing ingredients and re-add from input fields
        recipe.ingredients.clear()
        for row in content.ingredient_rows:
            name = row['name'].text.capitalize() if row['name'].text else row['name'].hint_text
            quantity = row['quantity'].text if row['quantity'].text else row['quantity'].hint_text
            product = Product(name=name, quantity=quantity)
            recipe.add_product(product)

        for path in content.image_paths:
            image_dir = f"imgs/recipe{recipe.id}/"
            os.makedirs(image_dir, exist_ok=True)
            dest_path = os.path.join(image_dir, f"{len(os.listdir(image_dir))}.png")
            try:
                with open(path, 'rb') as src_file:
                    with open(dest_path, 'wb') as dest_file:
                        dest_file.write(src_file.read())
            except Exception as e:
                continue

        # Remove from UI and disk
        for img_name in content.to_remove:
            img_path = os.path.join("imgs", f"recipe{recipe.id}", img_name)
            # Remove from disk
            if os.path.exists(img_path):
                try:
                    os.remove(img_path)
                except Exception:
                    pass

        # Update XML file
        update_recipe_in_xml("recipes.xml", recipe, language=self.lang.current_language)
        self.all_recipes = self.info.get_recipes()
        # Refresh lists
        self.populate_list(self.all_recipes)
        MDApp.get_running_app().scs.populate_list(self.all_recipes)

        self.dialog.dismiss()

    def set_default_toolbar_items(self):
        """
        Sets the default icons on the toolbar.
        """
        self.toolbar.title = self.lang.get_string("free_view")
        self.toolbar.right_action_items = [["filter-variant", lambda x: self.open_filter_dialog()]]
        self.toolbar.left_action_items = [["magnify", lambda x: self.enter_search_mode()]]

    def enter_search_mode(self, *args):
        """
        Changes the title and icons to a search text field.
        """
        self.toolbar.left_action_items = []
        self.toolbar.right_action_items = []
        self.toolbar.title = ""

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
        button_text = self.lang.get_string("edit_recipe")
        self.dialog = MDDialog(
            title=recipe.name,
            type="custom",
            content_cls=RecipeDialogContent(recipe=recipe, lang=self.lang),
            buttons=[
                MDRaisedButton(
                    text=self.lang.get_string("delete_recipe"),
                    md_bg_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.delete_the_recipe(recipe)
                ),
                MDRaisedButton(
                    text=button_text,
                    md_bg_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.edit_the_recipe(recipe)
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
        self.dialog.content_cls = RecipeDialogContent(recipe=recipe, lang=self.lang)
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

            try:
                main_ingredients = f"{list(recipe.ingredients.keys())[0]}, {list(recipe.ingredients.keys())[1]}, {list(recipe.ingredients.keys())[2]}..." if len(recipe.ingredients) > 3 else ", ".join(list(recipe.ingredients.keys()))
            except Exception as e:
                main_ingredients = self.lang.get_string("no_ingredients")
            list_item = TwoLineAvatarIconListItem(
                text=f"{recipe.name}",
                secondary_text=f"{main_ingredients}",
            )

            list_item.on_release = lambda rec=recipe: self.show_recipe_popup(rec)
            list_item.secondary_font_style = "Caption"

            # Add the image to the list item
            list_item.add_widget(image_widget)

            # Add the completed item to our MDList
            self.recipe_list.add_widget(list_item)


    def update_translation(self):
        self.toolbar.title = self.lang.get_string("free_view")
        self.add_button.text = self.lang.get_string("add_recipe")
        self.all_recipes = self.info.get_recipes()
        self.apply_filters_and_search()
