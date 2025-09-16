import arcade
from .base import BaseView


class HumanDogView(BaseView):
    def on_draw(self):
        super().on_draw()
        self.show_text_center("Human & Dog - Prototype")


