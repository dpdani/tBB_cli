"""

tBB_cli entering screen.

"""

import urwid
import asyncio
from .main import MainView
from . import common
import tBB_requests


class WelcomeView(urwid.WidgetWrap):
    def __init__(self, frame):
        self.frame = frame
        self.title = "tBB"
        self.location = common.StyledEdit("tBB location:", edit_style=('edit', None), text_width=16, left_padding=5)
        self.password = common.StyledEdit("Access password:", edit_style=('edit', None), mask='*', left_padding=5)
        urwid.connect_signal(self.location.edit, 'change', self.clear_error)
        urwid.connect_signal(self.password.edit, 'change', self.clear_error)
        blank = urwid.AttrWrap(urwid.Divider(), 'body')
        content = [
            blank,
            blank,
            urwid.Padding(self.location, align='center'),
            urwid.Padding(self.password, align='center'),
            blank,
            blank,
            blank,
            blank,
            urwid.GridFlow([
                urwid.Button("Ok", self.on_ok),
                urwid.Button("Quit", self.on_quit)],
                8,3,1, 'center'
            ),
        ]
        self.listbox = urwid.ListBox(urwid.SimpleFocusListWalker(content))
        self.listbox = urwid.AttrWrap(self.listbox, 'body')
        super().__init__(self.listbox)

    def refresh(self):
        pass

    def clear_error(self, *args):
        self.frame.reset_status()

    def on_ok(self, *args):
        self.clear_error()
        try:
            host, port = self.location.edit.get_edit_text().split(':')
            port = int(port)
        except:
            self.frame.set_status("Location malformed. Expected input to be in this format: 127.0.0.1:1984.", 'error')
            return
        handler = tBB_requests.RequestsHandler(host, port, self.password.edit.get_edit_text())
        self.frame.set_status("Checking connection to {}...".format(self.location.edit.get_edit_text()))
        asyncio.async(self.check_handler(handler))

    @asyncio.coroutine
    def check_handler(self, handler):
        try:
            yield from handler.test()
        except:
            self.frame.set_status("tBB isn't responding at specified location.", 'error')
            return
        try:
            yield from handler.status()
        except:
            self.frame.set_status("Incorrect password.", 'error')
            return
        self.frame.set_status("Access granted.", 'success')
        self.frame.reset_status()
        self.frame.set_body(MainView(handler, self.frame))

    def on_quit(self, *args):
        if hasattr(self, 'app_quit'):
            self.app_quit()
