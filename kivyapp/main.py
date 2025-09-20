# Import the necessary Kivy modules
import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

# The fixed window size has been removed to allow the app to scale
# and work on any device and orientation.

class SimpleApp(App):
    """
    A Kivy application with a label and six interactive buttons.
    """
    def build(self):
        """
        Constructs the root widget for the app.
        """
        # Define a consistent background color for the screen
        self.initial_bg_color = (0.95, 0.95, 0.95, 1)
        self.initial_label_color = (0.2, 0.2, 0.2, 1)
        self.initial_button_color = (0.1, 0.6, 0.9, 1)
        
        # Use a FloatLayout as the root to allow a custom background color
        root = FloatLayout()

        # Add a background rectangle to the root's canvas
        with root.canvas.before:
            self.bg_color = Color(*self.initial_bg_color)
            self.bg_rect = Rectangle(size=root.size, pos=root.pos)
        
        # Bind the background to the root size/position so it resizes with the window
        root.bind(size=self._update_bg_rect, pos=self._update_bg_rect)
        
        # Main layout to hold the widgets
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(20)
        )

        # Create a label to display a message with text wrapping enabled
        self.hello_label = Label(
            text="Hello, Kivy! This is a longer text to demonstrate text wrapping.",
            font_size='24sp',
            color=self.initial_label_color,
            size_hint_y=0.6,  # Adjusted to take up more space
            halign='center',
            valign='middle',
            # Enable text wrapping
            text_size=(Window.width - dp(40), None)
        )
        Window.bind(size=self.on_window_size)

        # Create a layout for the 6 buttons
        # Changed to 3 columns for a more horizontal and readable layout
        button_layout = GridLayout(
            cols=3,
            spacing=dp(10),
            size_hint_y=0.4  # Adjusted to take up more space
        )
        
        # Store buttons in a list to change their colors later
        self.buttons = []
        
        # Button to change the background color
        self.btn_bg = Button(text="BG Color", on_press=self.on_change_bg_press, background_color=self.initial_button_color)
        button_layout.add_widget(self.btn_bg)
        self.buttons.append(self.btn_bg)

        # Button to change the font style (bold/italic)
        self.btn_font_style = Button(text="Font Style", on_press=self.on_change_font_style_press, background_color=self.initial_button_color)
        button_layout.add_widget(self.btn_font_style)
        self.buttons.append(self.btn_font_style)
        
        # Button to change the label text color
        self.btn_label_color = Button(text="Label Color", on_press=self.on_change_label_color, background_color=self.initial_button_color)
        button_layout.add_widget(self.btn_label_color)
        self.buttons.append(self.btn_label_color)

        # Button to change all other buttons' colors randomly
        self.btn_random_colors = Button(text="Randomize", on_press=self.on_randomize_button_colors, background_color=self.initial_button_color)
        button_layout.add_widget(self.btn_random_colors)
        self.buttons.append(self.btn_random_colors)

        # Button to reset all settings
        self.btn_reset = Button(text="Reset", on_press=self.on_reset_press, background_color=self.initial_button_color)
        button_layout.add_widget(self.btn_reset)
        self.buttons.append(self.btn_reset)

        # Button to show a simple popup
        self.btn_popup = Button(text="Info", on_press=self.on_show_info_press, background_color=self.initial_button_color)
        button_layout.add_widget(self.btn_popup)
        self.buttons.append(self.btn_popup)

        # Add all widgets to the main layout
        main_layout.add_widget(self.hello_label)
        main_layout.add_widget(button_layout)
        
        # The main layout is added to the root FloatLayout
        root.add_widget(main_layout)

        return root
        
    def on_window_size(self, instance, new_size):
        """Callback to update the label's text_size on window resize."""
        width, height = new_size
        self.hello_label.text_size = (width - dp(40), None)

    def _update_bg_rect(self, instance, value):
        """Callback to update the background rectangle size."""
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def on_change_bg_press(self, instance):
        """Changes the app's background color to a random color."""
        new_color = (random.random(), random.random(), random.random(), 1)
        self.bg_color.rgba = new_color

    def on_change_font_style_press(self, instance):
        """Cycles the label's font style between normal, bold, and italic."""
        if not self.hello_label.bold and not self.hello_label.italic:
            self.hello_label.bold = True  # Go to bold
        elif self.hello_label.bold:
            self.hello_label.bold = False
            self.hello_label.italic = True # Go to italic
        else:
            self.hello_label.italic = False # Go back to normal

    def on_change_label_color(self, instance):
        """Changes the label's text color to a random color."""
        new_color = (random.random(), random.random(), random.random(), 1)
        self.hello_label.color = new_color

    def on_randomize_button_colors(self, instance):
        """Changes the color of all buttons to a random color."""
        for button in self.buttons:
            button.background_color = (random.random(), random.random(), random.random(), 1)

    def on_reset_press(self, instance):
        """Resets all UI elements to their initial state."""
        self.bg_color.rgba = self.initial_bg_color
        self.hello_label.text = "Hello, Kivy! This is a longer text to demonstrate text wrapping."
        self.hello_label.font_size = '24sp'
        self.hello_label.color = self.initial_label_color
        self.hello_label.bold = False
        self.hello_label.italic = False
        for button in self.buttons:
            button.background_color = self.initial_button_color

    def on_show_info_press(self, instance):
        """Displays a simple popup with information."""
        popup_content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        popup_content.add_widget(Label(text="This is a simple demo app!", font_size='20sp'))
        
        close_button = Button(text="Dismiss", size_hint_y=None, height=dp(48))
        popup = Popup(title='App Info', content=popup_content, size_hint=(0.8, 0.4), auto_dismiss=False)
        
        close_button.bind(on_press=popup.dismiss)
        popup_content.add_widget(close_button)
        
        popup.open()

if __name__ == '__main__':
    SimpleApp().run()
