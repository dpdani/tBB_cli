"""

Views for the CLI Urwid framework.

"""


import urwid
import asyncio
import datetime
from .welcome import WelcomeView
from .main import MainView
from .guide import GuideView
from . import ip
from . import mac
from . import common


def set_ui(ui):
    common.ui = ui


class MainFrame(urwid.Frame):
    def __init__(self):
        self.header_txt = urwid.Text("tBB - Command Line Front-end", 'center')
        self.header_txt = urwid.AttrWrap(self.header_txt, 'header')
        self.header_date = urwid.Text("{}", 'left')
        self.header_date = urwid.AttrWrap(self.header_date, 'header')
        self.header_time = urwid.Text("{}", 'right')
        self.header_time = urwid.AttrWrap(self.header_time, 'header')
        self.commands = urwid.Columns([
            urwid.AttrWrap(urwid.Text("[esc|q: Exit]", 'left'), 'header buttons'),
            urwid.AttrWrap(urwid.Text("[w: Back]", 'center'), 'header buttons'),
            urwid.AttrWrap(urwid.Text("[e: Next]", 'center'), 'header buttons'),
            urwid.AttrWrap(urwid.Text("[F5|r: Refresh]", 'center'), 'header buttons'),
            urwid.AttrWrap(urwid.Text("[h: Help]", 'right'), 'header buttons'),
        ])
        self.nav_position = urwid.AttrWrap(urwid.Text("ASD > asd"), 'navigation')
        self.header = urwid.Pile([
            urwid.Columns([
                self.header_date,
                ('weight', 2, self.header_txt),
                self.header_time,
            ]),
            self.commands,
            urwid.AttrWrap(urwid.Divider(div_char='━'), 'header'),
            self.nav_position,
        ])
        self.placeholder = urwid.WidgetPlaceholder(urwid.Text("Placeholder"))
        self.body_history = {}
        self.current_view = 0
        self.status = urwid.AttrWrap(urwid.Text(""), 'footer')  # footer
        self.reset_status()
        self.footer = urwid.Pile([urwid.AttrWrap(urwid.Divider(div_char='━'), 'header'), self.status])
        super().__init__(
            body=urwid.AttrWrap(self.placeholder, 'body'),
            header=self.header,
            footer=self.footer,
        )
        asyncio.async(self.keep_time_updated())

    @asyncio.coroutine
    def keep_time_updated(self):
        while asyncio.get_event_loop().is_running():
            try:
                self.header_date.set_text(datetime.datetime.now().strftime("%d/%m/%Y"))
                self.header_time.set_text(datetime.datetime.now().strftime("%H:%M"))
                yield from asyncio.sleep(5)
            except asyncio.CancelledError:
                break

    def set_status(self, text, color='waiting'):
        self.status.set_text(text)
        self.status.set_attr(color)

    def reset_status(self):
        self.set_status("Ready.", 'body')

    def set_body(self, body):
        if hasattr(self, 'app_quit'):
            body.app_quit = self.app_quit
        self.reset_status()
        for view_index in list(self.body_history.keys()):
            if view_index > self.current_view:
                del self.body_history[view_index]
        self.current_view += 1
        self.body_history[self.current_view] = body
        return self._set_body(body)

    def _set_body(self, body):
        views = list(self.body_history.values())[0:self.current_view]
        self.nav_position.set_text(" →  ".join([entry.title for entry in views]))
        self.reset_status()
        return super().set_body(body)

    def view_back(self):
        if self.current_view <= 1:
            return
        self.current_view -= 1
        return self._set_body(self.body_history[self.current_view])

    def view_next(self):
        if self.current_view +1 > len(self.body_history):
            return
        self.current_view += 1
        return self._set_body(self.body_history[self.current_view])
    
    def refresh(self):
        self.body_history[self.current_view].refresh()
        self.body._invalidate()

    def show_help(self):
        self.set_body(GuideView(self))
