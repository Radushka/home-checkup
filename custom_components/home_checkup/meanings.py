"""What a log error means, in plain words: a short code for the common causes. The page shows the words.

Only the message text is matched, in memory. Nothing leaves the home. Most specific causes come first.
"""

from __future__ import annotations

import re

MEANINGS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (code, re.compile(pattern, re.I))
    for code, pattern in (
        # From the browser: a dashboard card, not a device.
        ("card", r"uncaught error from|customelementregistry|/local/community/|/hacsfiles/"),
        ("signin", r"\b(401|403)\b|unauthori[sz]ed|forbidden|invalid (auth|credentials|token|password)|"
         r"auth(entication)? (failed|error)|token (has )?expired|re-?auth|login failed"),
        ("slowdown", r"\b429\b|rate.?limit|too many requests|quota"),
        ("certificate", r"\bssl\b|certificate|\btls\b handshake"),
        ("already", r"already[ _](running|started|in progress|active|exists?|configured|connected|open)"),
        ("notrunning", r"_not_running\b|nothing to stop"),
        ("storage", r"no space left|disk (is )?full|errno 28"),
        ("memory", r"memoryerror|out of memory|cannot allocate memory"),
        ("permission", r"permission denied|permissionerror|errno 13\b"),
        ("timeout", r"timed? ?out|timeouterror|deadline exceeded|no response|did not respond"),
        ("dns", r"name or service not known|name resolution|getaddrinfo|could not resolve|nodename nor servname|\bdns\b"),
        ("unreachable", r"connection (refused|reset|error|aborted)|cannot connect|can't connect|failed to connect|"
         r"unable to connect|clientconnectorerror|no route to host|host is unreachable|"
         r"network is unreachable|connect call failed"),
        ("dropped", r"disconnected|connection (was )?(lost|closed|dropped)|broken pipe|unexpectedly closed"),
        ("offline", r"\b(device|station|camera) (is )?offline\b|is not (available|online)|went offline"),
        ("server", r"\b(status|http|code|error)[ :=]*5\d\d\b|bad gateway|service unavailable|internal server error"),
        ("noaction", r"(service|action) [\w.]+ (was )?(not found|does not exist)|unknown (service|action)|servicenotfound"),
        ("missing", r"referenced entities .* missing|unable to find (referenced )?entit|entity .* (not found|does not exist)"),
        # Asked the other side for one thing by its id, and that thing is gone there (cleaned up, updated, deleted).
        ("image", r"/images/sha256|no such image|image .* (not found|does not exist)"),
        ("removed", r"resource not found|no such (container|volume|file|object|device)|"
         r"(has been|was) (deleted|removed)|no longer exists"),
        ("notfound", r"\b404\b|not found"),
        ("blocking", r"detected blocking call|blocking call to"),
        ("deprecated", r"deprecat"),
        ("template", r"template (variable )?(error|warning)|undefinederror|template.*render|"
         r"'dict object' has no attribute|\bjinja"),
        ("slowstart", r"setup of .* is taking|took longer than expected|is taking over \d+ seconds"),
        ("unsupported", r"not supported|unsupported|does not support|not implemented|notimplementederror"),
        ("baddata", r"jsondecodeerror|invalid json|unexpected (response|token|end of)|failed to (parse|decode)|"
         r"could not parse|malformed|expecting value"),
        ("badvalue", r"invalid (value|option|argument|entity id|config)|out of range|could not convert|invalid literal|"
         r"is not a valid|valueerror|multipleinvalid"),
        ("database", r"\brecorder\b|database|sqlite|mariadb|postgres"),
        # Last: a plain Python error with no better reading is a fault in the code that logged it.
        ("bug", r"\b(type|attribute|key|index|assertion|zerodivision|runtime|unboundlocal|name)error\b|nonetype|"
         r"unexpected exception|never retrieved"),
    )
)


_SSL_NOISE = re.compile(r"\bssl:\S+", re.I)


def meaning_of(text: str) -> str:
    """The code of the first cause that fits, or "" when none does."""
    # aiohttp writes "ssl:default" into every failed connection. It says nothing about certificates.
    text = _SSL_NOISE.sub(" ", text or "")
    for code, pattern in MEANINGS:
        if pattern.search(text):
            return code
    return ""
