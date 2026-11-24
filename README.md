# Order in Council Diary

Read the cabinet decisions hiding in plain sight. Search orders, appointments, departments and enabling statutes, then follow what changed.

Open https://coolcode.ca/oicdiary/

<!-- coolcode:guide -->
Search a department, statute or subject and open the original order. The weekly diary identifies newly observed and changed entries. Approval date is separate from the date the order first appeared in our archive.
<!-- /coolcode:guide -->

## Sources and interpretation

The official searchable database covers 1990 onward. This initial index collects orders approved in the current calendar year through collection day. Its coverage is explicit; the wider official archive remains linked.

Extraction uses the database’s ordinary public search form and paginated results with a session cookie. It does not use an undocumented private endpoint or bypass access controls.

The weekly snapshot diary and RSS feed show additions, changed entries and absences from the selected source results. A newly observed order may have an earlier approval date. First capture establishes a baseline.

Some orders are not published because of statutory restrictions. This index reflects the public source and cannot establish the full set of cabinet decisions.

The public search can omit its Next link before the final numbered pages. Collection follows the remaining numbered links and verifies distinct order IDs within the requested approval-date ranges.

## Collection and archive

Schedule: **Weekly** (`53 8 * * 1`, UTC). GitHub schedules are best effort. Scheduled and manual runs collect, validate, commit dated snapshots and deploy. A first code push also collects if no saved dataset exists. Other code pushes rebuild the saved dataset offline.

`data/current.json` contains the latest normalized source records and metadata. `archive/YYYY-MM/*.json.gz` retains distinct captured versions; `data/history.json` lists them. Identical data checks update the check time without manufacturing a change. An initial capture is labelled baseline. Archive data is tracked in Git and does not expire with Actions artifacts. The site has snapshot selection, filtering, source detail, CSV export and an RSS change feed.

The default build needs no network. Failed source validation does not replace the published dataset. Optional `HEALTHCHECKS_PING_URL` sends start/success/failure pings for collection runs; no accuracy email is implied.

```sh
python3 -m pip install -r requirements.txt
python3 scripts/collect.py
node --test tests/*.test.mjs
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

## Privacy

Search and filters are local to the browser; no upstream request is made by filtering. Public data collection runs in GitHub Actions. The shared CoolCode counter records aggregate page opens, without searches or filter values. The explorer and collector run without Cloudflare changes. To enable shared visit counts and private issue reports, add `oicdiary` to the existing `coolcode-visitor-api` Worker’s `toolList` and deploy it, if not already registered. See the [batch setup notes](https://github.com/jsdyer/jsdyer.github.io/blob/main/docs/tier1-tools.md).

## Software and attribution

Application code is MIT licensed; upstream data retains its original licence and attribution. Follow the source links for original records and terms.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

This is an interim mitigation, not a scheduling guarantee: GitHub does not document active-workflow renewal as a permanent exemption, and scheduled runs can be delayed or dropped. A scheduler on our own Linux server is the planned independent trigger. The guard does not collect data, create dummy commits, or change source/check timestamps; successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->
