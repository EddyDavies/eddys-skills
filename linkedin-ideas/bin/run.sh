#!/bin/zsh
# Pull new LinkedIn post ideas from recent Claude sessions into the idea bank.
#
# usage: run.sh [--force] [--since YYYY-MM-DD]
#   --force   run even if the last run was under EVERY_DAYS ago
#   --since   digest sessions from this date (default: the last run's date)
#
# Env: LINKEDIN_IDEAS_BANK (idea bank folder), LINKEDIN_IDEAS_EVERY_DAYS (default 3),
#      LINKEDIN_IDEAS_MODEL (default opus).
set -euo pipefail

SKILL_DIR=${0:A:h:h}
BANK=${LINKEDIN_IDEAS_BANK:-$HOME/code/pally/content/linkedin-ideas}
STATE=$HOME/.claude/linkedin-ideas
EVERY_DAYS=${LINKEDIN_IDEAS_EVERY_DAYS:-3}
MODEL=${LINKEDIN_IDEAS_MODEL:-opus}
FORCE=0
SINCE=""
while (( $# )); do
  case $1 in
    --force) FORCE=1 ;;
    --since) SINCE=$2; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done

mkdir -p "$STATE" "$BANK/ideas" "$BANK/runs"
LAST_FILE=$STATE/last-run
TODAY=$(date +%Y-%m-%d)

if [[ -f $LAST_FILE ]]; then
  LAST=$(<"$LAST_FILE")
  AGE=$(( ( $(date +%s) - $(date -j -f %Y-%m-%d "$LAST" +%s) ) / 86400 ))
  if (( ! FORCE && AGE < EVERY_DAYS )); then
    echo "last run $LAST ($AGE days ago), next after $EVERY_DAYS days; skipping"
    exit 0
  fi
  SINCE=${SINCE:-$LAST}
fi
SINCE=${SINCE:-$(date -v-3d +%Y-%m-%d)}

RUN_DIR=$STATE/digests/$TODAY
mkdir -p "$RUN_DIR"
echo "digesting sessions since $SINCE"
CHUNKS=("${(@f)$(python3 "$SKILL_DIR/bin/digest.py" --since "$SINCE" --out "$RUN_DIR" --seen "$STATE/seen-sessions.txt" --record "$RUN_DIR/session-ids.txt")}")
CHUNKS=(${CHUNKS:#})

PROMPT=$(<"$SKILL_DIR/prompt.md")
FAILED=0
for chunk in $CHUNKS; do
  echo "== $chunk"
  if ! (cd "$BANK" && claude -p "$PROMPT $chunk" \
      --model "$MODEL" \
      --permission-mode acceptEdits \
      --allowedTools "Read,Write,Edit,Glob,Grep,LS" \
      --add-dir "$RUN_DIR" \
      --strict-mcp-config \
      --no-session-persistence); then
    echo "!! failed on $chunk" >&2
    FAILED=1
  fi
done

python3 "$SKILL_DIR/bin/index.py" "$BANK"
if (( FAILED )); then
  osascript -e 'display notification "Some digests failed; see ~/.claude/linkedin-ideas/run.log" with title "LinkedIn ideas"' || true
  exit 1
fi
cat "$RUN_DIR/session-ids.txt" >> "$STATE/seen-sessions.txt"
echo "$TODAY" > "$LAST_FILE"
COUNT=$(grep -c '^| \[' "$BANK/INDEX.md" || true)
osascript -e "display notification \"Idea bank updated ($COUNT ideas)\" with title \"LinkedIn ideas\"" || true
