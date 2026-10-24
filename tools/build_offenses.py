#!/usr/bin/env python3
"""
Build the offense list for the Time Served Estimator.

What it does, in plain terms:
  1. Reads every Title 14 section and R.S. 40:961-991 section in the
     Louisiana Law Reference vault (one Markdown file per section).
  2. Keeps the active sections (drops "Repealed" and redesignated ones).
  3. Tags each one as a crime of violence (R.S. 14:2(B)) and/or a
     sex offense (R.S. 15:541(24)), using the tables below.
     Some offenses are only a crime of violence or sex offense under a
     particular subsection; those are tagged "cond" with the question
     the app asks the user.
  4. Notes whether the penalty sentences mention "hard labor" (a hint
     about felony grade; R.S. 14:2(A)(4)): all of them, some, or none.
  5. Writes the list into index.html between the OFFENSES markers.

Run it again whenever the vault statutes are refreshed:
    python3 tools/build_offenses.py

Standard library only. Nothing is sent anywhere.
"""
import json
import pathlib
import re
import sys

VAULT = pathlib.Path.home() / "Library/CloudStorage/Dropbox/Louisiana Law/Louisiana Law Reference/Louisiana Revised Statutes"
FOLDERS = [VAULT / "Title 14", VAULT / "Title 40 (961-991)"]
APP = pathlib.Path(__file__).resolve().parent.parent / "index.html"

# ---------------------------------------------------------------------------
# R.S. 14:2(B) enumerated crimes of violence (vault text retrieved 2026-10-15).
# Number in the comment is the paragraph of 14:2(B). Attempts are included by
# the preamble of 14:2(B).
# Value True = always a crime of violence.
# Value str  = only in the stated circumstance; the string is the question.
# ---------------------------------------------------------------------------
COV = {
    "14:28.1": True,    # (1) Solicitation for murder
    "14:30": True,      # (2) First degree murder
    "14:30.1": True,    # (3) Second degree murder
    "14:31": True,      # (4) Manslaughter
    "14:34": True,      # (5) Aggravated battery
    "14:34.1": True,    # (6) Second degree battery
    "14:37": True,      # (7) Aggravated assault
    "14:44.2": True,    # (8) Aggravated kidnapping of a child
    "14:42": True,      # (9) Aggravated or first degree rape
    "14:42.1": True,    # (10) Forcible or second degree rape
    "14:43": True,      # (11) Simple or third degree rape
    "14:43.1": True,    # (12) Sexual battery
    "14:43.2": True,    # (13) Second degree sexual battery
    "14:43.5": True,    # (14) Intentional exposure to AIDS virus (now "HIV")
    "14:44": True,      # (15) Aggravated kidnapping
    "14:44.1": True,    # (16) Second degree kidnapping
    "14:45": True,      # (17) Simple kidnapping
    "14:51": True,      # (18) Aggravated arson
    "14:55": True,      # (19) Aggravated criminal damage to property
    "14:60": True,      # (20) Aggravated burglary
    "14:64": True,      # (21) Armed robbery
    "14:64.1": True,    # (22) First degree robbery
    "14:65": True,      # (23) Simple robbery
    "14:65.1": True,    # (24) Purse snatching
    "14:46.1": True,    # (25) False imprisonment; offender armed with dangerous weapon
    "14:37.1": True,    # (26) Assault by drive-by shooting
    "14:89.1": True,    # (27) Aggravated crime against nature
    "14:64.2": True,    # (28) Carjacking
    "14:81.2": True,    # (29) Molestation of a juvenile or person with disability
    "14:128.1": True,   # (30) Terrorism
    "14:34.7": True,    # (31) Aggravated second degree battery
    "14:37.2": True,    # (32) Aggravated assault upon a peace officer
    "14:37.4": True,    # (33) Aggravated assault with a firearm
    "14:64.3": True,    # (34) Armed robbery; use of firearm; additional penalty
    "14:64.4": True,    # (35) Second degree robbery
    "14:34.6": True,    # (36) Disarming of a peace officer
    "14:40.2": True,    # (37) Stalking
    "14:93.2.3": True,  # (38) Second degree cruelty to juveniles
    "14:108.1": "Is it aggravated flight from an officer (R.S. 14:108.1(C))? Simple flight is not listed.",  # (39)
    "14:93.5": True,    # (40) Sexual battery of persons with infirmities
    "14:34.2": True,    # (41) Battery of a police officer
    "14:46.3": True,    # (42) Trafficking of children for sexual purposes
    "14:46.2": True,    # (43) Human trafficking
    "14:62.8": True,    # (44) Home invasion
    "14:37.7": True,    # (45) Domestic abuse aggravated assault
    "14:32.1": "Was the driver's BAC over 0.20? (R.S. 14:2(B)(46))",                      # (46)
    "14:34.9.1": True,  # (47) Aggravated assault upon a dating partner
    "14:35.3": "Is it punishable under R.S. 14:35.3(L), (M)(2), (N), (O) or (P)? (R.S. 14:2(B)(48))",  # (48)
    "14:34.9": "Is it punishable under R.S. 14:34.9(L), (M)(2), (N), (O) or (P)? (R.S. 14:2(B)(49))",  # (49)
    "14:79": "Is it punishable under R.S. 14:79(C)? (R.S. 14:2(B)(50))",                   # (50)
    "14:87.7": True,    # (51) Criminal abortion (now captioned "Abortion")
    "14:32.6": True,    # (52) First degree feticide
    "14:32.7": True,    # (53) Second degree feticide
    "14:32.8": True,    # (54) Third degree feticide
    "14:87.11": True,   # (55) Aggravated abortion by dismemberment
    "14:34.8": True,    # (56) Battery of emergency room personnel, EMS or healthcare professional
    "14:95.1": "Is it a violation of R.S. 14:95.1(D)? (R.S. 14:2(B)(57))",                 # (57)
    "40:967": "Is it distribution of fentanyl or carfentanil punishable under R.S. 40:967(B)(4)(f)? (R.S. 14:2(B)(58))",  # (58)
    "40:966": "Is it distribution of heroin punishable under R.S. 40:966(B)(3)(b)? (R.S. 14:2(B)(59))",  # (59)
    "14:62.2": "Was a person present in the dwelling? (R.S. 14:2(B)(60))",                 # (60)
    "14:94": True,      # (61) Illegal use of weapons or dangerous instrumentalities
    "14:39.2": "Was the driver's BAC over 0.20? (R.S. 14:2(B)(62))",                       # (62)
    "14:93.3.1": True,  # (63) Second degree cruelty to the elderly and persons with infirmities
}

