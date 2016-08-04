"""

CLI frontend interface for tBB.

"""

## Using modified libraries
## WARNING: libraries contained in tBB_cli/lib are modified.
## You might not be able to perform clean libraries updates.
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), "lib"))  # use these instead of built-ins
##

import asyncio
import urwid
import urwid_views
import urwid_views.common


def app_quit():
    raise urwid.ExitMainLoop()


def unhandled_input(key):
    if key in ('q', 'Q', 'esc'):
        @asyncio.coroutine
        def wait_for_input():
            sure = urwid_views.common.YesNoDialog(
                "Are you sure you want to quit?",
                attr='default', width=30, height=6, body=frame
            )
            if (yield from sure.listen()):
                raise urwid.ExitMainLoop()
        asyncio.async(wait_for_input())
    if key in ('w', 'W'):
        frame.view_back()
        return True
    if key in ('e', 'E'):
        frame.view_next()
        return True
    if key in ('f5', 'r', 'R'):
        frame.refresh()
        return True
    if key in ('h', 'H'):
        frame.show_help()
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
    ('reveal focus', 'default,standout', 'default'),
    ('dialog background', 'default', 'dark gray'),
    ('dialog button', 'default', 'dark gray'),
    ('dialog button focused', 'default', 'light blue'),
    ('edit', 'default,underline', 'default')
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
urwid_views.set_ui(loop.screen)
try:
    loop.run()
except KeyboardInterrupt:
    pass
finally:
    for task in asyncio.Task.all_tasks():
        task.cancel()
    asyncio.get_event_loop().run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))
    asyncio.get_event_loop().close()
print("Goodbye!")
