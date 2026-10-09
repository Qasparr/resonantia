#!/usr/bin/env python3
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# 93
"""egress-forward.py -- a local CONNECT forwarder for JVM tooling.

HYPOTHESIS: on this host, curl/Python speak the egress proxy fluently,
  but the JVM's HttpURLConnection dies in doTunneling0 with
  NoSuchElementException even when handed explicit proxyUser /
  proxyPassword. So the JVM never talks to the real proxy at all:
  it talks to THIS forwarder on 127.0.0.1 (no auth, pristine
  responses), and the forwarder does the authenticated CONNECT
  upstream the way curl does.
METHOD:    per connection: read the client's CONNECT request, open the
  upstream proxy, send CONNECT + Proxy-Authorization (Basic, credential
  read from the https_proxy env var at startup -- never logged, never
  written), require a 200, reply "200 Connection Established" to the
  client, then splice bytes both ways until EOF. Thread per
  connection; daemon threads; Ctrl-C stops.
DOCTRINE:  the credential lives ONLY in the process environment. It is
  never printed, never written to disk, never appears in an error
  message. Logs show hosts, never secrets.
"""

import base64
import os
import socket
import threading
from urllib.parse import urlparse

LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 8888
BUF = 65536


def _upstream():
    # Credential source: the environment, as curl uses it. Parsed once.
    raw = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY") or ""
    u = urlparse(raw)
    if not u.hostname or not u.port:
        raise SystemExit("egress-forward: https_proxy is missing or malformed")
    auth = ""
    if u.username:
        token = f"{u.username}:{u.password or ''}"
        auth = base64.b64encode(token.encode()).decode()
    return u.hostname, u.port, auth


UP_HOST, UP_PORT, UP_AUTH = _upstream()


def _read_headers(sock):
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
        if len(data) > 65536:
            break
    return data


def _splice(a, b):
    try:
        while True:
            chunk = a.recv(BUF)
            if not chunk:
                break
            b.sendall(chunk)
    except OSError:
        pass
    finally:
        for s in (a, b):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


def handle(client):
    try:
        req = _read_headers(client)
        if not req.startswith(b"CONNECT "):
            client.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            return
        # "CONNECT host:port HTTP/1.1"
        target = req.split(b" ", 2)[1].decode("ascii", "replace")
        host, _, port = target.partition(":")
        port = int(port or 443)
        print(f"forward: CONNECT {host}:{port}", flush=True)

        up = socket.create_connection((UP_HOST, UP_PORT), timeout=30)
        try:
            lines = [
                f"CONNECT {host}:{port} HTTP/1.1",
                f"Host: {host}:{port}",
            ]
            if UP_AUTH:
                lines.append(f"Proxy-Authorization: Basic {UP_AUTH}")
            lines += ["Proxy-Connection: Keep-Alive", "", ""]
            up.sendall("\r\n".join(lines).encode())
            resp = _read_headers(up)
            status = resp.split(b"\r\n", 1)[0] if resp else b""
            if b" 200" not in status.split(b"\r\n")[0]:
                print(f"forward: upstream refused {host}:{port}: "
                      f"{status[:60]!r}", flush=True)
                client.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
                return
            client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            t = threading.Thread(target=_splice, args=(up, client),
                                 daemon=True)
            t.start()
            _splice(client, up)
            t.join()
        finally:
            up.close()
    except Exception as exc:  # loud, but never the credential
        print(f"forward: error: {type(exc).__name__}", flush=True)
    finally:
        client.close()


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((LISTEN_HOST, LISTEN_PORT))
    srv.listen(64)
    print(f"egress-forward: listening on {LISTEN_HOST}:{LISTEN_PORT} "
          f"-> {UP_HOST}:{UP_PORT} (auth configured: {bool(UP_AUTH)})",
          flush=True)
    try:
        while True:
            client, _ = srv.accept()
            threading.Thread(target=handle, args=(client,),
                             daemon=True).start()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
