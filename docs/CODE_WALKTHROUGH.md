# Backend Walkthrough

Read the files in this order. Each one is one stage of a fuzzy controller.

## 1. `membership_functions.py` - fuzzification
- `trapezoidal(x, a, b, c, d)`: 0 up to `a`, rises to 1 at `b`, stays 1 until `c`, falls to 0 at `d`.
  If `a == b` the left edge is vertical (a "shoulder"), which is how *Dry* is fully true at 0.
- `triangular(x, a, b, c)`: a trapezoid whose top has width zero (`b, b`).
- `FuzzySet`: a name + shape + corner points. `.membership(x)` gives the degree 0..1.
- `LinguisticVariable`: a variable (soil moisture...) with its range and fuzzy sets.
  `.fuzzify(value)` returns the degree of every set: `{dry: 0.6, medium: 0.12, wet: 0}`.
- The four variables `SOIL_MOISTURE`, `TEMPERATURE`, `HUMIDITY`, `IRRIGATION` are plain data.
  **Change a breakpoint here and the whole system changes.**

Worked example: soil = 28 %. Dry falls from 1 (at 20) to 0 (at 40): (40-28)/(40-20) = **0.6**.
Medium rises from 0 (at 25) to 1 (at 50): (28-25)/(50-25) = **0.12**. Wet = 0.

## 2. `rules.py` - the rule base
Each `Rule` is data: three conditions (or `None` = "any"), an output set and a written reason.
`Rule.conditions()` returns the IF-part, `Rule.describe()` writes it as English.
`validate_rule_base()` runs at import and rejects typos in set names.

## 3. `fuzzy_engine.py` - Mamdani inference
`calculate_irrigation()` calls five small functions in order:

| Stage | Function | What happens |
|---|---|---|
| 1 Fuzzification | `fuzzify_all` | crisp inputs -> membership degrees |
| 2 Rule evaluation | `rule_firing_strength` | AND = **minimum** of the rule's conditions |
| 3 Implication | in `aggregate_output` | output set is **clipped** at the firing strength (`np.minimum`) |
| 4 Aggregation | in `aggregate_output` | all clipped sets are combined with **maximum** (`np.maximum`) |
| 5 Defuzzification | `centroid` | `sum(x * mu) / sum(mu)` over 1001 points from 0 to 100 |

**Category vs number.** `output_set_strengths` finds how strongly each output set was activated;
`choose_category` picks the strongest. The number comes only from the centroid. They are
computed separately and can differ (e.g. 77.3 % labelled "Very High", because Very High fired at 0.5
while High fired at only 0.12).

### Full worked example: soil 28 %, temperature 34 °C, humidity 40 %
Fuzzification: Dry 0.6, Medium 0.12 | Normal 0.1, Hot 0.5 | Low 0.25, Medium 0.5

| Rule | Min of conditions | Strength | Output |
|---|---|---|---|
| R3 dry, hot, medium | min(0.6, 0.5, 0.5) | 0.50 | Very High |
| R2 dry, hot, low | min(0.6, 0.5, 0.25) | 0.25 | Very High |
| R11 medium, hot, low | min(0.12, 0.5, 0.25) | 0.12 | High |
| R12 medium, hot, medium | min(0.12, 0.5, 0.5) | 0.12 | Medium |
| R5, R6, R14, R15 | | 0.10 | High, High, Medium, Medium |

Per output set the strongest rule wins: Very High 0.5, High 0.12, Medium 0.12.
Each set is clipped at its strength, the clipped shapes are combined with max, and the centroid
of that shape is **77.32 %**.

## 4. `schemas.py`, `database.py`, `models.py`, `main.py`
- `schemas.py`: Pydantic classes. `PredictionRequest` rejects out-of-range values automatically (HTTP 422).
- `database.py`: SQLite engine; `get_db()` gives each request its own session.
- `models.py`: the `Prediction` table (id, timestamp, three inputs, level, category, recommendation).
- `main.py`:
  - `POST /api/irrigation/predict` runs the engine and saves the row (unless `"save": false`).
  - `GET  /api/irrigation/history?limit=50` returns saved rows, newest first.
  - `GET  /api/irrigation/membership-functions` returns curve points for the frontend charts.

## 5. How to modify the system
| Goal | Edit |
|---|---|
| Change a range, e.g. when Dry stops | `membership_functions.py` |
| Add or change a rule | `RULES` in `rules.py` (add a `Rule(...)` line) |
| Use another AND operator (product) | `rule_firing_strength` in `fuzzy_engine.py` |
| Use another defuzzifier (e.g. mean of maxima) | replace `centroid` |
| Change recommendation wording | `RECOMMENDATIONS` in `fuzzy_engine.py` |
