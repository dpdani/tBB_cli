"""

CLI frontend interface for tBB.

"""

import asyncio
import sys
import urwid
import urwid_views


def app_quit():
    print("Goodbye!")
    asyncio.get_event_loop().stop()
    raise urwid.ExitMainLoop()


def unhandled_input(key):
    if key in ('q', 'Q', 'esc'):
        raise urwid.ExitMainLoop()
    if key in ('w', 'W'):
        frame.view_back()
        return True
    if key in ('e', 'E'):
        frame.view_next()
        return True
    if key == 'f5':
        frame.refresh()
        return True


palette = [
    ('body', 'default', 'default'),
    ('header', 'dark blue,bold', 'default'),
    ('header buttons', 'dark blue', 'default'),
    ('footer', 'yellow', 'default'),
    ('error', 'dark red', 'default'),
    ('success', 'dark green', 'default'),
    ('waiting', 'yellow', 'default'),
    ('navigation', 'dark gray,underline', 'default'),
    ('mainview_title', 'default,bold', 'default'),
    ('reveal focus', 'default,standout', 'default')
]


frame = urwid_views.MainFrame()
welcome_view = urwid_views.WelcomeView(frame)
welcome_view.app_quit = app_quit
frame.set_body(welcome_view)
evl = urwid.AsyncioEventLoop(loop=asyncio.get_event_loop())
loop = urwid.MainLoop(
    frame, event_loop=evl, unhandled_input=unhandled_input,
    palette=palette
)
try:
    loop.run()
except KeyboardInterrupt:
    pass
except asyncio.CancelledError:
    pass
print("Goodbye!")
