# Unattended daily schedule — Juan Cabezas

Run the workflow 3×/day per state, plus a nightly report. All local; no cloud needed.
Assumes the Agent OS API is running (`python -m juan_os.agent_os`, default port 8787).

## macOS / Linux (cron)
Edit with `crontab -e`. Times are local. `run_cycle` with no `campaign_id` picks the
next active campaign; pass a specific state campaign id to pin it.

```cron
# Juan Cabezas — 3 daily cycles (08:00, 12:30, 17:00) + nightly export at 18:00
0  8  * * 1-5  curl -s -X POST localhost:8787/api/orchestrator/run-cycle -H 'content-type: application/json' -d '{}' >/dev/null
30 12 * * 1-5  curl -s -X POST localhost:8787/api/orchestrator/run-cycle -H 'content-type: application/json' -d '{}' >/dev/null
0  17 * * 1-5  curl -s -X POST localhost:8787/api/orchestrator/run-cycle -H 'content-type: application/json' -d '{}' >/dev/null
0  18 * * 1-5  cd /path/to/clawdex && python -m juan_os export --out juan_daily_report.html >/dev/null
```

To pin a specific state campaign, first get its id:
```bash
curl -s localhost:8787/api/campaigns | python3 -c "import sys,json;[print(c['target_state'],c['id']) for c in json.load(sys.stdin)['campaigns'] if c['advisor_name']=='Juan Cabezas']"
# then: -d '{"campaign_id":"camp_xxxxxxxx"}'
```

## Windows (Task Scheduler)
Create three Basic Tasks (Daily, weekdays) running PowerShell:
```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8787/api/orchestrator/run-cycle -ContentType 'application/json' -Body '{}'
```
Trigger times: 8:00 AM, 12:30 PM, 5:00 PM. Add a 4th at 6:00 PM running the export command above.

## systemd timer (Linux, alternative to cron)
`/etc/systemd/system/juan-cycle.service`:
```ini
[Service]
Type=oneshot
ExecStart=/usr/bin/curl -s -X POST localhost:8787/api/orchestrator/run-cycle -H 'content-type: application/json' -d '{}'
```
`/etc/systemd/system/juan-cycle.timer`:
```ini
[Timer]
OnCalendar=Mon-Fri 08:00,12:30,17:00
Persistent=true
[Install]
WantedBy=timers.target
```
`sudo systemctl enable --now juan-cycle.timer`

## Notes
- Keep the API process running (a `tmux`/`screen` session, a `systemd` service, or
  `pm2 start "python -m juan_os.agent_os"`).
- Hot leads still require **human approval** in the Approvals surface before any send —
  the schedule only drives discovery/scoring, never unattended outreach to Hot leads.