# ---------------------------------------------------------------------------
# R.S. 15:541(24) "sex offense" (vault text retrieved 2026-10-15).
# Attempts and conspiracies are included by the definition itself.
# ---------------------------------------------------------------------------
SEX = {
    "14:46.2": "Was it prosecuted under R.S. 14:46.2(B)(2) (sexual trafficking)? (R.S. 15:541(24)(a))",
    "14:46.3": True,
    "14:73.13": "Is it under R.S. 14:73.13(A) or (B)(2)? (R.S. 15:541(24)(a))",
    "14:89": True,
    "14:89.1": True,
    "14:89.2": "Is it under R.S. 14:89.2(B)(3)? (R.S. 15:541(24)(a))",
    "14:80": True,
    "14:81": True,
    "14:81.1": True,   # before 8/1/2025 under (24)(a); on or after under (24)(c)
    "14:81.2": True,
    "14:81.3": True,
    "14:81.4": True,
    "14:82.1": True,
    "14:82.2": "Is it under R.S. 14:82.2(C)(2), (4) or (5)? (R.S. 15:541(24)(a))",
    "14:83": "Is it under R.S. 14:83(B)(2) or (3)? (R.S. 15:541(24)(a))",
    "14:92": "Is it under R.S. 14:92(A)(7)? (R.S. 15:541(24)(a))",
    "14:93.5": True,
    "14:106": "Is it under R.S. 14:106(A)(5) (solicitation of a person under 17)? (R.S. 15:541(24)(a))",
    "14:283": "Is it under R.S. 14:283(A)(1), (2) or (3)? (R.S. 15:541(24)(a))",
    "14:41": True,
    "14:42": True,
    "14:42.1": True,
    "14:43": True,
    "14:43.1": True,
    "14:43.2": True,
    "14:43.5": True,
    "14:283.1": "Is this a second or subsequent voyeurism conviction? (R.S. 15:541(24)(a))",
    "14:406": True,
    "14:89.3": "Is this a second or subsequent conviction? (R.S. 15:541(24)(a))",
}

