#!/usr/bin/env bash
# Assemble the rote play package in play/.
#
# It lives at the repo root because a play package may contain only main.ts,
# deps.toml and resources/ | lib/ | vendor/ -- anything else fails lint with
# FLOW_UNSUPPORTED_COMPANION.
#
# The modules are copied rather than committed twice, so the CLI at the repo
# root stays the single source of truth and the package cannot drift from it.
# Run this before lint or publish.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
here="$root/play"

modules=(factcheck claims collect extract issues precedence render script sources yamlish)
mkdir -p "$here/resources"
for m in "${modules[@]}"; do
  cp "$root/$m.py" "$here/resources/$m.py"
done

# Anything the classifier does not recognise fails `rote play lint` with
# FLOW_PACKAGE_CAPTURE_FAILED. Running the *published* play drops exactly that
# here when the install path collides with this directory, so clear it.
rm -rf "$here/factcheck" "$here/.factcheck.install.lock"

echo "package assembled: ${#modules[@]} modules in $here/resources"
