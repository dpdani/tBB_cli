"""

tBB_cli entering screen.

"""
import datetime
import urwid
import asyncio
from . import common


class MainView(urwid.WidgetWrap):
    def __init__(self, handler, frame):
        self.handler = handler
        self.frame = frame
        self.title = "Home"
        self.refresh()

    def refresh(self):
        self.up_hosts_label = urwid.Text("Up hosts: {}")
        self.network_label = urwid.Text("Monitoring network: {}")
        # self.hosts_list = urwid.SimpleFocusListWalker([])
        # self.hosts_list_box = urwid.ListBox(self.hosts_list)
        # self.set_hosts([])
        # self.hosts_list_adapter = urwid.BoxAdapter(self.hosts_list_box, height=24-9)
        self.hosts_list = common.EntriesList([], max_height=100)
        left_contents = [
            urwid.AttrWrap(urwid.Text("Network stats:"), 'mainview_title'),
            urwid.Padding(urwid.AttrWrap(self.up_hosts_label, ''), left=1),
            urwid.Padding(urwid.AttrWrap(self.network_label, ''), left=1),
            urwid.Divider(),
            urwid.AttrWrap(urwid.Text("Host changes (most recent first):"), 'mainview_title'),
            self.hosts_list,
        ]
        super().__init__(urwid.ListBox(urwid.SimpleFocusListWalker(left_contents)))
        asyncio.async(self.fill_stats())

    @asyncio.coroutine
    def fill_stats(self):
        self.frame.set_status("Waiting for response...")
        try:
            stats = yield from self.handler.stats()
        except Exception as exc:
            self.frame.set_status("Bad response: {}".format(exc), 'error')
            return
        self.frame.reset_status()
        self.up_hosts_label.set_text(str(self.up_hosts_label.get_text()[0]).format(stats['up_hosts']))
        self.network_label.set_text(str(self.network_label.get_text()[0]).format(stats['network']))
        yield from self.fill_changes()

    @asyncio.coroutine
    def fill_changes(self):
        self.frame.set_status("Waiting for response...")
        try:
            ip_changes = yield from self.handler.ip_host_changes('all', '1.1.1-0.0.0', 'now')  # all changes since tBB start
        except Exception as exc:
            self.frame.set_status("Bad response: {}".format(exc), 'error')
            return
        changes = {}
        # {change_time: [[ip, type, change]]}
        for ip in ip_changes:
            for change_type in ip_changes[ip]:
                for change in ip_changes[ip][change_type]:
                    if change not in changes:
                        changes[change] = []
                    changes[change].append([
                        ip,
                        change_type,
                        ip_changes[ip][change_type][change]
                    ])
                    yield
        self.frame.set_status("Parsing response...")
        yield
        changes_human_readable = []
        for change_time in sorted(changes):
            for change in changes[change_time]:
                message = None
                type_ = change[1]
                if type_ == 'is_up_history':
                    if change[2]:
                        message = "went up"
                    else:
                        message = "went down"
                elif type_ == 'history':
                    change[1] = "IP"
                elif type_ == 'mac_history':
                    change[1] = 'mac'
                elif type_ == 'discovery_history':
                    change[1] = 'discovery method'
                if message is None:
                    message = "changed {} to '{}'".format(
                        str(change[1]), str(change[2])
                    )
                changes_human_readable.append(
                    " - {}: {} {}.".format(
                        datetime.datetime.fromtimestamp(float(change_time)).strftime("%d/%m/%Y-%H.%M.%S"),
                        str(change[0]).upper(), message
                ))
                yield
        changes_human_readable = list(reversed(changes_human_readable))
        if changes_human_readable:
            self.set_hosts(changes_human_readable)
        else:
            self.set_hosts(["    No change found."])
        self.frame.reset_status()

    get_ip_info = common.get_ip_info

    def set_hosts(self, hosts):
        hosts_ = []
        for host in hosts:
            txt = common.SelectableText(host)
            txt.callback = self.get_ip_info
            hosts_.append(urwid.AttrWrap(txt, None, 'reveal focus'))
        self.hosts_list.genericList.content[:] = hosts_
        self.hosts_list.genericList.content.set_focus(0)

    def keypress(self, size, key):
        self.hosts_list.max_height = size[1] - 5
        return super().keypress(size, key)
