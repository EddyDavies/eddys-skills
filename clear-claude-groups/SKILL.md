---
name: clear-claude-groups
description: Use when asked to clear, delete or clean up the saved Chrome tab groups named "Claude" that Claude in Chrome leaves behind (they pile up under ⋮ > Tab groups in every profile), or when the daily launchd job runs it. Deletes them through Chrome's own menus with a screenshot before every click; never touches other groups or groups that are open right now.
---

# clear-claude-groups

Claude in Chrome puts its tabs in a group named "Claude". Chrome saves every group, and closing the tabs keeps the saved group, so dozens pile up in every profile. No extension API, AppleScript, policy or file edit removes a saved group (sync restores them), so this drives Chrome's own "Delete group" menu with the mouse.

## Schedule

`setup.sh` installs `~/Library/LaunchAgents/com.eddydavies.clear-claude-groups.plist`, which calls `bin/run` every 2 minutes. `bin/run` exits at once unless it is after 05:00, today is not done, fewer than 3 tries today, Chrome is running, the screen is **unlocked** and the user has been **idle 4 to 9 minutes**. The Mac locks the moment the display sleeps (10 minutes), and clicks can't reach Chrome behind the lock screen, so this idle window is the only time it can run unattended. A day with no such window is skipped; the groups wait.

Logs: `~/.claude/clear-claude-groups/run.log`, the last Claude output in `last-output.txt`. Run by hand with `bin/run --now`. Uninstall with `setup.sh uninstall`.

## Procedure (for the Claude doing the run)

Helpers live in this skill's `bin/`:

- `bin/shot`: screenshots the main display at 1 pixel per logical point and prints the path. Read the PNG to see it. Coordinates in the image are the coordinates `act` takes.
- `bin/act click X Y`, `bin/act right X Y`, `bin/act move X Y`: guarded mouse actions. If one prints `USER_ACTIVE`, someone touched the mouse: **stop all mouse and keyboard actions at once**, close the windows you opened (step 5, AppleScript only) and finish with `RESULT status=user_active`.
- `bin/live-groups`: JSON list of tabs currently inside open groups (the scheduled prompt already includes it).

Rules:

- Take a fresh `shot` before **every** click and read it. Menus shift (banners, submenus opening left or right), so never reuse coordinates from an earlier shot or from memory.
- Only delete saved groups whose name is "Claude" (case insensitive, may carry a number or suffix such as "Claude 2"). Never touch any other group.
- Never delete a group that is open: hover the group in the Tab groups menu; its submenu lists its tabs. If any listed tab matches a tab in the live-groups list for this profile, skip that group and count it as skipped.
- Use only the clicks below. No typing into pages, no other menus, no settings.

Steps:

1. Record the windows that exist: `osascript -e 'tell application "Google Chrome" to get id of every window'`.
2. List profiles: `osascript -e 'tell application "System Events" to get name of menu items of menu 1 of menu bar item "Profiles" of menu bar 1 of process "Google Chrome"'`. Ignore `missing value`, `Edit…` and `Add Profile…`.
3. For each profile:
   1. `osascript -e 'tell application "Google Chrome" to activate' -e 'tell application "System Events" to tell process "Google Chrome" to click menu item "<profile>" of menu 1 of menu bar item "Profiles" of menu bar 1'`, then `osascript -e 'tell application "Google Chrome" to make new window' -e 'tell application "Google Chrome" to activate'` so a window of that profile sits on the current desktop. `shot` and check the profile avatar or name in the toolbar matches.
   2. Click the ⋮ menu (far right of the toolbar). `shot`. Hover "Tab groups" with `act move`. `shot`: the submenu lists saved groups.
   3. If no deletable Claude group is listed, press Escape twice (`osascript -e 'tell application "System Events" to key code 53'`) and go to the next profile.
   4. Otherwise hover the first deletable Claude group. `shot`. Check its tabs against live-groups. Click "Delete group" in its submenu. `shot`. Click "Delete" in the confirmation dialog. `shot` to confirm it closed. Repeat from 3.2.
4. If a step's screen doesn't match what you expect twice in a row, press Escape twice, skip that profile and note it.
5. Close every Chrome window whose id was not in the step 1 list: `osascript -e 'tell application "Google Chrome" to close (every window whose id is <id>)'`.
6. Finish with exactly one line on its own:
   `RESULT status=ok deleted=<n> skipped=<n> profiles=<n>` (use `status=error reason=<short>` if a profile could not be done, `status=user_active` if `act` said so).
