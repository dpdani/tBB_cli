"""

IP view.

"""

import datetime
import urwid
import asyncio
import re
from . import common
from urwid_satext.sat_widgets import List


class IPView(urwid.WidgetWrap):
    def __init__(self, ip, handler, frame):
        self.ip = ip
        self.handler = handler
        self.frame = frame
        self.title = urwid.Text("Information about IP '{}':")
        self.up = urwid.Text("Up: {}.")
        self.mac = common.SelectableText("MAC: {}.")
        self.mac.callback = self.get_mac_info
        self.mac = urwid.AttrWrap(self.mac, None, 'reveal focus')
        self.method = urwid.Text("Discovery method: {}.")
        self.last_check = urwid.Text("Last checked: {} ({} ago).")
        self.last_seen = urwid.Text("Last seen: {} ({} ago).")
        self.history_list = List([], max_height=100)
        contents = [
            urwid.AttrWrap(self.title, 'mainview_title'),
            urwid.Padding(self.up, left=1),
            urwid.Padding(self.mac, left=1),
            urwid.Padding(self.method, left=1),
            urwid.Padding(self.last_seen, left=1),
            urwid.Padding(self.last_check, left=1),
            urwid.Divider(),
            urwid.AttrWrap(urwid.Text("History (most recent first):"), 'mainview_title'),
            self.history_list,
        ]
        super().__init__(urwid.ListBox(urwid.SimpleFocusListWalker(contents)))
        asyncio.async(self.fill_stats())

    @asyncio.coroutine
    def fill_stats(self):
        self.frame.set_status("Waiting for response...")
        try:
            info = yield from self.handler.ip_info(self.ip)
        except Exception as exc:
            self.frame.set_status("Bad response: {}".format(exc), 'error')
            return
        self.frame.reset_status()
        self.title.set_text(self.title.get_text()[0].format(info['ip']))
        if info['is_up']:
            self.up.set_text(self.up.get_text()[0].format('YES'))
        else:
            self.up.set_text(self.up.get_text()[0].format('NO'))
        self.mac.set_text(self.mac.get_text()[0].format(info['mac']))
        self.method.set_text(self.method.get_text()[0].format(info['method']))
        self.last_seen.set_text(self.last_seen.get_text()[0].format(
            datetime.datetime.fromtimestamp(info['last_seen']).strftime("%d/%m/%Y-%H.%M.%S"),
            (datetime.datetime.now() - datetime.datetime.fromtimestamp(info['last_seen']))
        ))
        self.last_check.set_text(self.last_check.get_text()[0].format(
            datetime.datetime.fromtimestamp(info['last_check']).strftime("%d/%m/%Y-%H.%M.%S"),
            (datetime.datetime.now() - datetime.datetime.fromtimestamp(info['last_check']))
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
                if type_ == 'is_up_history':
                    if change[1]:
                        message = "went up"
                    else:
                        message = "went down"
                elif type_ == 'mac_history':
                    change[0] = 'mac'
                elif type_ == 'discovery_history':
                    change[0] = 'discovery method'
                if message is None:
                    message = "changed {} to '{}'".format(
                        str(change[0]), str(change[1])
                    )
                changes_human_readable.append(
                    " - {}: {}.".format(
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

    def get_ip_info(self, label):
        self.frame.set_status(label)
        cmp = re.compile(
            r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
        )
        res = cmp.findall(label)
        self.frame.set_status("iP: {}".format(res))
        if res:
            ip = res[0]
            self.frame.set_status("Jumping to IP {}...".format(ip))
            ip_view = IPView(ip, self.handler, self.frame)
            ip_view.app_quit = self.app_quit
            self.frame.reset_status()
            self.frame.set_body(ip_view)

    def get_mac_info(self, label):
        self.frame.set_status(label)
        cmp = re.compile(
            r"\b([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])\b",
        )
        res = cmp.findall(label)
        self.frame.set_status("iP: {}".format(res))
        if res:
            ip = res[0]
            self.frame.set_status("Jumping to IP {}...".format(ip))
            ip_view = IPView(ip, self.handler, self.frame)
            ip_view.app_quit = self.app_quit
            self.frame.reset_status()
            self.frame.set_body(ip_view)

    def set_changes(self, changes):
        changes_ = []
        for change in changes:
            txt = common.SelectableText(change)
            txt.callback = self.get_ip_info
            changes_.append(urwid.AttrWrap(txt, None, 'reveal focus'))
        self.history_list.genericList.content[:] = changes_
        self.history_list.genericList.content.set_focus(0)
        # self.hosts_list_adapter.height = 5

    def keypress(self, size, key):
        self.history_list.max_height = size[1] - 8
        return super().keypress(size, key)
