Migrating to 0.2.0
==================

0.2.0 corrects four ways the library reported wrong numbers or the wrong
exception. Most code needs no changes. The parts that do are listed here, each
with what it did before, what it does now, and what to do about it.

The theme is worth stating plainly, because it explains why these are breaking
rather than merely new: in each case the old behaviour did not fail, it
*answered*. It returned a plausible number that was wrong, or an exception that
said nothing. For nutrition data, quietly wrong is worse than loudly absent, so
0.2.0 prefers ``None`` and a specific error over a confident fabrication — and
that is a change some callers will see.

Every exception still derives from ``FdcApiError``. A broad
``except FdcApiError`` keeps catching everything it used to.

At a glance
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - What
     - Before
     - Now
   * - Missing food (HTTP 404)
     - ``FdcApiError``
     - ``FdcResourceNotFoundError``
   * - Invalid API key (HTTP 403)
     - ``FdcApiError``
     - ``FdcAuthError``
   * - Rejected request (HTTP 400)
     - ``FdcApiError``
     - ``FdcValidationError``
   * - ``e.status_code``
     - Did not exist
     - The HTTP status, or ``None``
   * - ``dri_percent`` for incomparable units
     - A wrong number
     - ``None``
   * - ``get_dri(..., DriType.UL)``
     - Always ``None``
     - The upper limit, **in grams**
   * - Energy in kJ
     - Could become ``calories``
     - Kept as ``energy_kj``
   * - API key transport
     - ``?api_key=`` query parameter
     - ``X-Api-Key`` header

1. A missing food now raises its own exception
----------------------------------------------

A food that does not exist is an ordinary outcome of a lookup, not a breakdown,
and it used to be indistinguishable from a broken API.

.. code-block:: python

   # Before: any failure looked alike
   try:
       food = client.get_food(fdc_id)
   except FdcApiError:
       ...   # 404? 500? bad key? no way to tell

   # Now
   from usda_fdc import FdcResourceNotFoundError

   try:
       food = client.get_food(fdc_id)
   except FdcResourceNotFoundError:
       return None          # it simply is not there
   except FdcApiError as e:
       if e.status_code is not None and e.status_code >= 500:
           ...              # worth retrying

**What to change:** nothing, if you catch ``FdcApiError``. If you branch on the
exception's *exact* type (``type(e) is FdcApiError``), a 404, 403 and 400 will no
longer land there.

2. ``status_code`` exists now — and the documented retry works
--------------------------------------------------------------

The documentation has long shown a retry loop guarded by
``hasattr(e, 'status_code')``. Nothing ever set that attribute, so the guard was
always ``False`` and **the loop could never run**. If you copied that example,
your retries have silently never happened.

.. code-block:: python

   # Delete the hasattr guard; it is dead code that disables the branch
   except FdcApiError as e:
       if e.status_code is not None and e.status_code >= 500:
           retry()

``status_code`` is ``None`` when the request never reached the API at all — a
refused connection, a timeout — which is itself worth branching on.

3. DRI percentages can now be ``None``
--------------------------------------

``dri_percent`` used to divide a food's amount by the DRI as a bare number,
without regard to units. The shipped data does not use one scale: iron's RDA is
``8`` **mg**, while its UL is ``0.045`` **g**. So 100 g of spinach against iron's
upper limit reported ``2802.2%`` of it. The true figure is 2.8%.

Amounts are now converted into the DRI's unit before the division. Where the two
cannot be compared at all — vitamin A in IU against a µg allowance — the answer
is ``None``, not a number.

**What to change:** guard for ``None`` before formatting.

.. code-block:: python

   # Before: crashes on None, and silently printed nonsense before that
   print(f"{value.dri_percent:.1f}%")

   # Now
   percent = f"{value.dri_percent:.1f}%" if value.dri_percent is not None else "n/a"

4. ``DriType.UL`` returns data — in grams
-----------------------------------------

Upper limits used to come back as ``None`` for every nutrient, because
``ul.json`` ships under a different schema than the loader could read. It works
now, but that file expresses everything in grams, where ``rda.json`` uses a
natural unit per nutrient.

If you call ``get_dri`` directly and assumed one unit, you must now check. Use
``get_dri_value``, which hands you the unit with the number:

.. code-block:: python

   from usda_fdc.analysis.dri import get_dri_value, DriType, Gender

   rda = get_dri_value("iron", DriType.RDA, Gender.MALE, 30)   # 8, "mg"
   ul  = get_dri_value("iron", DriType.UL,  Gender.MALE, 30)   # 0.045, "g"

``analyze_food`` already does this conversion for you; only direct ``get_dri``
callers are affected.

``DriType.AI``, ``EAR`` and ``AMDR`` ship no data. They still return ``None``,
but now log a warning once saying so, rather than leaving an empty column with
no explanation.

5. Calories no longer come back as kilojoules
---------------------------------------------

FDC lists a food's energy several times over under the same name — in kcal, and
again in kJ, plus Atwater variants. All of them were matched by name and keyed as
``calories``, so whichever came last in the list won. Clarified butter lists 900
kcal and then 3766 kJ, and was analysed as **3766 calories**, which the CLI and
the HTML report duly printed with a ``kcal`` suffix.

``calories_per_serving`` is now always a kcal figure, and the kilojoule value is
kept separately under ``energy_kj``:

.. code-block:: python

   analysis.calories_per_serving              # 900.0, was 3766.0
   analysis.get_nutrient("energy_kj").amount  # 3766.0, if you want it

**What to change:** nothing, unless you stored calorie figures computed by an
earlier version — those may be overstated by roughly 4.2x for affected foods, and
are worth recomputing.

6. The API key travels as a header
----------------------------------

It used to go in the query string, and ``requests`` puts the full URL into its
exception messages — so the first connection blip wrote your key into your
tracebacks, log files and error tracker. It is now sent as ``X-Api-Key``, and
redacted from error messages as a backstop.

``FdcClient(api_key=...)`` and ``FDC_API_KEY`` are unchanged. This only matters
if you point ``base_url`` at a proxy or a recorded fixture that expects the key
as a query parameter — those need to read the header instead.

7. Abridged foods keep their nutrients
--------------------------------------

``get_food(fdc_id, format="abridged")`` used to return a food with **zero**
nutrients, silently: the abridged response inlines each nutrient's fields rather
than nesting them, and only the nested shape was parsed. A food with 18 nutrients
came back with none, and anything computing nutrition from it got zeros.

Both shapes are understood now. If you worked around this by avoiding
``abridged``, you no longer need to.
