# Working Notes

Context and open work for this library, written from the perspective of its
main consumer. Not a spec — see `README.md`, `TODO.md`, and `RELEASE.md`.

## Who consumes this

[nutrition_api](https://github.com/mcgarrah/nutrition_api) (cloned at
`/opt/nutrition_api` on the `nutrition-api-dev` LXC) uses this library as its
USDA FoodData Central client. It aggregates USDA + Open Food Facts + GS1 GPC
behind one `/api/v1/lookup/{gtin}` endpoint, and it looks foods up **by
barcode**, which is the source of both issues below.

Sibling repos, all under `/opt`: `gs1_gpc_python`, `gpcc`, `oneworldsync_python`,
`nutrimetrics`, `nutrition_api`.

---

## 1. `gtin_upc` — fix written, needs review + release

**Status:** PR [#8](https://github.com/mcgarrah/usda_fdc_python/pull/8) is open
on branch `claude/expose-gtin-upc`. Code is done and tested (35/35 unit tests,
verified against the live FDC API). Version bumped to **0.1.10** with a
changelog entry.

**What was wrong:** the FDC API returns `gtinUpc` for branded foods, but `Food`
and `SearchResultFood` both dropped it — the string "gtin" appeared nowhere in
the library.

**Why it matters:** FDC has no barcode-lookup endpoint. Looking a product up by
barcode means using the **full-text search**, and that search is fuzzy — an
unknown barcode cheerfully returns unrelated products:

```
query "00000000"  ->  "ALL NATURAL GLUTEN FREE CHICKEN NUGGETS"
                      (that food's real barcode is 0099447210127)
```

Without `gtin_upc`, a caller cannot verify a hit *is* the barcode it asked for,
and ends up serving **one product's nutrition under another product's barcode**.
For nutrition data, silently wrong is worse than no answer.

### What still needs doing

1. Review and merge PR #8.
2. **Release 0.1.10 to PyPI** — follow `RELEASE.md` (`python3 version_update.py`
   has already been done by hand; versions in `setup.py` and `pyproject.toml`
   both say 0.1.10).

### Why the release is the blocking step

`nutrition_api` currently reaches **past this library's public API** to get the
field, in `app/core/usda_fdc.py:search_by_upc`:

```python
raw = await _run_sync(
    client._make_request,                 # private method!
    "foods/search",
    params={"query": upc, "dataType": ["Branded"], "pageSize": 10},
)
for food in raw.get("foods", []):
    if normalize_gtin(food.get("gtinUpc", "")) == target:
        ...
```

Once 0.1.10 is **on PyPI**, that becomes the supported call and the workaround
is deleted:

```python
result = await _run_sync(client.search, upc, data_type=["Branded"], page_size=10)
for food in result.foods:
    if normalize_gtin(food.gtin_upc or "") == target:
        ...
```

I made that change in `nutrition_api` and had to **revert it**: its CI installs
`usda-fdc` from PyPI, where the newest release is 0.1.9 and has no `gtin_upc`.
So the cleanup can't ship until the release does. The order is:

**merge #8 → publish 0.1.10 → bump `usda-fdc>=0.1.10` in nutrition_api → delete the workaround**

---

## 2. No HTTP timeout — not yet fixed

**`usda_fdc/client.py:86`** issues every request with no timeout:

```python
response = self.session.request(
    method=method,
    url=url,
    params=params,
    json=data,
)   # <-- no timeout=
```

`requests` has **no default timeout**. If the FDC API accepts the TCP connection
and then never answers — a stalled socket rather than a refused one — this call
blocks **forever**. Not for 30 seconds. Forever.

**Why this bites hard.** The library is synchronous, so async consumers run it in
a thread pool. `nutrition_api` wraps each call in `asyncio.wait_for(...)`, but
that only cancels the *await* — **it cannot cancel the blocking call underneath**.
The caller is freed at 2 seconds; the thread stays stuck. With no socket timeout,
that thread is gone for the life of the process. Enough stalled calls and the
pool is permanently dead.

(`nutrition_api` now gives each upstream its own bounded pool so a stalled USDA
can't starve Open Food Facts, but that only *contains* the damage. The leak
itself can only be fixed here.)

### Suggested fix

Add a `timeout` to the client and pass it through:

```python
DEFAULT_TIMEOUT = 30.0   # seconds

def __init__(
    self,
    api_key: Optional[str] = None,
    base_url: str = "https://api.nal.usda.gov/fdc/v1/",
    timeout: float = DEFAULT_TIMEOUT,
):
    ...
    self.timeout = timeout

# in _make_request:
response = self.session.request(
    method=method,
    url=url,
    params=params,
    json=data,
    timeout=self.timeout,      # connect + read
)
```

Then `requests.exceptions.Timeout` should surface as an `FdcApiError` (or a new
`FdcTimeoutError`) so callers can distinguish "slow" from "broken" — see
`usda_fdc/exceptions.py`, which already models auth and rate-limit errors this
way.

**Tests worth having:**

- a request that exceeds the timeout raises rather than hanging (mock the
  session so nothing real is slow)
- the timeout is configurable per client, and defaults to something sane
- the default is actually passed to `session.request` — the easy regression is
  adding the parameter but forgetting to use it

---

## 3. Smaller observations

- `_make_request` is the only way to reach fields the models drop. Every such
  gap pushes consumers onto a private method. Issue 1 is one instance; worth
  auditing `from_api_data` against the FDC response for others (e.g. branded
  foods also carry `foodUpdateLog`, `marketCountry`, `packageWeight`).
- The FDC search API caps `pageSize` at 200; the library does not validate it,
  so an out-of-range value fails at the API rather than locally.
