# Time Served Estimator

Louisiana time-to-serve estimator for client meetings, for offenses **committed on or after August 1, 2024** (truth in sentencing, La. R.S. 15:571.3.1). Clone of GitHub `hammersong44-dot/pd-sentencing-calculator`.

## How to open

Double-click `index.html`. It works offline and saves nothing. `Time Served Estimator - offline.html` is an identical copy.

## What it does

1. **Offense.** Type a name ("battery") or number ("14:34.1"). It searches every active section of Title 14 and R.S. 40:961 to 991 (725 sections) and tags the pick as a sex offense (R.S. 15:541(24)), a crime of violence (R.S. 14:2(B)), or neither. Where the tag depends on a subsection (domestic abuse battery, heroin or fentanyl distribution, 14:95.1(D), vehicular homicide over 0.20 and so on), it asks a yes/no question. It also suggests felony or misdemeanor from the penalty text; you can change it.
2. **Prior record.** Prior crime-of-violence or sex-offense convictions, prior nonviolent felonies, habitual offender adjudication, and the peace officer/first responder death box.
3. **Sentence.** Years, months, jail credit days, sentencing date.
4. **Program credit slider.** 0 to 360 days (R.S. 15:828(B)), plus checkboxes for work release (+180, 15:828(D)) and degrees (+90 each, 15:828(E), (F)).
5. **Result.** Time left after sentencing, estimated release date, every step of the math with its statute, and warnings. Print button gives a black-and-white worksheet with blank client and docket lines.

## Rules applied

| Rule | Source |
|---|---|
| Sentence less jail credit; no good time on jail credit | C.Cr.P. art. 880; R.S. 15:571.3.1(D) |
| Good time up to 15%, so serve 85% of the balance (DOC method) | R.S. 15:571.3.1(B) |
| Sex offense: flat, no good time, no program credit | R.S. 15:571.3.1(B), (C); 15:571.3(C)(2); 15:537(A) |
| Habitual offender: no good time, program credit allowed | R.S. 15:571.3.1(B); 15:828(C) |
| Crime of violence with 2+ prior COV/sex convictions: no program credit | R.S. 15:828(C)(2) |
| Program credit caps 360 / +180 / +90 / +90 | R.S. 15:828(B) to (F) |
| Release is to unsupervised parole until full term | R.S. 15:571.3.1(F)(1); 15:571.5 |
| No parole for post-8/1/2024 offenses (narrow exceptions) | R.S. 15:574.22 |

Good time is rounded down to whole days, so the estimate never understates time.

**Open questions (TODO in the code, verify before relying):**
- Misdemeanors: 15:571.3.1 covers felonies only and 15:571.3(H) bars other good time, so the app treats a post-2024 misdemeanor as flat. Sheriffs may compute it differently.
- Peace officer/first responder death: the app uses the 15:571.3(F) rate (1 day per 30). Whether (F) or 15:571.3.1 controls for post-2024 offenses is unsettled.
- DOC applies the 15% to the sentence less jail credit; the statute says "fifteen percent of the particular sentence imposed." The app follows DOC.

**Not covered:** offenses before August 1, 2024 (old R.S. 15:571.3 rates), consecutive/concurrent stacking, parole exceptions in 15:574.4(D) to (K), good-time forfeiture, firearm enhancements.

## Self-test

Open "Self-test" at the bottom of the page: 11 known-answer cases, including DOC's 2025 PDAL seminar examples (10 yr with 1 yr jail credit and 360 days CTRP = about 6.65 yr; the app gives 2,434 days, 6.66 yr).

## Updating the offense list

The offense list and its classifications come from the Louisiana Law Reference vault. After the vault statutes are refreshed, or if R.S. 14:2(B) or 15:541 is amended (edit the tables in the script first), run:

```bash
python3 tools/build_offenses.py
```

Then copy `index.html` over the offline copy. Standard library only; no packages.

## Files

- `index.html`: the app (rebuilt 2026-10-24).
- `tools/build_offenses.py`: builds the offense list from the vault.
- `reference/`: PDAL 2025 seminar notes on the 2024 and 2025 changes.
- `backups/`: earlier versions, including the design-tool export (`*_prestatute.html`).
- `Time Served Estimator.dc.html`, `support.js`, `sw.js`, `manifest.json`: leftovers from the old design-tool version; the new app doesn't use them.

Rules last verified 2026-10-24 against vault text retrieved from legis.la.gov 2026-10-15. Not committed or pushed to GitHub yet.
