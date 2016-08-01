"""

Views for the CLI Urwid framework.

"""


import urwid
from .welcome import WelcomeView
from .main import MainView
from . import common


class MainFrame(urwid.Frame):
    def __init__(self):
        self.header_txt = urwid.Text("tBB - Command Line Front-end", 'center')
        self.header_txt = urwid.AttrWrap(self.header_txt, 'header')
        self.header = urwid.Pile([self.header_txt, urwid.AttrWrap(urwid.Divider(div_char='━'), 'header')])
        self.placeholder = urwid.WidgetPlaceholder(urwid.Text("Placeholder"))
        self.status = urwid.AttrWrap(urwid.Text(""), 'footer')  # footer
        self.reset_status()
        self.footer = urwid.Pile([urwid.AttrWrap(urwid.Divider(div_char='━'), 'header'), self.status])
        super().__init__(
            body=urwid.AttrWrap(self.placeholder, 'body'),
            header=self.header,
            footer=self.footer,
        )

    def set_status(self, text, color='waiting'):
        self.status.set_text(text)
        self.status.set_attr(color)

    def reset_status(self):
        self.set_status("Ready.", 'body')
