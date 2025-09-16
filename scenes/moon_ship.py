import arcade
from .base import BaseView


class MoonShipView(BaseView):
    def on_draw(self):
        super().on_draw()
        self.show_text_center("Moon Ship - Prototype")


