# Release Notes for v0.2.0

## Overview

Version 0.2.0 fixes six ways this library reported the wrong number or the wrong
error. Every one of them failed the same way: **not by breaking, but by
answering** — returning a plausible figure that was wrong, or an exception that
said nothing about what happened.

For a nutrition library that is the worst failure mode there is. A caller who
gets an error retries or reports it. A caller who gets `3766 calories` for a food
that has 900 serves it to someone.

The minor version bumps because fixing these changes behaviour. Most code needs
no edits; the exceptions are listed under [Breaking changes](#breaking-changes)
and walked through in [docs/user/migration.rst](docs/user/migration.rst).

## What was wrong

### A food's kilojoules could be served as its calories

FDC reports a food's energy several times, under the same name: in kcal
(nutrient 1008), again in kJ (1062), and once or twice more as Atwater variants
(2047/2048). All of them were matched on the name alone and stored as
`calories`, so whichever happened to come last in the list won.

Clarified butter (`fdc_id` 171314) lists 900 kcal and then 3766 kJ:

```python
analyze_food(client.get_food(171314)).calories_per_serving
# 3766.0   <- its kilojoule figure, 4.2x the truth
```

...which `analysis/cli.py` and the HTML report then printed with a `kcal` suffix.
Foods carrying two Atwater rows (a raw apple has 64.66 and 58.20 kcal) had their
calorie count decided by list order.

Energy is now matched on its nutrient id/number **and** its unit. Only kcal rows
can become `calories`, the plain `Energy` row is preferred over the Atwater
variants so the result cannot depend on ordering, and the kJ figure is kept under
`energy_kj` rather than overwriting anything.

### An upper intake limit was 1000x out

The DRI data does not use one scale: `rda.json` gives iron's RDA as `8` **mg**,
while `ul.json` gives its upper limit as `0.045` **g**. `dri_percent` divided the
food's amount by the DRI as a bare number, with no regard for either unit. 100 g
of spinach measured against iron's upper limit came out as **2802.2%** of it. The
real answer is 2.8%.

Amounts are now converted into the DRI's own unit first. Where the two cannot be
compared at all — vitamin A in IU against a µg allowance — the answer is `None`
rather than a fabricated percentage.

### Only one of the five DRI types actually worked

`ul.json` ships real Tolerable Upper Intake Levels, but under a different schema
than the loader could read, so **every UL lookup returned `None`**. Both schemas
are understood now. `DriType.AI`, `EAR` and `AMDR` ship no data at all — they
still return `None`, but log a warning saying so, instead of leaving an empty DRI
column with no explanation. The docs claimed data for all five; they now say
which two are real.

### The API key leaked into exception messages

The key travelled as a query parameter, and `requests` embeds the full URL in its
exception text. One connection blip wrote it into the caller's traceback, log
files and error tracker:

```
FdcApiError: Request failed: ... Max retries exceeded with url:
/fdc/v1/food/1750340?format=full&api_key=YOUR_REAL_KEY
```

It now goes out as an `X-Api-Key` header (which api.data.gov, fronting FDC,
accepts), so it never enters a URL, and it is redacted from error messages as a
backstop. **If you have been running an earlier version with a real key and your
logs are somewhere you would not want the key to be, rotate it.**

### Every failure looked the same

`FdcApiError` carried no `status_code`, although the documentation told callers
to branch on it and shipped a retry-on-5xx example built around
`hasattr(e, 'status_code')` — which was always `False`. **If you copied that
example, your retries have never run.**

`FdcResourceNotFoundError` and `FdcValidationError` were defined, documented, and
raised by nothing; they were not even exported from the package root. And because
FDC sits behind api.data.gov, which rejects a bad key with **403** rather than
401, the single most common caller mistake missed `FdcAuthError` entirely.

Now: 403 → `FdcAuthError`, 404 → `FdcResourceNotFoundError`, 400 →
`FdcValidationError`, 429 → `FdcRateLimitError`, and every exception carries the
status it came from (`None` when the request never reached the API).

### Abridged foods came back with no nutrients

`get_food(fdc_id, format="abridged")` returned a food with **zero** nutrients,
silently — the abridged response inlines each nutrient's fields instead of
nesting them, and only the nested shape was parsed. A food with 18 nutrients
arrived with none, and anything computing nutrition from it got zeros.

## Breaking changes

| What | Before | Now |
|---|---|---|
| Missing food (404) | `FdcApiError` | `FdcResourceNotFoundError` |
| Invalid key (403) | `FdcApiError` | `FdcAuthError` |
| Rejected request (400) | `FdcApiError` | `FdcValidationError` |
| `dri_percent`, incomparable units | A wrong number | `None` |
| `get_dri(..., DriType.UL)` | Always `None` | A value, **in grams** |
| `calories_per_serving` | Sometimes the kJ figure | Always kcal |
| API key transport | `?api_key=` query param | `X-Api-Key` header |

All exceptions still derive from `FdcApiError`, so a broad `except FdcApiError`
catches everything it always did. The three edits most likely to be needed:

1. Guard `dri_percent` for `None` before formatting it.
2. Drop any `hasattr(e, 'status_code')` guard — it disables the branch it guards.
3. If you call `get_dri` directly for a UL, read the unit via `get_dri_value`.

## Also in this release

- A request timeout on every call (default 30s), raising `FdcTimeoutError`
  instead of blocking a thread forever. `requests` has no default timeout, so a
  server that accepted a connection and never answered used to hang the calling
  thread for the life of the process.
- CI: the repository had none. Pull requests are now tested on Python 3.8, 3.11
  and 3.13, and the PyPI publish is gated behind those tests — a release can no
  longer ship code that fails its own suite.

### Barcode lookups

`gtin_upc` is exposed on `Food` and `SearchResultFood`. This matters more than it
sounds: FDC has **no barcode-lookup endpoint**, so looking a product up by
barcode means using the full-text search — which is fuzzy, and will answer an
unknown barcode with a confident, unrelated product. Searching `00000000` returns
455,982 hits, led by a chicken nugget product whose real barcode is
`0099447210127`.

Without the barcode on the result there is no way to check that a hit *is* what
you asked for, and a caller ends up serving one product's nutrition under another
product's barcode. Always verify:

```python
for food in client.search(barcode, data_type=["Branded"]).foods:
    if food.gtin_upc and food.gtin_upc.lstrip("0") == barcode.lstrip("0"):
        return food
return None   # no match beats the wrong food
```

## Upgrading

```bash
pip install --upgrade usda-fdc
```

See [docs/user/migration.rst](docs/user/migration.rst) for the migration guide,
and [CHANGELOG.md](CHANGELOG.md) for the full history.
