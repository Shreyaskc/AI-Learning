#!/bin/bash
# Undoes everything set up for LAN access to the AI Fluency app:
#   - the port-80 server (com.aifluency.server80)
#   - the port-8642 background server (com.aifluency.server)
#   - the local hostname change (aifluency -> whatever it was before)
#
# Run this yourself in Terminal: bash teardown-hosting.sh
# It uses sudo — you'll be prompted for your Mac password once.

set -e

# Absolute paths — some sudo configs use a restricted PATH (secure_path) that
# excludes /usr/sbin, which causes "sudo: scutil: command not found" even
# though scutil resolves fine without sudo. Absolute paths sidestep that.
SCUTIL="/usr/sbin/scutil"
LAUNCHCTL="/bin/launchctl"
RM="/bin/rm"

APP_DIR="/Users/shreyaskc/AI_Learning"
DAEMON80="com.aifluency.server80"
DAEMON80_PLIST="/Library/LaunchDaemons/${DAEMON80}.plist"
AGENT8642="com.aifluency.server"
AGENT8642_PLIST="$HOME/Library/LaunchAgents/${AGENT8642}.plist"

echo "== 1/3: Removing the port-80 server =="
if sudo $LAUNCHCTL print system/${DAEMON80} >/dev/null 2>&1; then
  sudo $LAUNCHCTL bootout system/${DAEMON80}
  echo "Stopped."
else
  echo "Not running — skipping stop."
fi
if [ -f "$DAEMON80_PLIST" ]; then
  sudo $RM "$DAEMON80_PLIST"
  echo "Removed $DAEMON80_PLIST."
else
  echo "No plist found — skipping."
fi

echo ""
echo "== 2/3: Removing the port-8642 background server =="
UID_NUM=$(id -u)
if $LAUNCHCTL print gui/${UID_NUM}/${AGENT8642} >/dev/null 2>&1; then
  $LAUNCHCTL bootout gui/${UID_NUM}/${AGENT8642}
  echo "Stopped."
else
  echo "Not running — skipping stop."
fi
if [ -f "$AGENT8642_PLIST" ]; then
  $RM "$AGENT8642_PLIST"
  echo "Removed $AGENT8642_PLIST."
else
  echo "No plist found — skipping."
fi

echo ""
echo "== 3/3: Restoring the original local hostname =="
CURRENT_NAME=$($SCUTIL --get LocalHostName 2>/dev/null || echo "")
if [ "$CURRENT_NAME" != "aifluency" ]; then
  echo "Hostname is already '$CURRENT_NAME' (not 'aifluency') — skipping."
else
  if [ -f "$APP_DIR/.hosting-original-hostname" ]; then
    ORIGINAL=$(cat "$APP_DIR/.hosting-original-hostname")
  else
    ORIGINAL="Shreyass-MacBook-Pro"
    echo "(No saved record of the original name — falling back to '$ORIGINAL',"
    echo " which is what this Mac was using before any of this was set up.)"
  fi
  sudo $SCUTIL --set LocalHostName "$ORIGINAL"
  $RM -f "$APP_DIR/.hosting-original-hostname"
  echo "Restored local hostname to '$ORIGINAL'."
fi

echo ""
echo "✅ Teardown complete. The app's files in $APP_DIR are untouched —"
echo "   only the background services and hostname were removed."
echo "   You can still run the app locally any time with:"
echo "     cd $APP_DIR && python3 -m http.server 8642"
