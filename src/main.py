"""

CLI frontend interface for tBB.

"""

import asyncio
import urwid


def show_or_exit(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()
    txt.set_text(repr(key))


txt = urwid.Text("Hello World")
fill = urwid.Filler(txt, 'top')
evl = urwid.AsyncioEventLoop(loop=asyncio.get_event_loop())
loop = urwid.MainLoop(fill, event_loop=evl, unhandled_input=show_or_exit)
try:
    loop.run()
except KeyboardInterrupt:
    pass
print("Goodbye!")
