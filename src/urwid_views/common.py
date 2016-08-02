import urwid


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

