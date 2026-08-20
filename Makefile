# Juan Cabezas OS — local run + Cloudflare edge share.
#
#   make serve         # run the Agent OS API locally (http://127.0.0.1:8787)
#   make tunnel        # expose it on a live *.trycloudflare.com URL (no account)
#   make tunnel-named  # expose it on your own domain (named tunnel; see cloudflared/README.md)
#   make seed          # load Juan Cabezas' FL/TX/CA campaigns
#   make daily         # run the Daily Runner once
#
# `serve` and a tunnel are two separate processes: start `make serve` in one
# terminal, `make tunnel` in another. No app code changes — the tunnel just
# points Cloudflare's edge at your local uvicorn (WebSocket included).

HOST ?= 127.0.0.1
PORT ?= 8787
TUNNEL_NAME ?= juan-os
PY ?= python

.DEFAULT_GOAL := help

.PHONY: help serve seed daily tunnel tunnel-named tunnel-login tunnel-create tunnel-route check-cloudflared

help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

serve: ## Run the Agent OS API locally (uvicorn)
	$(PY) -m juan_os.agent_os serve --host $(HOST) --port $(PORT)

seed: ## Load Juan Cabezas' FL/TX/CA campaigns into the local DB
	$(PY) -m juan_os.agent_os seed-juan

daily: ## Run the Daily Runner once (add ARGS="--loop --interval 14400" to stay resident)
	$(PY) -m juan_os.agent_os daily $(ARGS)

check-cloudflared:
	@command -v cloudflared >/dev/null 2>&1 || { \
		echo "cloudflared not found. Install it: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"; \
		echo "  macOS:  brew install cloudflared"; \
		echo "  Linux:  see the download page above (or your package manager)"; \
		exit 1; }

tunnel: check-cloudflared ## Quick tunnel — instant public https://*.trycloudflare.com URL (no account)
	@echo "Exposing http://$(HOST):$(PORT) via Cloudflare quick tunnel..."
	@echo "Look for the printed https://<random>.trycloudflare.com URL below."
	cloudflared tunnel --url http://$(HOST):$(PORT)

# --- Named tunnel (your own domain, persistent URL) ----------------------- #
# One-time setup, then `make tunnel-named` runs it. Details in cloudflared/README.md.
tunnel-login: check-cloudflared ## (1) Authorize cloudflared with your Cloudflare account
	cloudflared tunnel login

tunnel-create: check-cloudflared ## (2) Create the named tunnel + credentials
	cloudflared tunnel create $(TUNNEL_NAME)

tunnel-route: check-cloudflared ## (3) Map a hostname to it: make tunnel-route HOSTNAME=juan-os.example.com
	@test -n "$(HOSTNAME)" || { echo "Usage: make tunnel-route HOSTNAME=juan-os.example.com"; exit 1; }
	cloudflared tunnel route dns $(TUNNEL_NAME) $(HOSTNAME)

tunnel-named: check-cloudflared ## (4) Run the named tunnel using cloudflared/config.yml
	cloudflared tunnel --config cloudflared/config.yml run $(TUNNEL_NAME)
