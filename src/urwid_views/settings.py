"""

tBB_cli settings view.

"""
import datetime
import urwid
import asyncio
from . import common


class SettingsView(urwid.WidgetWrap):
    def __init__(self, handler, frame):
        self.handler = handler
        self.frame = frame
        self.title = "Settings"
        self.refresh()

    def refresh(self):
        left_contents = [
            urwid.AttrWrap(urwid.Text("Settings", 'center'), 'header'),

        ]
        self.cols = urwid.Columns([
            ('weight', 3, urwid.ListBox(urwid.SimpleFocusListWalker(left_contents))),
            common.ExpandedVerticalSeparator(
                urwid.ListBox(urwid.SimpleFocusListWalker([
                    urwid.Button("Save", on_press=self.on_settings),
                ]))
            ),
        ])
        super().__init__(self.cols)
        asyncio.async(self.fill_stats())

    def on_settings(self, user_data):
        @asyncio.coroutine
        def wait_for_input():
            yield from common.OkDialog(
                "Work in progress.",
                attr='default', width=30, height=8, body=self.frame
            ).listen()
        asyncio.async(wait_for_input())

    @asyncio.coroutine
    def fill_stats(self):
        self.frame.set_status("Waiting for response...")
        self.frame.reset_status()