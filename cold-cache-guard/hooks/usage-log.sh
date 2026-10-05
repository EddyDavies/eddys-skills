#!/bin/bash
# usage-log.sh: log plan usage for cold-cache-guard. Pipe the statusline's JSON into it.
#
# Claude Code hands the statusline your 5h and weekly plan % (rate_limits) but never
# hands hooks anything about limits. This appends {ts, sid, cost, h5, d7, h5_reset, d7_reset}
# to ~/.claude/state/usage-log.jsonl whenever one of them changes, so the hook can
# work out how many plan points a cache rebuild costs. Prints nothing.
input=$(cat)
usage=$(printf '%s' "$input" | jq -c 'select(.rate_limits.five_hour.used_percentage != null) | {ts: now | floor, sid: .session_id, cost: .cost.total_cost_usd, h5: .rate_limits.five_hour.used_percentage, d7: .rate_limits.seven_day.used_percentage, h5_reset: .rate_limits.five_hour.resets_at, d7_reset: .rate_limits.seven_day.resets_at}' 2>/dev/null)
[ -n "$usage" ] || exit 0
state="$HOME/.claude/state"
mkdir -p "$state"
key=$(printf '%s' "$usage" | jq -r '"\(.sid) \(.cost) \(.h5) \(.d7)"')
[ "$key" = "$(cat "$state/usage-last" 2>/dev/null)" ] && exit 0
printf '%s' "$key" > "$state/usage-last"
log="$state/usage-log.jsonl"
printf '%s\n' "$usage" >> "$log"
[ "$(wc -l < "$log")" -gt 20000 ] && tail -n 10000 "$log" > "$log.tmp" && mv "$log.tmp" "$log"
exit 0
