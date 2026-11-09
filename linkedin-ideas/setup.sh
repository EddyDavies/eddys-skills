#!/bin/zsh
# Install the linkedin-ideas launchd job: checks daily at 10:00, runs when 3+ days since the last run.
set -euo pipefail
SKILL_DIR=${0:A:h}
LABEL=com.eddydavies.linkedin-ideas
PLIST=$HOME/Library/LaunchAgents/$LABEL.plist
mkdir -p "$HOME/.claude/linkedin-ideas"

cat > "$PLIST.tmp" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>/bin/zsh</string><string>$SKILL_DIR/bin/run.sh</string></array>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>LINKEDIN_IDEAS_EVERY_DAYS</key><string>3</string>
  </dict>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>$HOME/.claude/linkedin-ideas/run.log</string>
  <key>StandardErrorPath</key><string>$HOME/.claude/linkedin-ideas/run.log</string>
</dict></plist>
EOF
mv "$PLIST.tmp" "$PLIST"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
[[ -L $HOME/.claude/skills/linkedin-ideas ]] || ln -s "$SKILL_DIR" "$HOME/.claude/skills/linkedin-ideas"
echo "installed $LABEL"
