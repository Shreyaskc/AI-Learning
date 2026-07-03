#!/bin/bash
# One-time setup: makes the AI Fluency app reachable at http://aifluency.local
# (no port needed) from any device on the same WiFi.
#
# Run this yourself in Terminal: bash setup-hosting.sh
# It uses sudo — you'll be prompted for your Mac password once.

set -e

# Absolute paths — some sudo configs use a restricted PATH (secure_path) that
# excludes /usr/sbin, which causes "sudo: scutil: command not found" even
# though scutil resolves fine without sudo. Absolute paths sidestep that.
SCUTIL="/usr/sbin/scutil"
LAUNCHCTL="/bin/launchctl"
CP="/bin/cp"
CHOWN="/usr/sbin/chown"
CHMOD="/bin/chmod"
RM="/bin/rm"

PLIST_NAME="com.aifluency.server80"
PLIST_DEST="/Library/LaunchDaemons/${PLIST_NAME}.plist"
APP_DIR="/Users/shreyaskc/AI_Learning"

echo "== 1/3: Setting local hostname to 'aifluency' =="
CURRENT_NAME=$($SCUTIL --get LocalHostName 2>/dev/null || echo "")
if [ "$CURRENT_NAME" = "aifluency" ]; then
  echo "Already set — skipping."
else
  # Save the pre-change hostname once, so teardown-hosting.sh can restore it exactly.
  if [ ! -f "$APP_DIR/.hosting-original-hostname" ]; then
    echo "$CURRENT_NAME" > "$APP_DIR/.hosting-original-hostname"
  fi
  sudo $SCUTIL --set LocalHostName aifluency
  echo "Done. This Mac now answers to aifluency.local on the network."
fi

echo ""
echo "== 2/3: Installing the port-80 server (so no :PORT is needed in the URL) =="
if sudo $LAUNCHCTL print system/${PLIST_NAME} >/dev/null 2>&1; then
  echo "Already installed and running — skipping."
else
  TMP_PLIST=$(mktemp /tmp/${PLIST_NAME}.XXXX.plist)
  cat > "$TMP_PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>-m</string>
        <string>http.server</string>
        <string>80</string>
        <string>--bind</string>
        <string>0.0.0.0</string>
    </array>
    <key>WorkingDirectory</key>
    <string>${APP_DIR}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/aifluency-server80.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/aifluency-server80.err.log</string>
</dict>
</plist>
EOF
  sudo $CP "$TMP_PLIST" "$PLIST_DEST"
  sudo $CHOWN root:wheel "$PLIST_DEST"
  sudo $CHMOD 644 "$PLIST_DEST"
  sudo $LAUNCHCTL bootstrap system "$PLIST_DEST"
  $RM -f "$TMP_PLIST"
  echo "Done. Serving ${APP_DIR} on port 80 as root (see the note below on why)."
fi

echo ""
echo "== 3/3: Verifying =="
sleep 1
if curl -s -o /dev/null -w "%{http_code}" http://localhost/index.html | grep -q 200; then
  echo "✅ http://localhost is serving the app."
else
  echo "⚠️  Could not confirm via curl — check /tmp/aifluency-server80.err.log for details."
fi

echo ""
echo "All set. From any device on the same WiFi, open:"
echo "  http://aifluency.local"
echo "(Mac/iPhone/iPad resolve .local names automatically. If another device"
echo " doesn't, use this Mac's LAN IP instead: http://$(ipconfig getifaddr en0 2>/dev/null || echo '<your-lan-ip>')"
echo ""
echo "Note: the port-80 server runs as root — required by macOS for any port"
echo "below 1024, unavoidable for a plain static server. It only serves files"
echo "from ${APP_DIR} and never leaves your home network."
