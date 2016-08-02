import urwid
import re
from urwid_satext import sat_widgets

IPView = None  # to be imported from urwid_views.ip
MACView = None  # to be imported from urwid_views.mac


class SelectableText(urwid.Text):
    def callback(self, data):
        pass

    def selectable(self):
        return True

    def keypress(self, size, key):
        if key in (' ', 'enter'):
            self.callback(self.text)
            return True
        return key


class EntriesList(sat_widgets.List):
    def keypress(self, size, key):
        if key == 'home':
            self.genericList.content.set_focus(0)
            return True
        if key == 'end':
            self.genericList.content.set_focus(len(self.genericList.content)-1)
            return True
        return super().keypress(size, key)


def get_ip_info(self, label):
    cmp = re.compile(
        r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}",
    )
    res = cmp.findall(label)
    if res:
        ip = res[0]
        self.frame.set_status("Jumping to IP {}...".format(ip))
        ip_view = IPView(ip, self.handler, self.frame)
        ip_view.app_quit = self.app_quit
        self.frame.reset_status()
        self.frame.set_body(ip_view)


def get_mac_info(self, label):
    cmp = re.compile(
        r"([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])",
    )
    mac = cmp.search(label)
    if mac:
        mac = mac.group()
        self.frame.set_status("Jumping to MAC {}...".format(mac))
        mac_view = MACView(mac, self.handler, self.frame)
        mac_view.app_quit = self.app_quit
        self.frame.reset_status()
        self.frame.set_body(mac_view)


class OkPopUpDialog(urwid.WidgetWrap):
    signals = ['close']
    def __init__(self, text):
        self.ok_button = urwid.Button("Ok")
        urwid.connect_signal(self.ok_button, 'click', self.on_ok)
        pile = urwid.Pile([
            urwid.Text(text),
            urwid.Divider(),
            self.ok_button
        ])
        fill = urwid.Filler(pile)
        super().__init__(fill)

    def on_ok(self, button):
        self._emit('close')


class OkPopUp(urwid.PopUpLauncher):
    def __init__(self, attach_to, text, left=0, top=1, width=32, height=7):
        self.text = text
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        super().__init__(attach_to)
        self.open_pop_up()

    def create_pop_up(self):
        pop_up = OkPopUpDialog(self.text)
        urwid.connect_signal(
            pop_up, 'close',
            lambda button: self.close_pop_up()
        )
        return pop_up

    def get_pop_up_parameters(self):
        return {
            'left': self.left,
            'top': self.top,
            'overlay_width': self.width,
            'overlay_height': self.height
        }