# Extra notes shown when the offense is picked.
NOTES = {
    "14:43.1.1": "R.S. 14:43.1.1(D): not subject to sex-offender laws. Misdemeanor (6 months max).",
    "14:43.1": "Both a sex offense and a crime of violence: no good time, no program credit.",
    "14:81.1": "Sex offense under R.S. 15:541(24)(a) before 8/1/2025 and (24)(c) on or after.",
    "14:98": "Penalties are in R.S. 14:98.1 to 14:98.4. Third and fourth offenses are felonies; set the grade by hand.",
}


def front_matter(text):
    """Return the YAML front matter as a dict of simple key: "value" pairs."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    out = {}
    if m:
        for line in m.group(1).splitlines():
            kv = re.match(r'^([a-z_]+):\s*"?(.*?)"?\s*$', line)
            if kv:
                out[kv.group(1)] = kv.group(2)
    return out, text[m.end():] if m else text


def sort_key(sec):
    title, rest = sec.split(":")
    return [int(title)] + [int(p) for p in rest.split(".") if p.isdigit()]


def main():
    rows = []
    for folder in FOLDERS:
        for f in folder.glob("RS *.md"):
            if "Index" in f.name or "Manifest" in f.name:
                continue
            fm, body = front_matter(f.read_text(encoding="utf-8"))
            cite = fm.get("citation", "").replace("La. R.S. ", "")
            head = fm.get("section_heading", "")
            if not cite or fm.get("status") == "repealed":
                continue
            if head.lower().startswith(("repealed", "redesignated")):
                continue
            # Only the statute text, not the history line, for the hard-labor hint.
            statute_text = body.split("### Source and history")[0].lower()
            # Penalty sentences = sentences that mention imprisonment.
            # hl 2: every one mentions hard labor (felony grade throughout)
            # hl 1: only some do (grade depends on the subsection)
            # hl 0: none do (misdemeanor penalties only, or no penalty)
            pen = [p for p in re.split(r"(?<=[.;])\s+", statute_text) if "imprison" in p]
            hard = [p for p in pen if "hard labor" in p]
            hl = 2 if pen and len(hard) == len(pen) else (1 if hard else 0)
            row = {"s": cite, "n": head, "hl": hl}
            if cite in COV:
                row["cov"] = COV[cite]
            if cite in SEX:
                row["sex"] = SEX[cite]
            if cite in NOTES:
                row["note"] = NOTES[cite]
            rows.append(row)
    rows.sort(key=lambda r: sort_key(r["s"]))

    # Every table entry must match a real, active section, or the tables are stale.
    have = {r["s"] for r in rows}
    missing = sorted((set(COV) | set(SEX) | set(NOTES)) - have, key=sort_key)
    if missing:
        print("WARNING: table entries not found as active sections:", ", ".join(missing))

    data = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    html = APP.read_text(encoding="utf-8")
    start, end = "/* OFFENSES-START */", "/* OFFENSES-END */"
    if start not in html or end not in html:
        sys.exit("index.html is missing the OFFENSES markers")
    before, rest = html.split(start, 1)
    _, after = rest.split(end, 1)
    APP.write_text(before + start + "\nconst OFFENSES = " + data + ";\n" + end + after, encoding="utf-8")
    print(f"Wrote {len(rows)} offenses into {APP.name} "
          f"({sum(1 for r in rows if 'cov' in r)} crime-of-violence tags, "
          f"{sum(1 for r in rows if 'sex' in r)} sex-offense tags).")


if __name__ == "__main__":
    main()
