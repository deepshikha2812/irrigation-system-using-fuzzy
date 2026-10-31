# Viva Questions and Answers (based on this implementation)

## Fuzzy logic basics
**1. What is fuzzy logic?**
A logic where a statement can be partly true, with a degree between 0 and 1, instead of only true or false. It lets us model vague terms such as "dry" or "hot".

**2. What is a crisp input? A fuzzy set? A membership function?**
Crisp input: an exact number such as 28 %. Fuzzy set: a vague category such as "Dry". Membership function: a curve that gives the degree (0-1) to which a crisp value belongs to the fuzzy set.

**3. What is fuzzification?**
Converting crisp inputs into membership degrees. Example: soil 28 % → Dry 0.6, Medium 0.12, Wet 0 (function `SOIL_MOISTURE.fuzzify`).

**4. Which membership shapes did you use and why?**
Triangular and trapezoidal. They are defined by few points, are easy to explain and compute, and trapezoids give "shoulders" at the ends of a range (Dry is fully true from 0 to 20).

**5. How is the membership of 28 % in Dry calculated?**
Dry is a trapezoid (0, 0, 20, 40). Between 20 and 40 it falls linearly: (40 − 28) / (40 − 20) = 0.6.

**6. Why do neighbouring sets overlap?**
Overlap is what makes transitions gradual. At 28 % the soil is partly Dry and partly Medium, so both sets influence the answer. Without overlap we would have hard thresholds.

## Rules and inference
**7. What is a fuzzy rule? Give one from your system.**
IF soil is DRY AND temperature is HOT AND humidity is LOW THEN irrigation is VERY HIGH (rule 2).

**8. How is AND evaluated?**
With the minimum of the condition degrees (`rule_firing_strength`). Rule 2 at (20, 35, 30): min(1.0, 0.625, 0.75) = 0.625.

**9. Why 17 rules and not 27?**
The three inputs have 3 × 3 × 3 = 27 combinations, but wet soil needs no irrigation whatever the weather (rule 1 replaces 9 combinations) and cold weather with medium soil needs little regardless of humidity (rule 17 replaces 3). So: 1 wet rule + 9 dry rules + 6 medium rules (hot/normal × 3 humidities) + 1 medium-cold rule = 17, with full coverage and no rule created only to increase the count.

**10. What if two rules give the same output set?**
Each clips the same set at its own strength; aggregation by max means the stronger one wins (rules 2 and 3 in the 28/34/40 example: 0.25 and 0.5 → Very High at 0.5).

**11. What if no rule fires?**
Not possible here: the sets cover each full range and the rules cover all combinations (tested over a grid). The engine would raise an error rather than guess.

**12. Why is it called Mamdani?**
Because rule conclusions are fuzzy sets (e.g. "Very High"), which are clipped, aggregated and defuzzified. Sugeno systems use mathematical functions or constants as conclusions.

**13. What is implication and what is aggregation?**
Implication: clip the output set at the rule's strength (`np.minimum`). Aggregation: combine all clipped sets using maximum (`np.maximum`). Both are in `aggregate_output`.

## Defuzzification
**14. What is defuzzification and why is it needed?**
Converting the aggregated fuzzy shape into one number; an actuator or user needs a single irrigation percentage.

**15. How does centroid work in your code?**
`sum(x · μ(x)) / sum(μ(x))` over 1001 points (0, 0.1 … 100): the centre of gravity of the shape. Function `centroid` in `fuzzy_engine.py`.

**16. Why centroid and not mean of maxima?**
Centroid uses the entire shape, so every fired rule contributes and the output changes smoothly. Mean of maxima ignores everything but the peak and jumps.

**17. Why are category and number separate? Why can they differ?**
The number is the centroid of the whole shape; the category is the output set with the highest firing strength. For (28, 34, 40) Very High fires at 0.5 and High at only 0.12, so category = Very High, while the centroid 77.3 % lies between the High and Very High sets because the weaker rules pull it down.

**18. Why does irrigation never reach exactly 0 % or 100 %?**
Centroid averages over a clipped shape that has width, so the result stays inside the shape: Very Low gives about 9 %, Very High about 91 %. This is a known property of centroid defuzzification with this output design.

## Comparison and design
**19. Why fuzzy logic instead of if/else thresholds?**
Thresholds jump (29.9 % vs 30.1 %); fuzzy output changes gradually. Fuzzy logic also combines several inputs and keeps human-readable rules.

**20. Why fuzzy logic instead of machine learning?**
There is no labelled dataset, and fuzzy rules encode expert knowledge directly and are explainable. ML would need data.

**21. Why did you not use scikit-fuzzy?**
`skfuzzy.control` hides the inference steps and has maintenance/compatibility problems. Writing it with NumPy lets me show and explain every step.

**22. What would you change to calibrate the system for a real plant?**
Edit the breakpoints in `membership_functions.py` and rules in `rules.py` using agricultural data (e.g. the plant's wilting point and field capacity) and expert advice, then re-run the tests.

**23. Are the recommendations scientifically accurate?**
No. The ranges and rules are assumptions made for demonstration. The project demonstrates the fuzzy-logic method, not validated agronomy.

## Implementation
**24. Explain the flow of one request.**
The form sends POST /api/irrigation/predict → Pydantic validates ranges (422 on error) → `calculate_irrigation` runs → row saved in SQLite → JSON returned → React shows the result, memberships, rules and charts.

**25. Where is input validated?**
Twice: in `schemas.py` (Pydantic, returns HTTP 422 with a message), and in `validate_inputs` in the engine (guards direct use of the engine). The frontend also checks before sending.

**26. Why is the fuzzy engine separate from FastAPI?**
So it can be tested and understood without a web server or database, and reused elsewhere.

**27. How did you test it without hard-coding answers?**
Tests use ranges (e.g. case 1 must be ≥ 75 and High/Very High), hand-calculated membership and strength values, and properties: output always 0-100, wetter soil never increases irrigation, small input steps produce small output steps.

**28. What does the dashed line in the charts mean?**
On the input charts it is the entered value; its crossing with each curve is the membership degree. On the output chart it is the centroid, and the shaded area is the aggregated output.

**29. How could this connect to real hardware?**
A microcontroller with a soil-moisture sensor would send readings to the API, and the returned irrigation level would set how long a pump runs. This was not implemented.

**30. Name some limitations.**
Assumed ranges, no real sensors, only three inputs, equal rule weights, no authentication.
