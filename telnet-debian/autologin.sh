#!/bin/bash
# Custom telnet login program.
# Accepts ANY username and ANY password.
# - If the user does not exist yet, it is created on the fly.
# - The password is prompted for (to look real) but never checked.
# After "authenticating", it hands off to `login -f` so you get a
# proper PAM session, tty setup, environment and login shell.

user=""

# telnetd invokes us roughly like:  autologin -h <remotehost> -p [USER]
# Parse args: drop flags (and -h's value), take the first bare word as the user.
while [ $# -gt 0 ]; do
  case "$1" in
    -h) shift 2 ;;          # -h <host>
    -p|--) shift ;;         # standalone flags
    -*) shift ;;            # any other flag
    *)  user="$1"; shift ;; # first non-flag arg = username
  esac
done

if [ -z "$user" ]; then
  printf 'login: '
  read -r user
fi

# Prompt for a password just so it feels like a normal login, then ignore it.
printf 'Password: '
read -rs _pass
echo

# Fall back to a default if somehow still empty.
[ -z "$user" ] && user="guest"

# Create the account on demand if it doesn't already exist.
if ! id "$user" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "$user" >/dev/null 2>&1
fi

# Hand off to the real login with -f (skip authentication) for a clean session.
exec /bin/login -f "$user"
