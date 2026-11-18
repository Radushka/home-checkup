# Home Checkup

**A quiet log for every home.**

A calm daily checkup of your Home Assistant, in plain words. Free.

Once a day it tells you if your home is healthy, or which few things need a look:

1. Errors in the log, grouped by cause and by the integration that caused them.
2. Integrations that did not start.
3. Leftover entities and devices that nothing provides any more.
4. Entities that have been unavailable for a long time.
5. Automations and scripts that point to things that no longer exist.
6. Helpers that nothing seems to use.
7. Batteries running low (under 15%), so you can change them before a device stops. Phones, tablets and
   computers are left out, because you charge them.

For log errors it does more than count them:

1. It adds one plain line on what a common error means.
2. It offers one next step: "See the update" when an update that may fix it is ready, "Sign in again",
   "Open the devices", or "Open dashboards" for a template that reads something missing.
3. It tells start-up noise (errors only in the first minutes after a restart) from real, ongoing problems.
   Start-up noise is shown, but not counted. A start-up error from an earlier start leaves the page as soon as
   Home Assistant starts again, and it returns only if it happens again.
4. It keeps its own short error history, so it still sees errors that keep coming back after a restart.
5. After you take the next step, it looks again later and tells you when the errors stopped.

Tap a log line to see the full error right on the page, with a "Copy" button for a forum post or a bug
report. You do not have to search the whole log. Lines that differ only by a number are counted as one, and
a line that only says "Unexpected exception" shows the real error as its title.

Anything that first showed in the last 24 hours gets a small "New" mark.

For automations that point to missing things, it says when each one last ran (still-running ones first) and
offers a one-tap fix where the answer is clear:

1. "Use the new one" when an entity was renamed, for example by an integration update. Only when there is
   exactly one clear match.
2. "Remove this step" when one step acts on something that no longer exists and the rest of the automation
   still works. Only that step is taken out.
3. "Turn off" when the integration or device it needs was removed, so it can never work again.
4. "Choose another" when there is no clear answer. You pick what the step should use now, from a list of the
   same kind (a light for a light). This works for automations and for scripts made in the UI.

An automation or script that you wrote by hand in another YAML file (a package, for example) gets no button,
because Home Assistant's editor cannot change it. The line says where it is instead, such as
"Written in packages/scripts.yaml, line 102", so you can change it there.

It never changes, removes or restarts anything by itself. For a few clear cases (leftover entities, helpers
made in the UI that nothing uses, and the automation fixes above) it offers a safe fix on its page. A fix happens only when an admin taps it.
It shows the exact list first, makes a backup, and can be undone for 30 days.

Helpers written in YAML files are listed, but the button cannot remove them. The page marks them, and you remove
their lines from your YAML files yourself.

## Ask for a fix

Some lines have no fix button yet. On those you can press "Ask" to tell us that you want a fix.

1. Nothing is sent by itself. A small sheet shows every word first, and it is sent only when you press Send.
2. What is sent: the kind of problem, the name of the integration, the error text as you see and can edit it,
   the versions of Home Checkup and Home Assistant, and your language. A note and an email address are optional.
3. What is never sent: names of devices, people or places, addresses, tokens, or anything about your account.
4. The request goes to lukaps.com, to the makers of Home Checkup. The server keeps no IP address.
5. We count how many homes ask for the same fix, and build the most wanted ones first.

After you asked, the page can tell you what happened: "A fix is planned" or "A fix arrived in version X".
For this, the page sends only the codes of your own requests to lukaps.com, at most once every few hours and
only while the page is open. A code says nothing about your home. If you never press Send, nothing is ever
sent.

These are the only times Home Checkup sends anything outside your home.

## Works with Home Assistant's own Repairs

Home Checkup adds to Home Assistant; it does not replace or change any part of it.

1. Repairs belongs to Home Assistant. Home Checkup adds at most one note there, never one per problem.
   The note, the Home Checkup page, the sensor and the Studio card always show the same number. A short burst
   of log errors is listed on the page under "To watch". It is counted only when it keeps coming back.
2. Many people never open their log, so the note lists log errors too, but only real problems: errors that
   keep coming back (seen in at least 3 different hours of the last 24), and brand new errors once Home Checkup
   has watched for 2 days. One short burst, such as a network drop, and start-up noise stay on the Home Checkup
   page only.
3. If Home Assistant already shows a repair for an integration, Home Checkup does not count that integration's
   problems again in its note. They stay on the Home Checkup page.
4. It never hides, changes or dismisses Home Assistant's own repairs, or those of other integrations.
5. You can turn the note off: Settings > Devices and services > Home Checkup > Configure.

## Your privacy

Home Checkup is built with your privacy in mind. This is exactly what it does and does not do.

1. Everything stays in your home. Home Checkup sends nothing to any server, ours included.
2. It never opens `secrets.yaml`, or any file named like a secret, password, token or key file.
3. It never opens the files where Home Assistant keeps passwords, keys and sign-ins
   (such as `.storage/core.config_entries`, `.storage/auth` and the cloud files).
4. From your YAML files and dashboards it picks out only helper names (like `input_boolean.guest_mode`),
   the names of your scripts and automations, and the file name and line number of a broken step.
   All other text is dropped at once and never kept.
5. For each kind of error it keeps the full text of the newest one, for the "full error" view. It stays in
   your home, in Home Assistant's own storage folder, for 7 days.
6. Passwords, keys, tokens, sign-in addresses and email addresses in log messages are hidden
   before a message is kept or shown.
7. Log messages can name people and devices (for example "Anna's iPhone" or a serial number). They are shown
   only on your own Home Checkup page, to admins, and never leave your home.
8. Nothing is written to disk except your own "Ignore" list, a 7-day error history (counts and the hidden-name
   message text only, in Home Assistant's own storage folder) and, when you use a safe fix, its backup
   (in `/config/home_checkup_backups`, kept in your home).

## What it gives you

1. A Home Checkup page in the sidebar, for admins. It shows the full list, with a link to each item and an "Ignore" button for things that are fine as they are. "Check now" runs the checkup at once.
2. A sensor, "Things to look at" (0 means healthy).
3. One note in Settings > System > Repairs when something needs a look. It is always one note, never one per problem, and it goes away by itself when all is well. You can turn it off in the Home Checkup settings (Configure).
4. A Home Checkup card in [Dashboard Studio](https://lukaps.com/dashboardstudio/), if you use it.
