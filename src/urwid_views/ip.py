"""

IP view.

"""

import datetime
import urwid
import asyncio
from . import common
from tBB_requests import RequestError


class IPView(urwid.WidgetWrap):
    def __init__(self, ip, handler, frame):
        self.ip = ip
        self.handler = handler
        self.frame = frame
        self.title = "IP {}".format(ip)
        self.refresh()

    def refresh(self):
        self.header = urwid.Text("Information about IP '{}':")
        self.up = urwid.Text("Up: {}.")
        self.names_list = common.EntriesList(lesser_height=0, fixed_height=3, options=[])
        self.mac = common.SelectableText("MAC: {}.")
        self.mac.callback = self.get_mac_info
        self.mac = urwid.AttrWrap(self.mac, None, 'reveal focus')
        self.method = urwid.Text("Discovery method: {}.")
        self.last_check = urwid.Text("Last checked: {} ({} ago).")
        self.last_seen = urwid.Text("Last seen: {} ({} ago).")
        self.ignored = urwid.Text("Ignored: {}.")
        self.priority_txt = urwid.Text("Priority: {}.")
        self.history_list = common.EntriesList(lesser_height=19, options=[], max_height=100)
        left_contents = [
            urwid.AttrWrap(urwid.Text("IP View", 'center'), 'header'),
            urwid.AttrWrap(self.header, 'mainview_title'),
            urwid.Padding(self.up, left=1),
            urwid.Padding(urwid.Text("Names:"), left=1),
            urwid.Padding(self.names_list, left=3),
            urwid.Padding(self.mac, left=1),
            urwid.Padding(self.method, left=1),
            urwid.Padding(self.last_seen, left=1),
            urwid.Padding(self.last_check, left=1),
            urwid.Padding(self.ignored, left=1),
            urwid.Padding(self.priority_txt, left=1),
            urwid.Divider(),
            urwid.AttrWrap(urwid.Text("History (most recent first):"), 'mainview_title'),
            self.history_list,
        ]
        self.cols = urwid.Columns([
            ('weight', 3, urwid.ListBox(urwid.SimpleFocusListWalker(left_contents))),
            common.ExpandedVerticalSeparator(
                urwid.ListBox(urwid.SimpleFocusListWalker([
                    urwid.Button("Ignore", on_press=self.ignore),
                    urwid.Button("Set priority", on_press=self.priority),
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
                "Are you sure you want to set this IP to be ignored?" if not already_ignored \
                else "Are you sure you want to prevent this IP from being ignored?",
                attr='default', width=30, height=6 if not already_ignored else 7, body=self.frame
            )
            if (yield from sure.listen()):
                self.frame.set_status("Performing request for 'ignore'...")
                try:
                    yield from self.handler.ignore('toggle', self.ip)
                except Exception as exc:
                    self.frame.set_status("Unable to perform request due to error: {}".format(exc), 'error')
                    return
                self.frame.refresh()
                yield from asyncio.sleep(0.1)
                self.frame.set_status("Done.", 'body')
                yield from asyncio.sleep(1)
                self.frame.reset_status()
        asyncio.async(wait_for_input())

    def priority(self, user_data):
        @asyncio.coroutine
        def wait_for_input():
            try:
                priority = list((yield from self.handler.get_priority(self.ip)).values())[0]
            except Exception as exc:
                self.frame.set_status("Unable to perform request due to error: {}".format(exc), 'error')
                return
            sure = common.OkCancelEntryDialog(
                "Please, enter new priority for '{}'. Current priority is {}.".format(self.ip, priority),
                entry_caption='', int_only=False, attr='default', width=30, height=8, body=self.frame
            )
            if (yield from sure.listen()):
                try:
                    yield from self.handler.set_priority(self.ip, int(sure.edit_text))
                except ValueError:
                    self.frame.set_status("Please, insert a valid integer. Got: '{}'.".format(sure.edit_text), 'error')
                    return
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
            ignore_info = yield from self.handler.is_ignored(self.ip)
        except RequestError as exc:
            if exc.status == 406:
                self.frame.set_status("Couldn't find IP '{}'.  Maybe it's in the ignore list?".format(
                    self.ip), 'error')
            else:
                self.frame.set_status("Bad response: {}".format(exc), 'error')
            return
        except Exception as exc:
            self.frame.set_status("Bad response: {}".format(exc), 'error')
            return
        if list(ignore_info.values())[0]:
            self.ignored.set_text(self.ignored.get_text()[0].format('YES'))
        else:
            self.ignored.set_text(self.ignored.get_text()[0].format('NO'))
        try:
            priority = list((yield from self.handler.get_priority(self.ip)).values())[0]
        except Exception as exc:
            self.frame.set_status("Bad response: {}".format(exc), 'error')
            return
        self.priority_txt.set_text(self.priority_txt.get_text()[0].format(str(priority)))
        try:
            info = yield from self.handler.ip_info(self.ip)
        except Exception as exc:
            self.frame.set_status("Bad response: {}".format(exc), 'error')
            return
        self.frame.reset_status()
        self.header.set_text(self.header.get_text()[0].format(info['ip']))
        if info['is_up']:
            self.up.set_text(self.up.get_text()[0].format('YES'))
        else:
            self.up.set_text(self.up.get_text()[0].format('NO'))
        # self.name.set_text(self.name.get_text()[0].format(info['name']))
        if info['name'] is None:
            self.names_list.genericList.content.append(
                urwid.AttrWrap(common.SelectableText("No names found."),
                    None, 'reveal focus')
            )
        else:
            for name in sorted(info['name']):
                txt = common.SelectableText("':{}:'".format(name))
                txt.callback = self.get_name_info
                txt = urwid.AttrWrap(txt, None, 'reveal focus')
                self.names_list.genericList.content.append(txt)
                yield
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
                elif type_ == 'name_history':
                    change[0] = 'name'
                    change[1] = ':{}:'.format(change[1])
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
            yield
        changes_human_readable = list(reversed(changes_human_readable))
        if changes_human_readable:
            self.set_changes(changes_human_readable)
        else:
            self.set_changes(["    No change found."])
        self.frame.reset_status()

    get_ip_info = common.get_ip_info
    get_mac_info = common.get_mac_info
    get_name_info = common.get_name_info
    get_all_info = common.get_all_info

    def set_changes(self, changes):
        changes_ = []
        for change in changes:
            txt = common.SelectableText(change)
            txt.callback = self.get_all_info
            changes_.append(urwid.AttrWrap(txt, None, 'reveal focus'))
        self.history_list.genericList.content[:] = changes_
        self.history_list.genericList.content.set_focus(0)


common.IPView = IPView
