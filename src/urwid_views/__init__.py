"""

Views for the CLI Urwid framework.

"""


import urwid
import asyncio
import datetime
from .welcome import WelcomeView
from .main import MainView
from . import ip
from . import mac
from . import common


class MainFrame(urwid.Frame):
    def __init__(self):
        self.header_txt = urwid.Text("tBB - Command Line Front-end", 'center')
        self.header_txt = urwid.AttrWrap(self.header_txt, 'header')
        self.header_date = urwid.Text("{}", 'left')
        self.header_date = urwid.AttrWrap(self.header_date, 'header')
        self.header_time = urwid.Text("{}", 'right')
        self.header_time = urwid.AttrWrap(self.header_time, 'header')
        self.header = urwid.Pile([
            urwid.Columns([
                self.header_date,
                ('weight', 2, self.header_txt),
                self.header_time,
            ]),
            urwid.AttrWrap(urwid.Divider(div_char='━'), 'header')
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
        for view_index in list(self.body_history.keys()):
            if view_index > self.current_view:
                del self.body_history[view_index]
        self.current_view += 1
        self.body_history[self.current_view] = body
        return self._set_body(body)

    def _set_body(self, body):
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

    def keypress(self, size, key):
        if key in ('w', 'W'):
            self.view_back()
            return True
        if key in ('e', 'E'):
            self.view_next()
            return True
        return super().keypress(size, key)
