# Smart Plant Irrigation System Using Mamdani Fuzzy Logic
*Project report draft. Replace [bracketed] items with your own details.*

> **Scope statement.** This project is an academic demonstration of fuzzy logic. The membership
> ranges and rules are project assumptions. The system does not provide scientifically accurate
> irrigation recommendations for any specific plant. For a real plant, the ranges and rules would
> have to be calibrated using agricultural data and expert knowledge.

## 1. Abstract
Irrigation decisions depend on imprecise conditions such as "the soil is quite dry" or "it is fairly hot". This project implements a web-based irrigation advisor that takes soil moisture, temperature and humidity and computes an irrigation level (0-100 %) using a Mamdani fuzzy inference system. The engine is written from scratch with NumPy: triangular and trapezoidal membership functions, a base of 17 IF-THEN rules, min/max inference and centroid defuzzification. A FastAPI backend exposes the engine, SQLite stores predictions, and a React dashboard shows the result, the membership degrees, the rules that fired, the membership-function graphs and the prediction history. The project shows that fuzzy logic produces smooth, explainable decisions where hard thresholds would jump abruptly.

## 2. Problem Statement
A simple controller that waters when soil moisture falls below one fixed number (for example 30 %) treats 29.9 % and 30.1 % as completely different situations and ignores temperature and humidity. Human gardeners reason with vague terms and combine several factors. The problem is to build a system that combines several imprecise inputs and produces a gradual, explainable irrigation decision.

## 3. Objectives
1. Accept soil moisture, temperature and humidity as crisp inputs.
2. Define fuzzy sets and membership functions for each variable.
3. Build a rule base of logical, explainable rules.
4. Implement Mamdani inference with aggregation and centroid defuzzification.
5. Return a numerical irrigation level, a category and a recommendation.
6. Provide a REST API, a database of past predictions and an interactive dashboard.
7. Make every stage of the fuzzy process visible to the user.

## 4. Existing System
- **Manual watering** by experience: subjective and inconsistent.
- **Timer-based irrigation:** waters on a schedule regardless of conditions, wasting water.
- **Threshold-based controllers** (if moisture < X then water): simple, but abrupt, single-factor and sensitive to sensor noise near the threshold.

## 5. Proposed System
A fuzzy controller that evaluates three inputs together. Each reading belongs partly to several fuzzy sets at once, 17 rules fire to different degrees, and their combined effect gives a smooth irrigation percentage. The result is accompanied by the fuzzy analysis (memberships and fired rules) so the decision can be explained.

## 6. Why Fuzzy Logic?
- It models linguistic, imprecise knowledge ("dry", "hot") directly.
- Output changes gradually with input: no sudden jumps (verified by an automated test: a 1-unit input step changes the output by less than 5 points).
- Rules are readable by non-programmers and easy to modify.
- It needs no training data, unlike machine-learning approaches, which suits a project where no labelled dataset exists.
- Decisions are transparent: each can be traced to specific rules.

## 7. System Architecture
```
 React dashboard (Vite, Recharts)
        |  HTTP / JSON  (proxy /api -> :8000)
        v
 FastAPI  (main.py, schemas.py: validation)
        |                     |
        v                     v
 Fuzzy engine           SQLite via SQLAlchemy
 (fuzzy_engine.py,      (database.py, models.py)
  membership_functions.py,
  rules.py)
```
Request flow: the form sends `POST /api/irrigation/predict`; FastAPI validates the input; the engine computes the result; the row is saved; the JSON response drives the result card, analysis tables and charts; the history is reloaded.

## 8. Fuzzy Logic Methodology
1. **Crisp inputs:** soil moisture, temperature, humidity.
2. **Fuzzification:** each input is converted to membership degrees of its fuzzy sets.
3. **Rule evaluation:** for each rule, firing strength = minimum of its condition degrees (AND = min).
4. **Implication:** each rule clips its output set at its firing strength.
5. **Aggregation:** the clipped sets are combined by maximum into one fuzzy shape.
6. **Defuzzification:** the centroid of the shape gives the crisp irrigation level.
7. **Categorisation:** the output set with the highest firing strength gives the category (kept separate from the number).

## 9. Membership Functions
All values are project assumptions. Triangles are listed as (a, b, c), trapezoids as (a, b, c, d).

