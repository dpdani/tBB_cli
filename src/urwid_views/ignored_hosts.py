"""

tBB_cli ignored hosts view.

"""
import datetime
import urwid
import asyncio
from . import common
import socket
from tBB_requests import RequestError
from urwid_satext.sat_widgets import VerticalSeparator


class IgnoredHostsView(urwid.WidgetWrap):
    def __init__(self, handler, frame):
        self.handler = handler
        self.frame = frame
        self.title = "Ignored Hosts"
        self.refresh()

    def refresh(self):
        self.ips_list = common.EntriesList(options=["Waiting...", "  ...", "  ..."], max_height=100, lesser_height=8)
        self.macs_list = common.EntriesList(options=["Waiting...", "  ...", "  ..."], max_height=100, lesser_height=8)
        self.cols = urwid.Columns([
            self.ips_list,
            VerticalSeparator(
                self.macs_list,
            ),
        ])
        super().__init__(urwid.ListBox(urwid.SimpleFocusListWalker([
            urwid.AttrWrap(urwid.Text("Ignored Hosts", 'center'), 'header'),
            urwid.Divider(),
            self.cols
        ])))
        asyncio.async(self.fill_hosts())

    @asyncio.coroutine
    def fill_hosts(self):
        self.frame.set_status("Waiting for ip hosts response...")
        try:
            ip_hosts = yield from self.handler.ignored_ips()
        except Exception as exc:
            self.frame.set_status("Bad response: {}".format(exc), 'error')
            return
        ip_hosts = sorted(ip_hosts, key=lambda item: socket.inet_aton(item))
        self.ips_list.genericList.content[:] = []
        self.frame.set_status("Parsing ip hosts response...")
        for host in ip_hosts:
            try:
                host_info = yield from self.handler.ip_info(host)
            except RequestError as exc:
                if exc.status == 406:
                    txt = common.SelectableText("  · {}:\nCouldn't get more information. "
                                                "Probably due to the fact that it had been"
                                                "ignored since tBB service start.".format(host))
                    self.macs_list.genericList.content.append(urwid.AttrWrap(txt, None, 'reveal focus'))
                    continue
                else:
                    self.frame.set_status("Bad response: {}".format(exc), 'error')
                    return
            except Exception as exc:
                self.frame.set_status("Bad response while looking for {}: {}".format(host, exc), 'error')
                return
            txt = common.SelectableText(" · {}:\n     {}\n     method: {}\n     last seen: {} ({} ago).".format(
                host, host_info['mac'], host_info['method'],
                datetime.datetime.fromtimestamp(host_info['last_seen']).strftime("%d/%m/%Y-%H.%M.%S"),
                (datetime.datetime.now() - datetime.datetime.fromtimestamp(host_info['last_seen']))
            ))
            txt.callback = self.get_ip_info
            self.ips_list.genericList.content.append(urwid.AttrWrap(txt, None, 'reveal focus'))
            yield
        if len(self.ips_list.genericList.content) <= 0:
            self.ips_list.genericList.content[:] = [urwid.Text("No IP found.")]
        self.frame.set_status("Waiting for mac hosts response...")
        yield
        try:
            mac_hosts = yield from self.handler.ignored_macs()
        except Exception as exc:
            self.frame.set_status("Bad response: {}".format(exc), 'error')
            return
        mac_hosts = sorted(mac_hosts)
        self.macs_list.genericList.content[:] = []
        self.frame.set_status("Parsing mac hosts response...")
        for host in mac_hosts:
            try:
                host_info = yield from self.handler.mac_info(host)
            except RequestError as exc:
                if exc.status == 406:
                    txt = common.SelectableText("  · {}:\n      Couldn't get more information. "
                                                "This is probably due to the fact that it had been "
                                                "ignored since tBB service start.".format(host.upper()))
                    self.macs_list.genericList.content.append(urwid.AttrWrap(txt, None, 'reveal focus'))
                    continue
                else:
                    self.frame.set_status("Bad response: {}".format(exc), 'error')
                    return
            except Exception as exc:
                self.frame.set_status("Bad response while looking for {}: {}".format(host, exc), 'error')
                return
            txt = common.SelectableText("  · {}:\n      {}\n      last seen: {} ({} ago).".format(
                host.upper(), host_info['ip'],
                datetime.datetime.fromtimestamp(host_info['last_seen']).strftime("%d/%m/%Y-%H.%M.%S"),
                (datetime.datetime.now() - datetime.datetime.fromtimestamp(host_info['last_seen']))
            ))
            txt.callback = self.get_mac_info
            self.macs_list.genericList.content.append(urwid.AttrWrap(txt, None, 'reveal focus'))
            yield
        if len(self.macs_list.genericList.content) <= 0:
            self.macs_list.genericList.content[:] = [urwid.Text("No MAC found.")]
        self.frame.reset_status()

    get_ip_info = common.get_ip_info
    get_mac_info = common.get_mac_info
