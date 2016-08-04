"""

tBB_cli settings view.

"""
import datetime
import urwid
import asyncio
from . import common


class SettingsView(urwid.WidgetWrap):
    def __init__(self, handler, frame):
        self.handler = handler
        self.frame = frame
        self.title = "Settings"
        self.refresh()

    def refresh(self):
        self.seconds = common.StyledEdit("secs:", edit_width=3, edit_style=('edit', None), align='right')
        self.minutes = common.StyledEdit("mins:", edit_width=3, edit_style=('edit', None), align='right')
        self.random_time = common.StyledEdit("Maximum seconds randomly added:", text_width=35, edit_style=('edit', None))
        self.automatically_ignore_broadcasts = None
        radio_buttons_group = []
        self.radio_buttons = [
            urwid.RadioButton(radio_buttons_group, "Yes", on_state_change=self.radiobuttons_change),
            urwid.RadioButton(radio_buttons_group, "No", on_state_change=self.radiobuttons_change)
        ]
        left_contents = [
            urwid.AttrWrap(urwid.Text("Settings", 'center'), 'header'),
            urwid.Divider(),
            urwid.Divider(),
            urwid.Columns([
                ('fixed', 36, urwid.Text("Time between checks:")),
                ('fixed', 10, self.minutes),
                 ('fixed', 9, self.seconds),
            ]),
            self.random_time,
            urwid.Columns([
                ('fixed', 36, urwid.Text("Automatically ignore broadcasts: ")),
                urwid.GridFlow(self.radio_buttons, 13, 3, 1, 'left')
            ]),
        ]
        self.cols = urwid.Columns([
            ('weight', 3, urwid.ListBox(urwid.SimpleFocusListWalker(left_contents))),
            common.ExpandedVerticalSeparator(
                urwid.ListBox(urwid.SimpleFocusListWalker([
                    urwid.Button("Save", on_press=self.on_save),
                ]))
            ),
        ])
        super().__init__(self.cols)
        asyncio.async(self.fill_stats())

    def on_save(self, user_data):
        @asyncio.coroutine
        def do_save():
            try:
                int(self.seconds.edit.get_text()[0])
            except ValueError:
                self.frame.set_status("Please insert a valid value for 'Time between checks:secs'. "
                                      "Got: '{}'. Expected to be float.".format(self.time.edit.get_text()[0]), 'error')
                return
            try:
                int(self.minutes.edit.get_text()[0])
            except ValueError:
                self.frame.set_status("Please insert a valid value for 'Time between checks:mins'. "
                                      "Got: '{}'. Expected to be float.".format(self.time.edit.get_text()[0]), 'error')
                return
            try:
                int(self.random_time.edit.get_text()[0])
            except ValueError:
                self.frame.set_status("Please insert a valid value for 'Maximum seconds randomly added'. "
                                      "Got: '{}'. Expected to be integer.".format(self.random_time.edit.get_text()[0]), 'error')
                return
            try:
                yield from self.handler.settings_set('time_between_checks', ':'.join([
                    self.minutes.edit.get_text()[0], self.seconds.edit.get_text()[0]]))
                yield from self.handler.settings_set('maximum_seconds_randomly_added', self.random_time.edit.get_text()[0])
            except Exception as exc:
                self.frame.set_status('Bad response: {}.'.format(exc), 'error')
                return
            ignore = None
            for rb in self.radio_buttons:
                if rb.get_label() == 'Yes':
                    if rb.get_state():
                        ignore = True
                        break
                ignore = False
            try:
                yield from self.handler.settings_set('auto_ignore_broadcasts', ignore)
            except Exception as exc:
                self.frame.set_status('Bad response: {}.'.format(exc), 'error')
            self.frame.refresh()
        asyncio.async(do_save())

    def radiobuttons_change(self, radio_button, new_state, user_data=None):
        if radio_button.get_label() == 'No':
            self.automatically_ignore_broadcasts = True
        elif radio_button.get_label() == 'Yes':
            self.automatically_ignore_broadcasts = False

    @asyncio.coroutine
    def fill_stats(self):
        self.frame.set_status("Waiting for response...")
        try:
            time = yield from self.handler.settings_get('time_between_checks')
            random = yield from self.handler.settings_get('maximum_seconds_randomly_added')
            ignore = yield from self.handler.settings_get('auto_ignore_broadcasts')
        except Exception as exc:
            self.frame.set_status('Bad response: {}.'.format(exc), 'error')
            return
        self.minutes.edit.set_edit_text(time[0].split(':')[0])
        self.seconds.edit.set_edit_text(time[0].split(':')[1])
        self.random_time.edit.set_edit_text(str(random[0]))
        for rb in self.radio_buttons:
            if rb.get_label() == 'Yes':
                rb.set_state(ignore[0], do_callback=False)
            elif rb.get_label() == 'No':
                rb.set_state(not ignore[0], do_callback=False)
        self.frame.reset_status()