"""

MAC view.

"""

import datetime
import urwid
import asyncio
from tBB_requests import RequestError
from . import common


class MACView(urwid.WidgetWrap):
    def __init__(self, mac, handler, frame):
        self.mac = mac
        self.handler = handler
        self.frame = frame
        self.title = urwid.Text("Information about MAC '{}':")
        self.up = urwid.Text("Up: {}.")
        self.ip = common.SelectableText("IP: {}.")
        self.ip.callback = self.get_ip_info
        self.ip = urwid.AttrWrap(self.ip, None, 'reveal focus')
        self.last_update = urwid.Text("Last updated: {} ({} ago).")
        self.last_seen = urwid.Text("Last seen: {} ({} ago).")
        self.history_list = common.EntriesList([], max_height=100)
        contents = [
            urwid.AttrWrap(self.title, 'mainview_title'),
            urwid.Padding(self.up, left=1),
            urwid.Padding(self.ip, left=1),
            urwid.Padding(self.last_seen, left=1),
            urwid.Padding(self.last_update, left=1),
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
            info = yield from self.handler.mac_info(self.mac)
        except Exception as exc:
            if isinstance(exc, RequestError):
                if exc.status == 406:
                    self.frame.set_status("Bad response. Couldn't find MAC.  Maybe '{}' is in the ignore list?".format(
                        self.mac), 'error')
            else:
                self.frame.set_status("Bad response: {}".format(exc), 'error')
            return
        self.frame.reset_status()
        self.title.set_text(self.title.get_text()[0].format(info['mac'].upper()))
        if info['is_up']:
            self.up.set_text(self.up.get_text()[0].format('YES'))
        else:
            self.up.set_text(self.up.get_text()[0].format('NO'))
        self.ip.set_text(self.ip.get_text()[0].format(info['ip']))
        self.last_seen.set_text(self.last_seen.get_text()[0].format(
            datetime.datetime.fromtimestamp(info['last_seen']).strftime("%d/%m/%Y-%H.%M.%S"),
            (datetime.datetime.now() - datetime.datetime.fromtimestamp(info['last_seen']))
        ))
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
                if type_ == 'is_up_history':
                    if change[1]:
                        message = "went up"
                    else:
                        message = "went down"
                elif type_ == 'history':
                    change[0] = 'ip'
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

    get_ip_info = common.get_ip_info
    get_mac_info = common.get_mac_info

    def set_changes(self, changes):
        changes_ = []
        for change in changes:
            txt = common.SelectableText(change)
            txt.callback = self.get_ip_info
            changes_.append(urwid.AttrWrap(txt, None, 'reveal focus'))
        self.history_list.genericList.content[:] = changes_
        self.history_list.genericList.content.set_focus(0)

    def keypress(self, size, key):
        self.history_list.max_height = size[1] - 8
        return super().keypress(size, key)


common.MACView = MACView
