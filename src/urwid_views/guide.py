"""

tBB_cli guide view.

"""

import urwid
import asyncio


class GuideView(urwid.WidgetWrap):
    def __init__(self, frame):
        self.frame = frame
        self.title = "Guide"
        blank = urwid.AttrWrap(urwid.Divider(), 'body')
        content = [
            urwid.AttrWrap(urwid.Text("tBB CLI Guide."), 'mainview_title'),
            urwid.Text(
"""\
  Welcome to tBB - Command Line Frontend.
This guide assumes you know basic tBB service functionality.
If you don't, you probably had something better to do last night.

  ... work in progress ...
"""),
            blank,
        ]
        self.listbox = urwid.ListBox(urwid.SimpleFocusListWalker(content))
        self.listbox = urwid.AttrWrap(self.listbox, 'body')
        super().__init__(self.listbox)

    def refresh(self):
        pass
