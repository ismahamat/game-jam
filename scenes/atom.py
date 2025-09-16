import arcade
from .base import BaseView


class AtomView(BaseView):
    def on_draw(self):
        super().on_draw()
        self.show_text_center("Atom - Prototype")


