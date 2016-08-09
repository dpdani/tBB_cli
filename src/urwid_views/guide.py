"""

tBB_cli guide view.

"""

import urwid
import asyncio


class GuideView(urwid.WidgetWrap):
    def __init__(self, frame):
        self.frame = frame
        self.title = "Guide"
        blank = urwid.AttrWrap(urwid.Divider(), 'body')
        content = [
            urwid.AttrWrap(urwid.Text("tBB CLI Guide", 'center'), 'header'),
            urwid.Text(
"""||
     About tBB.||
  tBB is a service capable of keeping track of changes that
occur in a network.
It periodically checks every host on the network in order
to do so.||
  tBB provides ways to prevent hosts from hiding right out---
of-the-box. It checks the presence of an IP by both check--
ing its ICMP response and its TCP response.
tBB is also able to detect a host's MAC address while
doing the periodic checks.||
  While keeping the network tracked, tBB is instructed to
keep record of the changes on the network and these
changes are available for end-users to monitor with any
tBB front-end. A tBB front-end is a program running
independently from tBB which allows end-users to access
the data tBB is collecting.||
  As of today, the only officially supported tBB front-end
is tBB_cli (the one you're using right now ;) ).||
  For further details on tBB please refer to its documentation.||
||||
     About tBB_cli.||
  tBB_cli is the only front-end officially supported.||
  It is based on command line terminals to provide its user
interface, but it's not command based. This means that,
although the interface might not really look appealing, it
will still be user friendly.||
  Here follows a quick walkthrough of tBB_cli usage.||
||
     Gotchas.||
  There are a couple gotchas you need to be aware of when
using tBB_cli for the first time.||
  For many graphical elements in tBB_cli you'll find that
mouse interaction is actually correctly handled, but for
some it is not (any dialog, for instance). Therefore, it
is important to remember that while mouse interaction isn't
fully reliable, keyboard interaction is guaranteed to work.||
  There are many lists in tBB_cli that display important
information. Many of them have a peculiar behaviour regarding
window resizing: when you resize the terminal window you're
running tBB_cli on, you'll often see lists not being correctly
resized and keep displaying their elements as if the resize
didn't happen. To fix this behaviour, simply focus the list and
scroll down or up. You'll now see the list being correctly displayed.
Talking about lists, did you know that almost all of them support
the "home" and "end" buttons?||
  You'll probably have already noticed that you cannot select
text inside tBB_cli as you would normally do in your terminal
application. This is tBB_cli default behaviour, but if you
would like to select some text in tBB_cli (to do some copy-pasting,
for instance) you can override this behaviour by holding shift
and then selecting text on the screen. Note: screen selection and
copy-pasting capabilities and key bindings depend on your
terminal application.||
||
     Navigation in tBB_cli.||
  Before explaining each view tBB_cli offers, let's take a
quick look at how you can navigate between each one of them.||
  Right beneath the top bar you'll notice a line displayed in
gray-ish. That line indicates the position you have right now
in the navigation content. For instance, if you came reading
this guide from the Welcome page you would see something like:
"tBB →  Guide", but if you came here from an IP view, you might
see something like: "tBB →  Home →  IP 192.168.11.237 →  Guide".||
  Regardless of what your current view is, you can use the following
commands:||
    - w      ->    jump to the previous view (if there is any).||
    - e      ->    jump to the next view (if there is any).||
    - h      ->    jump to this guide (happy to see you here dude :) ).||
    - q|esc  ->    close tBB_cli (a prompt will be shown).||
    - r|F5   ->    refresh the current view.||
  These commands can also be found at the top of the screen
and are designed to provide an easy-to-understand and quick---
to-use keyboard layout.||
||
     The Welcome view.||
  This is the view you're prompted into when launching
tBB_cli. In this screen you can see two text fields that
are used to log into the tBB service. The first one is captioned
"tBB location". It is asking you to provide a socket in which the
tBB service can be found. For instance, let's say I have tBB
running on my machine at port 1984 (the default port for tBB).
In this case I would enter "localhost:1984" in the location field.
Let's also say that I have another instance of tBB running on
port 1985 of a remote server located at 192.168.100.200. In this
case I'll enter "192.168.100.200:1985" in the location field.||
  Please remember that if tBB is set to be able to be detected
outside the loopback network you're going to need to enter
your machine IP address instead of localhost, just as you would
do for remote tBB instances, even if it is running on your
local machine.||
  Please note that tBB_cli doesn't handle DNS resolution.||
  In the password field you need to enter the password the
instance of tBB you have selected is using.||
  When you're all set, press the "Ok" button placed at the middle
of the screen to log in.||
  Or don't.||
  It's up to you. c:||
||
     The Home view.||
  This view is presented to you once you successfully log into
tBB.||
  On the screen you can see statistics related to the tBB instance
such as the location from which it is running and whether or not
the information exchange with the front-end is securely encrypted.||
  Right beneath tBB service information, you'll see statistics
about the network tBB is instructed to watch such as how many hosts
are up on the network or the network boundaries.||
  The main component you should be seeing is the Changes list.
In this list are shown the changes that have occurred on the network
since tBB started monitoring it. They are ordered by the time they
occurred, displaying the most recent at the top of the list for
convenience.||
  On the right-hand side of the screen you can see some useful
buttons. They are mostly self-explanatory, but I'll cover them here
anyways:||
    - Settings: this button takes you to the Settings view.||
    - Up Hosts: this button takes you to the Up Hosts view.||
    - Ignored Hosts: this button takes you to the Ignored Hosts view.||
    - About IP...: this button prompts you an IP address and will
redirect you to the appropriate IP view.||
    - About MAC...: this button prompts you a MAC address and will
redirect you to the appropriate MAC view.||
||
     The IP view.||
  This view is displayed whenever you want to watch an IP address,
whatever your preceding view was this is the page you should see
when pressing enter on a graphic element that has an IP address in it.||
  It shows you useful information about the host, such as
whether it is up or not, its mac, and so on.||
  You should be able to see two commands at the right hand side
of the screen:||
    - Ignore: set this IP to be ignored in the next checks.||
    - Set priority: set the this IP's priorities over other IPs.
See tBB documentation for how priorities works.||
||
    The MAC view.||
  This view is very similar to the IP view. It appears whenever
you want to watch a MAC address, whatever your preceding view
was this is the page you should see when pressing enter on a
graphic element that has a MAC address in it.||
  Differently from the IP view, you should consider that,
since a MAC address isn't bound to a single IP address,
in the IP field there might be more than one IP.||
||
    The Settings view.||
  This view shows you the possible ways you can set tBB
to work. As of today, there are only a few parameters you can set.
Here they are explained:||
    - Time between checks: this is the time each tracker waits
before checking a new IP. A higher value in this field means a
lesser weight of tBB on the network. If you think that tBB is
slowing the network down too much you might want to change
this parameter.||
    - Maximum seconds randomly added: seconds to add to
"Time between checks". Seconds actually added vary from 0
to the value here specified randomly. This behaviour has
been implemented in order to make more difficult for hosts
to detect tBB presence.||
    - Automatically ignore broadcasts: set this to 'Yes' if you
want broadcasts found during checks to be automatically ignored.
In case this is set to 'No', even if tBB detects a broadcast
while working, it will be repeatedly checked (and failed) in
every check iteration.||
|||||| Have fun! :D
""".replace('--\n', '').replace('\n', ' ').replace('|| ', '\n').replace('||', '\n')),
            blank,
        ]
        self.listbox = urwid.ListBox(urwid.SimpleFocusListWalker(content))
        self.listbox = urwid.AttrWrap(self.listbox, 'body')
        super().__init__(self.listbox)

    def refresh(self):
        pass
