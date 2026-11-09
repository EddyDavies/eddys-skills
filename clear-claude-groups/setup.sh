#!/bin/zsh
# Install (or `setup.sh uninstall`) the clear-claude-groups skill link and launchd job.
set -eu
DIR=${0:A:h}
LABEL=com.eddydavies.clear-claude-groups
PLIST=$HOME/Library/LaunchAgents/$LABEL.plist

if [[ ${1:-} == probe ]]; then
  S=$HOME/.claude/clear-claude-groups
  rm -f $S/probe.out; touch $S/probe
  open -g -j -a $HOME/Applications/ClearClaudeGroups.app
  for i in {1..15}; do [[ -s $S/probe.out ]] && break; sleep 1; done
  cat $S/probe.out 2>/dev/null || print "no answer yet (permission prompt open?)"
  exit 0
fi

if [[ ${1:-} == uninstall ]]; then
  launchctl bootout gui/$(id -u)/$LABEL 2>/dev/null || true
  rm -f $PLIST
  print "Removed $LABEL"
  exit 0
fi

chmod +x $DIR/bin/*
[[ -L $HOME/.claude/skills/clear-claude-groups ]] || ln -s $DIR $HOME/.claude/skills/clear-claude-groups
mkdir -p $HOME/.claude/clear-claude-groups

# Helper app that holds the Screen Recording and Accessibility grants (launchd jobs
# can't). Built once: rebuilding changes its signature and drops the grants, so only
# `setup.sh rebuild-app` replaces it.
APP=$HOME/Applications/ClearClaudeGroups.app
if [[ ! -d $APP || ${1:-} == rebuild-app ]]; then
  mkdir -p $HOME/Applications
  rm -rf $APP
  osacompile -o $APP -e "do shell script \"'$DIR/bin/run' --inapp >/dev/null 2>&1\""
  plutil -replace LSUIElement -bool true $APP/Contents/Info.plist
  plutil -replace CFBundleIdentifier -string com.eddydavies.clear-claude-groups $APP/Contents/Info.plist
  codesign --force --deep -s - $APP
  print "Built $APP: grant it Screen Recording and Accessibility in System Settings > Privacy & Security"
fi

cat >| $PLIST <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>$DIR/bin/run</string></array>
  <key>EnvironmentVariables</key><dict><key>PATH</key><string>$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string></dict>
  <key>StartInterval</key><integer>120</integer>
  <key>StandardErrorPath</key><string>$HOME/.claude/clear-claude-groups/launchd.err</string>
</dict></plist>
EOF

launchctl bootout gui/$(id -u)/$LABEL 2>/dev/null || true
launchctl bootstrap gui/$(id -u) $PLIST
print "Installed $LABEL (checks every 2 minutes)"
