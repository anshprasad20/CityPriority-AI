# CityPriority AI (Prototype): demo script and judge Q&A

Version 1.0.0 · DATATHON 2026 · Data is SYNTHETIC. Open `dashboard/citypriority_dashboard.html` before you start (works offline).

## 60-90 second walkthrough (about 90 seconds at a calm pace)

| Time | Click | Say |
|---|---|---|
| 0:00 | **Overview** | "CityPriority AI answers one question: where should a city fix first? Of 1,000 locations, 52 need immediate review. Each one trips a hard safety rule, such as an unresolved critical incident with an injury, so it ranks first whatever its score." |
| 0:20 | **Map** | "Here they are on the map. Red dots are those 52. Larger, darker green dots are higher-scoring locations. I can filter by zone, road type, or near a school or hospital." Click any red dot. |
| 0:35 | **Location** (opens from the click) | "Every rank is explained in plain words: the score, the five factors behind it, and the exact rule that triggered. Nothing is a black box." |
| 0:50 | **What-if** | "Officers can change the weights. The page says in plain words how many places each location moves, and whether the weights really matter." Drag one slider. |
| 1:05 | **Data quality**, then point at the footer | "Two honesty points. The data is synthetic, as the banner and footer say. And it can't confirm whether work is finished, so these are leads for on-site inspection, not confirmed hazards. This ranks current priority; we tested forecasting and no model beat a simple average, so we don't claim prediction." |

Tips: keep the synthetic-data banner in view. If you are short on time, skip What-if. To show the #1 location instead, open Priority list and click L0556.

## Likely judge questions, with honest answers

**1. Is this real city data?**
No. The organisers provided synthetic data with simulated coordinates and timestamps. The dashboard says so on every page, and it must not be used for real public-safety decisions.

**2. Does it predict where problems will happen next?**
No, and we say so. The score ranks *current* priority. We tested forecasting (train on January to September, predict October to December): no model beat the plain average. Poisson deviance for Q4 incidents was 1.108 for the baseline, 1.121 for the Poisson model and 1.142 for gradient boosting (lower is better). The priority score itself has AUC 0.499 for next-quarter injuries, which is chance level.

**3. Why do you call it "AI" if there is no prediction?**
The system is an explainable weighted scoring model plus hard safety rules, chosen on purpose so every rank can be explained to an officer. We tested machine-learning forecasters and they did not beat the baseline on this data, so we did not ship one.

**4. How do you know which incidents are unresolved?**
We can't fully. Every one of the 2,874 incidents marked unresolved, and every one of the 3,438 open complaints, still carries a resolution time. So the "unresolved" status needs on-site confirmation. The dashboard treats the 52 escalated locations as leads for inspection, not confirmed hazards.

**5. Why does a location with a lower score rank above a higher-scoring one?**
By design. Escalated locations always rank first because a hard safety rule (for example an unresolved Critical incident with injury) should not be outvoted by a weighted average. The highest-scoring non-escalated location is L0688 (80.7), which ranks 53rd.

**6. Where do the weights come from? Are they arbitrary?**
They are judgement-based: severity 30%, safety risk 25%, traffic impact 20%, incident frequency 15%, local context 10%. We tested stability: equal weights keep 74% (37 of 50) of the top 50, and shifting one weight by 10 points keeps 82 to 88%. The What-if page lets anyone test this live.

**7. Is severity really worth 30%?**
Probably too much, and we say so. In this data, mean severity barely changes with injuries (1.92 at zero injuries vs 1.86 at three). Lowering its weight is our first planned improvement.

**8. Traffic impact has no traffic counts. How is it measured?**
It is a proxy: road type plus the share of signal-failure and collision incidents. It is labelled "proxy" on the Method page because no traffic-count data exists.

**9. What about locations with very few incidents?**
Small samples are shrunk toward the city average so a single incident can't dominate. 31 locations have fewer than 5 incidents, and 15 are flagged low data confidence, which shows on the Priority list, each location page and the Overview.

**10. Are the map positions real?**
No. The coordinates are simulated, so the map shows relative layout only, not real streets. With real data, the same map plots real positions.

**11. Did you find any interesting patterns?**
No, and we don't claim any. The data looks randomly generated: zone averages are flat, factor correlations are near zero, and incidents are spread evenly across months. We prefer to say that than to present noise as insight.

**12. What would you do next?**
Use real data; get a reliable resolution status; add repair-cost data and traffic counts; use more than one year so seasonality can be studied; and lower the severity weight after checking it on the new data.

## Numbers to keep handy
1,000 locations · 10,000 incidents · 8,000 complaints · 52 escalated · top location L0556 (85.4) · 2025-01-01 to 2025-12-31 · 12 tests pass · v1.0.0 (prototype)