| Variable (range) | Set | Shape | Points |
|---|---|---|---|
| Soil moisture (0-100 %) | Dry | trapezoid | 0, 0, 20, 40 |
| | Medium | triangle | 25, 50, 75 |
| | Wet | trapezoid | 60, 80, 100, 100 |
| Temperature (0-45 °C) | Cold | trapezoid | 0, 0, 10, 20 |
| | Normal | triangle | 15, 25, 35 |
| | Hot | trapezoid | 30, 38, 45, 45 |
| Humidity (0-100 %) | Low | trapezoid | 0, 0, 25, 45 |
| | Medium | triangle | 30, 50, 70 |
| | High | trapezoid | 55, 75, 100, 100 |
| Irrigation (0-100 %) | Very Low | trapezoid | 0, 0, 10, 25 |
| | Low | triangle | 10, 25, 40 |
| | Medium | triangle | 30, 50, 70 |
| | High | triangle | 60, 75, 90 |
| | Very High | trapezoid | 75, 90, 100, 100 |

Neighbouring sets overlap on purpose; the overlap is what makes transitions gradual. Every value in each range belongs to at least one set (checked by a test).

## 10. Rule Base
| # | Soil | Temp | Humidity | Irrigation | Reasoning |
|---|---|---|---|---|---|
| 1 | Wet | any | any | Very Low | Wet soil already has enough water. |
| 2 | Dry | Hot | Low | Very High | No reserve, fastest water loss. |
| 3 | Dry | Hot | Medium | Very High | Humidity is not high enough to slow evaporation. |
| 4 | Dry | Hot | High | High | Humid air slows evaporation: one level lower. |
| 5 | Dry | Normal | Low | High | Dry air increases loss. |
| 6 | Dry | Normal | Medium | High | Dry soil needs plenty of water. |
| 7 | Dry | Normal | High | Medium | Humidity reduces loss. |
| 8 | Dry | Cold | Low | Medium | Little evaporation in cold, but soil and air are dry. |
| 9 | Dry | Cold | Medium | Medium | Cold lowers need. |
| 10 | Dry | Cold | High | Low | Cold and humid: very little loss. |
| 11 | Medium | Hot | Low | High | Hot dry air will drain half-full soil quickly. |
| 12 | Medium | Hot | Medium | Medium | Heat speeds drying: moderate top-up. |
| 13 | Medium | Hot | High | Low | Humidity offsets the heat. |
| 14 | Medium | Normal | Low | Medium | Dry air dries the soil. |
| 15 | Medium | Normal | Medium | Medium | Everything average. |
| 16 | Medium | Normal | High | Low | Humid air keeps soil moist. |
| 17 | Medium | Cold | any | Low | Cold: little evaporation. |

The rule base covers all 27 input combinations: dry and medium soil are covered in every temperature/humidity combination, and wet soil is covered by rule 1.

## 11. Mamdani Inference Explanation
Mamdani inference keeps both the conditions and the conclusions fuzzy. For each rule the AND of conditions is the minimum of their degrees. The rule's output set is then cut off (clipped) at that strength, meaning "we are only this confident in this conclusion". Clipped sets of all rules are merged by maximum (aggregation). The result is one irregular shape describing how much each irrigation value is supported.

*Worked example (soil 28 %, temp 34 °C, humidity 40 %):* memberships Dry 0.6, Medium 0.12; Normal 0.1, Hot 0.5; Low 0.25, Medium 0.5. Strongest rule: R3 = min(0.6, 0.5, 0.5) = 0.5 → Very High clipped at 0.5. R2 gives 0.25 (Very High), R11 gives 0.12 (High), R12 gives 0.12 (Medium). The aggregated shape has its centroid at 77.32 %.

## 12. Defuzzification Explanation
The aggregated shape cannot be sent to a valve; a single number is needed. The **centroid (centre of gravity)** method is used: irrigation = Σ(x · μ(x)) / Σ μ(x), computed over 1001 points between 0 and 100 (step 0.1). It uses the whole shape, so every fired rule influences the answer, and it changes smoothly. The **category** is separate: it is the output fuzzy set with the highest firing strength. Because the two are computed differently they can occasionally disagree slightly (e.g. 77.3 % labelled Very High).

## 13. Backend Architecture
| File | Responsibility |
|---|---|
| `membership_functions.py` | shape functions, fuzzy sets, fuzzification |
| `rules.py` | rule base as data, with reasons |
| `fuzzy_engine.py` | rule evaluation, aggregation, centroid, `calculate_irrigation()` |
| `schemas.py` | request/response models and range validation |
| `database.py`, `models.py` | SQLite connection and table |
| `main.py` | endpoints, CORS, saving to the database |

The engine does not import FastAPI or the database, so it can be tested and reused independently.

## 14. Database Design
SQLite file `irrigation.db`, table `predictions`:

| Column | Type | Description |
|---|---|---|
| id | integer, primary key | auto-increment |
| timestamp | datetime | local time of the prediction |
| soil_moisture | float | input (%) |
| temperature | float | input (°C) |
| humidity | float | input (%) |
| irrigation_level | float | crisp output (%) |
| irrigation_category | text | e.g. "High" |
| recommendation | text | sentence shown to the user |

