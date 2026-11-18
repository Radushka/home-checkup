"""What a log error means, in plain words: a short code for the common causes. The page shows the words.

Only the message text is matched, in memory. Nothing leaves the home. Most specific causes come first.
"""

from __future__ import annotations

import re

MEANINGS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (code, re.compile(pattern, re.I))
    for code, pattern in (
        ("signin", r"\b(401|403)\b|unauthori[sz]ed|forbidden|invalid (auth|credentials|token|password)|"
         r"auth(entication)? (failed|error)|token (has )?expired|re-?auth|login failed"),
        ("slowdown", r"\b429\b|rate.?limit|too many requests|quota"),
        ("certificate", r"\bssl\b|certificate|\btls\b handshake"),
        ("timeout", r"timed? ?out|timeouterror|deadline exceeded|no response|did not respond"),
        ("unreachable", r"connection (refused|reset|error|aborted)|cannot connect|can't connect|failed to connect|"
         r"unable to connect|clientconnectorerror|no route to host|host is unreachable|name or service not known|"
         r"network is unreachable|connect call failed"),
        ("offline", r"\b(device|station|camera) (is )?offline\b|is not (available|online)|went offline"),
        ("notfound", r"\b404\b|not found"),
        ("blocking", r"detected blocking call|blocking call to"),
        ("deprecated", r"deprecat"),
        ("template", r"template (variable )?(error|warning)|undefinederror|has no attribute|template.*render"),
        ("missing", r"referenced entities .* missing|unable to find (referenced )?entit|entity .* (not found|does not exist)"),
        ("slowstart", r"setup of .* is taking|took longer than expected|is taking over \d+ seconds"),
        ("database", r"\brecorder\b|database|sqlite|mariadb|postgres"),
    )
)


def meaning_of(text: str) -> str:
    """The code of the first cause that fits, or "" when none does."""
    for code, pattern in MEANINGS:
        if pattern.search(text or ""):
            return code
    return ""
