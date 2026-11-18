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
   Start-up noise is shown, but not counted.
4. It keeps its own short error history, so it still sees errors that keep coming back after a restart.
5. After you take the next step, it looks again later and tells you when the errors stopped.

Anything that first showed in the last 24 hours gets a small "New" mark.

For automations that point to missing things, it says when each one last ran (still-running ones first) and
offers a one-tap fix where the answer is clear:

1. "Use the new one" when an entity was renamed, for example by an integration update. Only when there is
   exactly one clear match.
2. "Remove this step" when one step acts on something that no longer exists and the rest of the automation
   still works. Only that step is taken out.
3. "Turn off" when the integration or device it needs was removed, so it can never work again.

It never changes, removes or restarts anything by itself. For a few clear cases (leftover entities, helpers
made in the UI that nothing uses, and the automation fixes above) it offers a safe fix on its page. A fix happens only when an admin taps it.
It shows the exact list first, makes a backup, and can be undone for 30 days.

Helpers written in YAML files are listed, but the button cannot remove them. The page marks them, and you remove
their lines from your YAML files yourself.

## Install

Home Checkup installs from this repository through Home Assistant's store for custom integrations. On Home
Assistant 2026.11 and newer that is the built-in **Marketplace**. On older versions it is [HACS](https://hacs.xyz).

[![Open this repository in Home Assistant.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Radushka&repository=home-checkup&category=integration)

### Home Assistant 2026.11 and newer (Marketplace)

1. Open **Settings > Marketplace**. The first time, tick **I understand the risks and agree** and press **Continue**.
2. Choose **Add from link** and paste `https://github.com/Radushka/home-checkup`. Home Assistant asks you to
   connect GitHub once, with a short code.
3. Install **Home Checkup**, restart Home Assistant if it asks, then press **Set up**.

### Home Assistant 2025.11 to 2026.10 (HACS)

1. Open **HACS**.
2. Open the menu (three dots, top right) and choose **Custom repositories**.
3. Paste `https://github.com/Radushka/home-checkup`, choose **Integration**, and press **Add**.
4. Find **Home Checkup** in HACS and press **Download**.
5. Restart Home Assistant.
6. Open **Settings > Devices and services > Add integration** and choose **Home Checkup**.

Home Checkup then appears in the sidebar. The first checkup runs about five minutes after Home Assistant starts.

Needs Home Assistant 2025.11 or newer.

## Works with Home Assistant's own Repairs

Home Checkup adds to Home Assistant; it does not replace or change any part of it.

1. Repairs belongs to Home Assistant. Home Checkup adds at most one note there, never one per problem.
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
4. From your YAML files and dashboards it picks out only helper names (like `input_boolean.guest_mode`).
   All other text is dropped at once and never kept.
5. Passwords, keys, tokens, sign-in addresses and email addresses in log messages are hidden
   before a message is kept or shown.
6. Log messages can name people and devices (for example "Anna's iPhone" or a serial number). They are shown
   only on your own Home Checkup page, to admins, and never leave your home.
7. Nothing is written to disk except your own "Keep" list, a 7-day error history (counts and the hidden-name
   message text only, in Home Assistant's own storage folder) and, when you use a safe fix, its backup
   (in `/config/home_checkup_backups`, kept in your home).

## What it gives you

1. A Home Checkup page in the sidebar, for admins. It shows the full list, with a link to each item and a "Keep" button for things that are fine as they are. "Check now" runs the checkup at once.
2. A sensor, "Things to look at" (0 means healthy).
3. One note in Settings > System > Repairs when something needs a look. It is always one note, never one per problem, and it goes away by itself when all is well. You can turn it off in the Home Checkup settings (Configure).
4. A Home Checkup card in [Dashboard Studio](https://lukaps.com/dashboardstudio/), if you use it.
