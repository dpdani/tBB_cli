"""

MAC view.

"""

import datetime
import urwid
import asyncio
import socket
from tBB_requests import RequestError
from . import common


class NameView(urwid.WidgetWrap):
    def __init__(self, name, handler, frame):
        self.name = name
        self.handler = handler
        self.frame = frame
        self.title = "Name {}".format(name)
        self.refresh()

    def refresh(self):
        self.header = urwid.Text("Information about Name '{}':")
        self.ignored = urwid.Text("Ignored: {}.")
        self.ip_list = common.EntriesList(options=['Waiting...'], fixed_height=4, max_height=4, lesser_height=0)
        self.last_update = urwid.Text("Last updated: {} ({} ago).")
        self.history_list = common.EntriesList(lesser_height=15, options=[], max_height=1)
        left_contents = [
            urwid.AttrWrap(urwid.Text("Name View", 'center'), 'header'),
            urwid.AttrWrap(self.header, 'mainview_title'),
            urwid.Padding(self.ignored, left=1),
            urwid.Padding(urwid.Text("IPs:"), left=1),
            urwid.Padding(self.ip_list, left=3),
            urwid.Padding(self.last_update, left=1),
            urwid.Divider(),
            urwid.AttrWrap(urwid.Text("History (most recent first):"), 'mainview_title'),
            self.history_list,
        ]
        self.cols = urwid.Columns([
            ('weight', 3, urwid.ListBox(urwid.SimpleFocusListWalker(left_contents))),
            common.ExpandedVerticalSeparator(
                urwid.ListBox(urwid.SimpleFocusListWalker([
                    urwid.Button("Ignore", on_press=self.ignore),
                ]))
            ),
        ])
        super().__init__(self.cols)
        asyncio.async(self.fill_stats())

    def ignore(self, user_data):
        @asyncio.coroutine
        def wait_for_input():
            if self.ignored.get_text()[0].find("NO") > -1:
                already_ignored = False
            else:
                already_ignored = True
            sure = common.YesNoDialog(
                "Are you sure you want to set this Name to be ignored?" if not already_ignored \
                    else "Are you sure you want to prevent this Name from being ignored?",
                attr='default', width=31, height=6 if not already_ignored else 7, body=self.frame
            )
            if (yield from sure.listen()):
                self.frame.set_status("Performing request for 'ignore'...")
                try:
                    yield from self.handler.ignore_name('toggle', self.name)
                except Exception as exc:
                    self.frame.set_status("Unable to perform request due to error: {}".format(exc), 'error')
                    return
                self.frame.refresh()
                yield from asyncio.sleep(0.1)
                self.frame.set_status("Done.", 'body')
                yield from asyncio.sleep(1)
                self.frame.reset_status()
        asyncio.async(wait_for_input())

    @asyncio.coroutine
    def fill_stats(self):
        self.frame.set_status("Waiting for response...")
        try:
            ignore_info = yield from self.handler.is_name_ignored(self.name)
        except Exception as exc:
            if isinstance(exc, RequestError):
                if exc.status == 406:
                    self.frame.set_status("Couldn't find Name '{}'.  Maybe it's in the ignore list?".format(
                        self.name), 'error')
            else:
                self.frame.set_status("Bad response: {}".format(exc), 'error')
            return
        if list(ignore_info.values())[0]:
            self.ignored.set_text(self.ignored.get_text()[0].format('YES'))
        else:
            self.ignored.set_text(self.ignored.get_text()[0].format('NO'))
        try:
            info = yield from self.handler.name_info(self.name)
        except Exception as exc:
            if isinstance(exc, RequestError):
                if exc.status == 406:
                    self.frame.set_status("Couldn't find MAC '{}'.  Maybe it's in the ignore list?".format(
                        self.name), 'error')
            else:
                self.frame.set_status("Bad response: {}".format(exc), 'error')
            return
        self.frame.reset_status()
        self.header.set_text(self.header.get_text()[0].format(info['name']))
        self.ip_list.genericList.content[:] = []
        for ip in sorted(info['ip'], key=lambda item: socket.inet_aton(item)):
            txt = common.SelectableText(ip)
            txt.callback = self.get_ip_info
            txt = urwid.AttrWrap(txt, None, 'reveal focus')
            self.ip_list.genericList.content.append(txt)
            yield
        self.last_update.set_text(self.last_update.get_text()[0].format(
            datetime.datetime.fromtimestamp(info['last_update']).strftime("%d/%m/%Y-%H.%M.%S"),
            (datetime.datetime.now() - datetime.datetime.fromtimestamp(info['last_update']))
        ))
        changes = {}
        # {change_time: [[type, change]]}
        for change_type in info:
            if change_type.find("history") > -1:
                for change in info[change_type]:
                    if change not in changes:
                        changes[change] = []
                    changes[change].append([
                        change_type,
                        info[change_type][change]
                    ])
                    yield
        self.frame.set_status("Parsing response...")
        yield
        changes_human_readable = []
        for change_time in sorted(changes):
            for change in changes[change_time]:
                message = None
                type_ = change[0]
                if type_ == 'history':
                    change[0] = 'ip'
                if message is None:
                    message = "changed {} to '{}'".format(
                        str(change[0]), str(change[1])
                    )
                changes_human_readable.append(
                    "  · {}: {}.".format(
                        datetime.datetime.fromtimestamp(float(change_time)).strftime("%d/%m/%Y-%H.%M.%S"),
                        message
                    ))
                yield
        changes_human_readable = list(reversed(changes_human_readable))
        if changes_human_readable:
            self.set_changes(changes_human_readable)
        else:
            self.set_changes(["    No change found."])
        self.frame.reset_status()

    get_ip_info = common.get_ip_info
    get_name_info = common.get_name_info

    def set_changes(self, changes):
        changes_ = []
        for change in changes:
            txt = common.SelectableText(change)
            txt.callback = self.get_ip_info
            changes_.append(urwid.AttrWrap(txt, None, 'reveal focus'))
        self.history_list.genericList.content[:] = changes_
        self.history_list.genericList.content.set_focus(0)


common.NameView = NameView