## 15. API Documentation
Interactive docs: `http://127.0.0.1:8000/docs`.

**POST /api/irrigation/predict**
```json
Request:  {"soil_moisture": 28, "temperature": 34, "humidity": 40, "save": true}
Response: {"irrigation_level": 77.32, "category": "Very High",
           "recommendation": "Very high irrigation: water immediately and thoroughly.",
           "membership_values": {"soil_moisture": {"dry": 0.6, "medium": 0.12, "wet": 0.0},
                                 "temperature": {"cold": 0.0, "normal": 0.1, "hot": 0.5},
                                 "humidity": {"low": 0.25, "medium": 0.5, "high": 0.0}},
           "output_strengths": {...}, "activated_rules": [...],
           "aggregated_output": {...}, "saved": true, "id": 1}
```
`save` is optional (default true). Out-of-range or non-numeric values return **422** with a message naming the field, e.g. "Input should be less than or equal to 100".

**GET /api/irrigation/history?limit=50**: saved predictions, newest first (limit 1-500).

**GET /api/irrigation/membership-functions**: curve points for all fuzzy sets (used by the charts).

## 16. Frontend Explanation
React + Vite single page. `App.jsx` holds the state and calls `api.js`. Components: `InputForm` (validated inputs and three example presets), `ResultCard`, `FuzzyAnalysis` (membership bars and fired rules), `MembershipCharts` (four graphs; dashed line = input or centroid; shaded area = aggregated output), `HistoryChart` and `HistoryTable`. Recharts draws the graphs. The Vite dev server proxies `/api` to FastAPI.

## 17. Test Cases
55 automated tests (pytest), grouped as: membership functions (including a hand-calculated value), rule base integrity, engine behaviour, and API/database.

| Case | Input (soil, temp, humidity) | Expected | Check |
|---|---|---|---|
| 1 | 20, 35, 30 | High or Very High, ≥ 75 | range |
| 2 | 80, 25, 70 | Very Low, ≤ 20 | range |
| 3 | 50, 25, 50 | Medium, 40-60 | range |
| Boundaries | (0,0,0), (100,45,100), (0,45,0), (100,0,100) | valid result in 0-100 | |
| Invalid | -1, 101, temp 46, NaN, infinity, text | rejected (ValueError / HTTP 422) | |
| Properties | wetter soil never increases irrigation; hotter weather never decreases it for dry soil; full input grid always gives 0-100 | | |

Expected values are ranges and mathematical properties, not copies of the program's output.

## 18. Results
Actual outputs of the system:

| Soil % | Temp °C | Humidity % | Irrigation % | Category | Main rule |
|---|---|---|---|---|---|
| 20 | 35 | 30 | 89.69 | Very High | R2 (0.625) |
| 80 | 25 | 70 | 9.26 | Very Low | R1 (1.0) |
| 50 | 25 | 50 | 50.00 | Medium | R15 (1.0) |
| 28 | 34 | 40 | 77.32 | Very High | R3 (0.5) |
| 65 | 25 | 50 | 38.02 | Medium | R15 (0.4), R1 (0.25) |
| 40 | 30 | 40 | 50.00 | Medium | R15 (0.5), R14 (0.25) |

Dry/hot/dry-air conditions give high irrigation, wet soil gives very low irrigation, and average conditions give about 50 %. The case (65, 25, 50), where soil is between medium and wet, gives 38 %: the output decreases gradually rather than jumping, which is the fuzzy behaviour the project set out to demonstrate.

## 19. Limitations
- Ranges and rules are assumptions, not calibrated for any plant, soil type or climate.
- Inputs are typed manually; no real sensors or pumps are connected.
- Only three inputs; plant type, soil type, rainfall forecast and time of day are ignored.
- All rules have equal weight.
- Category and centroid can differ slightly.
- No authentication; designed for local use.

## 20. Future Scope
- Calibrate membership functions with agricultural data and expert input for a chosen plant.
- Read live data from sensors (e.g. Arduino/ESP32 with a soil-moisture sensor) and drive a pump.
- Add inputs such as rainfall forecast, soil type, plant type.
- Compare against a threshold controller and against a Sugeno system.
- Tune rule weights and membership shapes with optimisation.

## 21. Conclusion
The project implements a complete, transparent Mamdani fuzzy controller and shows how fuzzy logic turns vague conditions into a smooth numerical decision. Every stage (fuzzification, rule evaluation, implication, aggregation, centroid defuzzification) is visible in the code, API and dashboard. Because the ranges and rules are assumptions, the system is a demonstration of the method rather than a validated agricultural tool.
