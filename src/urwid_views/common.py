import urwid
import re
import asyncio
from urwid_satext import sat_widgets

IPView = None  # to be imported from urwid_views.ip
MACView = None  # to be imported from urwid_views.mac
ui = None  # to be imported from main


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


class StyledEdit(urwid.WidgetWrap):
    def __init__(self, caption='', left_padding=0, caption_style=(None,None), edit_style=(None,None),
                 edit_text="", text_width=None, edit_width=20, *args, **kwargs):
        self.text = urwid.AttrWrap(urwid.Text(caption), caption_style[0], caption_style[1])
        self.edit = urwid.Edit(edit_text=edit_text, *args, **kwargs)
        if text_width is None:
            text_width = len(self.text.get_text()[0])
        text_width += left_padding
        super().__init__(urwid.Columns([
            ('fixed', text_width, urwid.Padding(self.text, left=left_padding)),
            ('fixed', edit_width, urwid.AttrWrap(self.edit, edit_style[0], edit_style[1]))
        ], dividechars=1))

class ExpandedVerticalSeparator(sat_widgets.VerticalSeparator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EntriesList(sat_widgets.List):
    def __init__(self, lesser_height, *args, **kwargs):
        self.lesser_height = lesser_height
        super().__init__(*args, **kwargs)
        self.reset_max_height()

    def reset_max_height(self):
        self.max_height = min(ui.get_cols_rows()[1], ui.get_cols_rows()[1] - self.lesser_height) or 1
        self._invalidate()

    def keypress(self, size, key):
        self.reset_max_height()
        if key == 'home':
            self.genericList.content.set_focus(0)
            return True
        if key == 'end':
            self.genericList.content.set_focus(len(self.genericList.content)-1)
            return True
        if key == 'ctrl up':
            try:
                self.genericList.content.set_focus(self.genericList.content.focus - 5)
            except IndexError:
                self.genericList.content.set_focus(0)
            return True
        if key == 'ctrl down':
            try:
                self.genericList.content.set_focus(self.genericList.content.focus + 5)
            except IndexError:
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
        self.frame.set_body(
            IPView(ip, self.handler, self.frame)
        )
        return True
    else:
        return False


def get_mac_info(self, label):
    cmp = re.compile(
        r"([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])",
    )
    mac = cmp.search(label)
    if mac:
        mac = mac.group()
        self.frame.set_status("Jumping to MAC {}...".format(mac))
        self.frame.set_body(
            MACView(mac, self.handler, self.frame)
        )
        return True
    else:
        return False


class Dialog(urwid.WidgetWrap):
    # See https://excess.org/svn/urwid/contrib/trunk/rbreu_menus.py for credits.
    """
    Creates a BoxWidget that displays a message

    Attributes:

    b_pressed -- Contains the label of the last button pressed or None if no
                 button has been pressed.
    edit_text -- After a button is pressed, this contains the text the user
                 has entered in the edit field
    """

    b_pressed = None
    edit_text = None

    _blank = urwid.Text("")
    _edit_widget = None
    _mode = None

    def __init__(self, msg, buttons, attr, width, height, body):
        """
        msg -- content of the message widget, one of:
                   plain string -- string is displayed
                   (attr, markup2) -- markup2 is given attribute attr
                   [markupA, markupB, ... ] -- list items joined together
        buttons -- a list of strings with the button labels
        attr -- a tuple (background, button, active_button) of attributes
        width -- width of the message widget
        height -- height of the message widget
        body -- widget displayed beneath the message widget
        """
        self.body = body
        self.b_pressed = None
        if attr is None:
            attr = (None, None, None)
        elif attr == 'default':
            attr = ('dialog background', 'dialog button', 'dialog button focused')

        # Text widget containing the message:
        msg_widget = urwid.Padding(urwid.Text(msg), 'center', width - 4)

        # GridFlow widget containing all the buttons:
        button_widgets = []

        for button in buttons:
            button_widgets.append(urwid.AttrWrap(
                urwid.Button(button, self._action), attr[1], attr[2]))

        button_grid = urwid.GridFlow(button_widgets, 12, 2, 1, 'center')

        # Combine message widget and button widget:
        widget_list = [msg_widget, self._blank]
        if self._edit_widget:
            widget_list.append(urwid.AttrWrap(
                self._edit_widget, attr[1], attr[2]))
        widget_list.append(button_grid)
        self._combined = urwid.AttrWrap(urwid.Filler(
            urwid.Pile(widget_list, 2)), attr[0])

        # Place the dialog widget on top of body:
        overlay = urwid.Overlay(self._combined, body, 'center', width,
                                'middle', height)

        urwid.WidgetWrap.__init__(self, overlay)

    def _action(self, button):
        """
        Function called when a button is pressed.
        Should not be called manually.
        """

        self.b_pressed = button.get_label()
        if self._edit_widget:
            self.edit_text = self._edit_widget.get_edit_text()

    # XXX: modified here
    @asyncio.coroutine
    def listen(self):
        """
        Start an event loop that listens to user input.
        """
        dim = ui.get_cols_rows()
        keys = True
        while True:
            if keys:
                ui.draw_screen(dim, self.render(dim, True))
            keys = ui.get_input()
            if "window resize" in keys:
                dim = ui.get_cols_rows()
            if "esc" in keys:
                return False
            for k in keys:
                try:
                    self.keypress(dim, k)
                except TypeError:
                    self.mouse_event(dim, *k, focus=False)
            if self.b_pressed is not None:
                return self.b_pressed
            yield


class OkDialog(Dialog):
    def __init__(self, text, attr, width, height, body):
        super().__init__(text, ['Ok'], attr, width, height, body)


class OkCancelEntryDialog(Dialog):
    def __init__(self, text, entry_caption, attr, width, height, body, int_only=False):
        if int_only:
            self._edit_widget = urwid.IntEdit(default=0, caption=entry_caption)
        else:
            self._edit_widget = urwid.Edit(caption=entry_caption)
        super().__init__(text, ['Ok', 'Cancel'], attr, width, height, body)

    @asyncio.coroutine
    def listen(self):
        pressed = yield from super().listen()
        if pressed == 'Ok':
            return True
        else:
            return False


class YesNoDialog(Dialog):
    def __init__(self, text, attr, width, height, body):
        super().__init__(text, ['Yes', 'No'], attr, width, height, body)

    @asyncio.coroutine
    def listen(self):
        pressed = yield from super().listen()
        if pressed == 'Yes':
            return True
        else:
            return False
