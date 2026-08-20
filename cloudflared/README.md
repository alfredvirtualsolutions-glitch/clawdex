# Share Juan Cabezas OS on Cloudflare's edge (Option D — local-first)

Run the OS on your own machine and put a **live Cloudflare edge URL** in front of
it — WAF, caching, and optional login — with **no application code changes**. The
tunnel just points Cloudflare at your local `uvicorn`; the Daily Runner and the
database stay on your computer.

```
  your machine                         Cloudflare edge            the world
  ┌──────────────────┐   outbound     ┌──────────────┐          ┌─────────┐
  │ uvicorn :8787    │◀──tunnel──────▶│ *.trycloudfl │◀────────▶│ browser │
  │ (Agent OS API +  │  (cloudflared) │  or your      │  https   │         │
  │  WebSocket /ws)  │                │  domain)      │          └─────────┘
  └──────────────────┘                └──────────────┘
```

## 0. Install cloudflared (one time)

- **macOS:** `brew install cloudflared`
- **Windows / Linux:** grab the binary from
  <https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/>

## 1. Start the OS locally

```bash
make serve            # → http://127.0.0.1:8787  (WebSocket at /ws)
# first time, in another shell, load Juan's campaigns:
make seed
```

## 2a. Quick tunnel — instant, no account

Best for a fast demo / share link. Cloudflare hands you a random
`https://<something>.trycloudflare.com` URL that lives as long as the command runs.

```bash
make tunnel           # prints the live https URL — share it
```

That's the whole "one command = live edge URL" flow. Stop it with Ctrl-C.

## 2b. Named tunnel — your own domain, persistent URL

Best for ongoing use (e.g. `https://juan-os.yourdomain.com`). Requires a
Cloudflare account with the domain on Cloudflare. One-time setup:

```bash
make tunnel-login                                   # (1) authorize in your browser
make tunnel-create                                  # (2) creates the tunnel + ~/.cloudflared/<UUID>.json
cp cloudflared/config.example.yml cloudflared/config.yml
#   edit config.yml → set tunnel UUID, credentials-file path, and hostname
make tunnel-route HOSTNAME=juan-os.yourdomain.com   # (3) point DNS at the tunnel
```

Then, any time you want it live:

```bash
make serve            # terminal 1
make tunnel-named     # terminal 2 → serves at your hostname
```

## 3. (Recommended) Lock the internal OS behind a login

The dashboard, prospects, and approvals are internal — put **Cloudflare Access**
in front so only you/your advisor can reach them, while public pages
(`/qualify`, `/resources`, `/book`) stay open:

1. Cloudflare dashboard → **Zero Trust → Access → Applications → Add application**
   (self-hosted).
2. App domain: your tunnel hostname; **Path:** protect `/api`, `/dashboard`,
   `/approvals` (leave `/qualify` public, or add it as a separate bypass policy).
3. Policy: allow your email (`alfred.virtualsolutions@gmail.com`) — one-time email
   PIN or Google login. No code changes required.

## Notes & safety

- **WebSocket** (`/ws`, the live event stream) is proxied automatically — no extra
  config.
- **Secrets never get committed.** `cloudflared/config.yml`, `cloudflared/*.json`,
  and `cert.pem` are gitignored. Only `config.example.yml` (placeholders) is tracked.
- The server binds to `127.0.0.1` by default; only the tunnel reaches it, so the
  API isn't exposed on your LAN.
- Change the local port with `make serve PORT=9000 tunnel PORT=9000` (keep them in
  sync), or edit the `service:` line in `config.yml` for named tunnels.
