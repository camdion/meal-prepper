from textual.message import Message
from textual.widgets import Button


class Quit(Button):
    def __init__(self):
        super().__init__(label="Quit", id="quit", classes="quit_button", variant="error")

    class QuitPressed(Message):
        def __init__(self):
            super().__init__()

    def on_button_pressed(self):
        self.post_message(self.QuitPressed())
