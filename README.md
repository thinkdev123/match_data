
# match_data
A Python wrapper for ESPN's undocumented sports API that turns raw scoreboard JSON into clean, usable match data. Currently supports soccer/football with filtering, caching, and object-based access.
=======
# matchdata

**Version:** alpha 1.0.0

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/version-alpha%201.0.0-orange.svg?style=for-the-badge)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)](LICENSE)

---

## Disclaimer

This project accesses ESPN's undocumented public API endpoints — the same endpoints that serve data to ESPN's website and mobile applications. This project is **not affiliated with, endorsed by, or connected to ESPN or The Walt Disney Company** in any way. No authentication mechanisms are bypassed and no proprietary systems are accessed. Use responsibly and in accordance with ESPN's terms of service.

---

## Credits

This project is built upon the research and documentation of ESPN's public API endpoints by **Joseph Wilson (pseudo-r)**.

- GitHub: [pseudo-r](https://github.com/pseudo-r)
- Repository: [Public-ESPN-API](https://github.com/pseudo-r/Public-ESPN-API)

---

## Table of Contents

- [Overview](#overview)
- [Important Notes](#important-notes)
- [Current State](#current-state)
- [Dependencies](#dependencies)
- [Quick Start](#quick-start)
- [Available Data](#available-data)
- [Client Methods](#client-methods)
- [Match Object](#match-object)
- [Supported Leagues](#supported-leagues)
- [Caching](#caching)
- [Limitations](#limitations)
- [Reporting Bugs](#reporting-bugs)
- [License](#license)

---

## Overview

ESPN provides undocumented APIs that power their website and mobile applications. These endpoints return JSON data for scores, teams, players, statistics, and more across all major sports. However, the data is deeply nested, inconsistent across sports and leagues, and entirely undocumented.

`matchdata` uses the open endpoints documented by [pseudo-r](https://github.com/pseudo-r/Public-ESPN-API) and wraps them in a clean, object-oriented Python library. Instead of dealing with raw JSON and unpredictable schemas, developers get structured `Match` objects with consistent attributes and convenient properties — regardless of league or match state.

---

## Important Notes

- **Unofficial.** These APIs are not officially supported by ESPN and may change, break, or be removed without notice.
- **No Authentication Required.** The endpoints accessed by this library are publicly available and require no API key.
- **Rate Limiting.** ESPN does not publish official rate limits. Be respectful with request frequency. Excessive requests may result in temporary or permanent blocking.
- **Schema Inconsistency.** ESPN's API responses vary in structure depending on the sport, league, and match state. Fields that are not consistently available across all leagues have been intentionally excluded from this release.

---

## Current State

`matchdata` is in **early alpha**. The first supported sport is soccer/football, covering the ESPN `/scoreboard` endpoint.

| Feature | Status |
|---------|--------|
| Soccer / Football Client | ✅ Functional |
| Match Object with Properties | ✅ Functional |
| Time-based Caching | ✅ Functional |
| Date and Date Range Queries | ✅ Functional |
| Motorsport / F1 Client | 🔜 Planned |
| Error Handling / Custom Exceptions | 🔜 Planned |
| Additional Data Fields | 🟡 Partial |
| `/summary` Endpoint Support | 🔜 Planned |
| PyPI Distribution | 🔜 Planned |

The library currently extracts approximately 40% of the available data from the `/scoreboard` endpoint. Fields such as goal scorers, match statistics, broadcasts, odds, and headlines are available in the raw API response but have been excluded from this release due to inconsistent availability across leagues.

---
## Dependencies

| Package | Required | Purpose |
|---------|----------|---------|
| Python 3.7+ | ✅ | Minimum Python version |
| `requests` | ✅ | HTTP requests to ESPN API |
| `datetime` | ✅ | Timestamp handling and cache tracking (included in Python standard library) |

`datetime` is part of the Python standard library and does not require separate installation. The only external dependency is `requests`.

```bash
pip install requests
```
---
## Quick Start

`matchdata` is not yet published on PyPI. To use it, clone the repository directly.

```bash
git clone https://github.com/thinkdev123/matchdata.git
cd matchdata
pip install requests
```

### Basic Usage

```python
from main import SoccerClient

# Initialize client for FIFA World Cup
client = SoccerClient('fifa.world')

# Fetch all matches (defaults to today)
matches = client.get_info()

# Print each match
for match in matches:
    print(match)
```

### Filtering by Match State

```python
# Currently live matches
live = client.ongoing()

# Completed matches
done = client.finished()

# Scheduled matches
soon = client.upcoming()
```

### Querying by Date

```python
# Specific date (YYYYMMDD format)
matches = client.get_info(date="20260628")

# Date range
matches = client.get_info(date_range=("20260615", "20260620"))
```

### Accessing Match Data

```python
match = matches[0]

print(match.home_name)          # "Brazil"
print(match.away_name)          # "Argentina"
print(match.home_score)         # "2"
print(match.away_score)         # "1"
print(match.is_live)            # False
print(match.is_finished)        # True
print(match.venue)              # {"venue": "Maracanã", "city": "Rio de Janeiro", "country": "Brazil"}
print(match.score)              # {"home": "Brazil", "home_score": "2", "away_score": "1", "away": "Argentina"}
```

### Match IDs

```python
# All match IDs
ids = client.get_ids()
# {"BRA @ ARG": "401862897", "GER @ FRA": "401862898"}

# Specific match ID by short name
match_id = client.get_id("BRA @ ARG")
# "401862897"
```

---

## Available Data

Each `Match` object exposes the following attributes:

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `match_id` | `str` | ESPN event identifier | `"401862897"` |
| `date` | `str` | Match date in ISO 8601 format | `"2026-05-30T16:00Z"` |
| `short_name` | `str` | Abbreviated match name | `"ARS @ PSG"` |
| `state` | `str` | Match state | `"pre"` / `"in"` / `"post"` |
| `detail` | `str` | Status detail | `"FT"` / `"HT"` / `"65'"` |
| `home_name` | `str` | Home team full name | `"Paris Saint-Germain"` |
| `away_name` | `str` | Away team full name | `"Arsenal"` |
| `home_score` | `str` | Home team score | `"1"` |
| `away_score` | `str` | Away team score | `"1"` |
| `home_abbreviation` | `str` | Home team abbreviation | `"PSG"` |
| `away_abbreviation` | `str` | Away team abbreviation | `"ARS"` |
| `home_logo` | `str` | Home team logo URL | ESPN CDN URL |
| `away_logo` | `str` | Away team logo URL | ESPN CDN URL |
| `home_form` | `str` | Home team last 5 results | `"WLWWD"` |
| `away_form` | `str` | Away team last 5 results | `"LWWWW"` |
| `venue_name` | `str` | Venue name | `"Puskás Aréna"` |
| `venue_city` | `str` | Venue city | `"Budapest"` |
| `venue_country` | `str` | Venue country | `"Hungary"` |

**Note on `home_form` / `away_form`:** Each character represents a result from the team's last 5 matches. `W` = Win, `D` = Draw, `L` = Loss.

**Note on `home_logo` / `away_logo`:** These return ESPN CDN URLs only. Image retrieval and rendering is not implemented.

---

## Client Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `get_info(date, date_range, limit)` | Fetches match data from ESPN | `list[Match]` |
| `ongoing(max_time)` | Returns matches currently in progress | `list[Match]` |
| `finished(max_time)` | Returns completed matches | `list[Match]` |
| `upcoming(max_time)` | Returns scheduled matches | `list[Match]` |
| `venues(max_time)` | Returns venue info for all matches | `list[dict]` |
| `scores(max_time)` | Returns score info for all matches | `list[dict]` |
| `get_ids(max_time)` | Returns all match IDs mapped to short names | `dict` |
| `get_id(short_name, max_time)` | Returns match ID for a specific match | `str` or `None` |

**`get_info()` parameters:**
- `date` (str, optional): Specific date in YYYYMMDD format.
- `date_range` (tuple, optional): Start and end dates as `("YYYYMMDD", "YYYYMMDD")`.
- `limit` (int, optional): Maximum events to return. Default is 100.

**Cache behavior:** When `get_info()` is called with `date`, `date_range`, or a custom `limit`, the results are returned but not stored in the internal cache. This ensures that `ongoing()`, `finished()`, and `upcoming()` always operate on today's default data.

All filter methods accept `max_time` (int, seconds) for cache control. Default is `60`.

---

## Match Object

### Properties

| Property | Returns | Description |
|----------|---------|-------------|
| `is_live` | `bool` | `True` if match is currently in progress |
| `is_finished` | `bool` | `True` if match has been completed |
| `is_upcoming` | `bool` | `True` if match has not yet started |
| `venue` | `dict` | `{"venue": str, "city": str, "country": str}` |
| `score` | `dict` | `{"home": str, "home_score": str, "away_score": str, "away": str}` |

### String Representation

```python
print(match)
# Paris Saint-Germain 1 - 1 Arsenal | post | FT-Pens, Venue: Puskás Aréna, Budapest, Hungary
```

---

## Supported Leagues

The following competition slugs have been verified and tested:

| Competition | Slug | Type |
|-------------|------|------|
| FIFA World Cup | `fifa.world` | Tournament |
| English Premier League | `eng.1` | Season |
| Spanish La Liga | `esp.1` | Season |
| UEFA Champions League | `uefa.champions` | Tournament |
| MLS | `usa.1` | Season |
| Brazilian Serie A | `bra.1` | Season |
| Japanese J.League | `jpn.1` | Season |
| Australian A-League | `aus.1` | Season |

```python
# Premier League
client = SoccerClient('eng.1')

# Champions League
client = SoccerClient('uefa.champions')
```

Additional slugs may work but have not been verified. ESPN's endpoint structure is broadly consistent across most soccer competitions. for more slugs refer pseudo-r's orginal repository

---

## Caching

All filter and data-access methods implement time-based caching to minimize unnecessary API calls.

- Default cache duration is **60 seconds**.
- Cache is automatically refreshed when expired or when no data exists.
- `get_info()` with date parameters does **not** update the cache.

```python
# Uses cache if less than 60 seconds old (default)
client.ongoing()

# Uses cached data regardless of age
client.ongoing(max_time=False)

# Refreshes if data is older than 120 seconds
client.ongoing(max_time=120)
```

---

## Limitations

- **Undocumented API.** ESPN does not officially support these endpoints. They may change or be removed without notice.

- **No official rate limits.** No API key is required, but excessive requests may be blocked.

- **Inconsistent data across leagues.** Some fields including headlines, statistics, odds, records, and shootout scores vary by league and match state. These have been excluded from this release.

- **Partial data extraction.** Approximately 40% of the available `/scoreboard` data is currently parsed. Additional fields will be added in future releases.

- **Scoreboard endpoint only.** Other endpoints such as `/summary`, `/teams`, and `/rankings` are not yet supported.

- **Limited error handling.** Network failures and unexpected API responses are not yet handled with custom exceptions.

- **Schema varies by match state.** Scheduled, live, and completed matches return structurally different responses. Known variations are handled, but edge cases may exist.

- **No async support.** All requests are synchronous. Async support is planned for a future release.
- **No package structure.** The current release is not structured as an installable Python package. Import statements in the documentation reference local files directly (e.g. `from main import SoccerClient`). This will be replaced with a proper module import (e.g. `from matchdata import SoccerClient`) in a future release when the library is published to PyPI.
---

## Reporting Bugs

Encountered a bug or have a suggestion? Report it through any of the following channels:

- **GitHub Issues:** [matchdata Issues](https://github.com/thinkdev123/matchdata/issues)
- **Email:** hamza.s.bade@gmail.com
- **LinkedIn:** [Hamza Bade](https://www.linkedin.com/in/hamza-bade/)

---

## License

This project is open source under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2026 Hamza Bade

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

*Maintained by [Hamza Bade](https://github.com/thinkdev123)*
>>>>>>> a7b74b5 (Added main.py README.md and LICENSE)
