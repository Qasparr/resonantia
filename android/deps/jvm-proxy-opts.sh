#!/usr/bin/env bash
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# 93
#
# jvm-proxy-opts.sh -- print JVM -D proxy flags derived from the
# environment's https_proxy (which carries the egress auth).
#
# Usage:  GRADLE_OPTS="$(./jvm-proxy-opts.sh)" gradle ...
# or:     eval "$(./jvm-proxy-opts.sh --export)"
#
# DOCTRINE: the credential comes from the environment at runtime and is
# never written to disk by this script. It WILL appear in the JVM's own
# command line (unavoidable -- that is how Java takes proxy auth). Do
# not echo this script's output into logs.
set -euo pipefail
MODE="${1:-print}"
python3 - "$MODE" <<'PYEOF'
import os, sys
from urllib.parse import urlparse
mode = sys.argv[1]
raw = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY") or ""
u = urlparse(raw)
if not u.hostname or not u.port:
    sys.exit("jvm-proxy-opts: https_proxy missing or malformed")
opts = [
    f"-Dhttps.proxyHost={u.hostname}", f"-Dhttps.proxyPort={u.port}",
    f"-Dhttp.proxyHost={u.hostname}", f"-Dhttp.proxyPort={u.port}",
]
if u.username:
    opts += [f"-Dhttps.proxyUser={u.username}",
             f"-Dhttps.proxyPassword={u.password or ''}",
             f"-Dhttp.proxyUser={u.username}",
             f"-Dhttp.proxyPassword={u.password or ''}"]
# Direct egress is dead on this host; the JVM must NOT bypass the proxy
# for the hosts it needs (keep 127.0.0.1 bypassed for the loopback UI).
opts += ["-Dhttp.nonProxyHosts=localhost|127.0.0.1"]
if mode == "--export":
    print("GRADLE_OPTS='" + " ".join(opts).replace("'", "'\\''") + "'")
    print("export GRADLE_OPTS")
else:
    print(" ".join(opts))
PYEOF
