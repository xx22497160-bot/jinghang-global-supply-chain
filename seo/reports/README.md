# SEO Automation Reports

The automation is read-only. It does not change page copy, submit sitemaps, call an indexing API, publish content, send outreach, commit, merge, or deploy.

Architecture and safety boundaries are documented in `seo/automation-architecture.md`.

Report paths:

- Daily: `seo/reports/daily/YYYY-MM-DD.md`
- Weekly: `seo/reports/weekly/YYYY-WW.md`
- Monthly: `seo/reports/monthly/YYYY-MM.md`

Scheduled GitHub Actions upload reports as workflow artifacts. They do not commit generated reports back to the repository.

## Run Locally

```bash
python3 seo/scripts/seo_automation.py daily --local-only
python3 seo/scripts/seo_automation.py weekly
python3 seo/scripts/seo_automation.py monthly
```

Run the daily production monitor:

```bash
python3 seo/scripts/seo_automation.py daily --strict
```

The monitor continues checking all pages after an individual failure, writes its report, and only then returns a non-zero status when `--strict` is used and an error was found.

## Schedules

- Daily: 01:30 UTC, which is 09:30 China Standard Time (UTC+8).
- Weekly: Monday at 01:30 UTC, which is Monday 09:30 China Standard Time.
- Monthly: day 1 at 01:30 UTC, which is day 1 at 09:30 China Standard Time.

All three workflows also support manual `workflow_dispatch`.
