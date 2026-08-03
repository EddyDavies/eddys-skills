#!/bin/bash
# notify-web-ready.sh <url> [label]
# Replaces "open <url>": sends a desktop notification saying the page is
# ready and copies the URL to the clipboard, instead of stealing focus by
# opening a browser.
url="$1"
label="${2:-Web page ready}"

if [ -n "$url" ]; then
  printf '%s' "$url" | pbcopy 2>/dev/null
  body="$url (URL copied to clipboard)"
else
  body="URL on request"
fi

# Ghostty OSC 777 notification - only possible when we have a tty
# (interactive use); Claude's Bash tool has no controlling terminal.
if { true 2>/dev/null >/dev/tty; } 2>/dev/null; then
  printf '\033]777;notify;%s;%s\033\\' "Claude: $label" "$body" >/dev/tty
  echo "Notified via Ghostty: $label - $body"
  exit 0
fi

osascript -e "display notification \"$body\" with title \"Claude: $label\"" >/dev/null 2>&1 \
  && echo "Notified: $label - $body" \
  || { echo "Notification failed" >&2; exit 1; }
