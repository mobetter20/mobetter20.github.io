#!/usr/bin/env python3
"""
build_data.py — Joseon civil-service examination (문과) roster pipeline.

Reads _raw/munkwa.xml (the Academy of Korean Studies 조선조문과급제자 dataset,
data.go.kr 15052752) and emits data.json consumed by the static app in this dir.

The XML quirk: every record element is <급제자>, and it contains a CHILD also
tagged <급제자> that holds the passer's name. We read the record's direct child
<급제자> for the name.

Run: python3 build_data.py
"""

import json
import re
import statistics
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "_raw" / "munkwa.xml"
OUT = HERE / "data.json"

GENERATED = "2026-06-06"
SOURCE = ("한국학중앙연구원 (Academy of Korean Studies), 조선조문과급제자, "
          "data.go.kr dataset 15052752")

# Compound (2-character) Korean surnames: take two chars for the surname.
COMPOUND_SURNAMES = {"남궁", "황보", "선우", "독고", "제갈", "사공", "서문", "동방"}

# Honorific markers found inside the 등위 bracket -> our key.
HONORIFIC = {"壯元": "jangwon", "亞元": "aweon", "探花郞": "tamhwarang"}


# ---------------------------------------------------------------------------
# Field helpers
# ---------------------------------------------------------------------------

def hangul(s):
    """Part before the first '(' . e.g. '증광시(增廣試)' -> '증광시'."""
    if not s:
        return ""
    return s.split("(", 1)[0].strip()


def hanja(s):
    """Part inside the OUTER parens (may itself contain [...]).
    '남양(南陽[唐])' -> '南陽[唐]'; '장흥(長興)' -> '長興'."""
    if not s:
        return ""
    i = s.find("(")
    if i < 0:
        return ""
    j = s.rfind(")")
    inner = s[i + 1:j] if j > i else s[i + 1:]
    return inner.strip()


_BRACKET = re.compile(r"\[[^\]]*\]\s*$")


def strip_bracket(s):
    """Strip a trailing [...] annotation. '南陽[唐]' -> '南陽'; '남양' -> '남양'."""
    return _BRACKET.sub("", s).strip()


def surname_of(hangul_name):
    """First char of the Hangul name, or two for a compound surname."""
    if not hangul_name:
        return ""
    if hangul_name[:2] in COMPOUND_SURNAMES:
        return hangul_name[:2]
    return hangul_name[:1]


def as_year(s):
    """int when the value is a 4-digit number, else None (e.g. '미상')."""
    s = (s or "").strip()
    return int(s) if re.fullmatch(r"\d{4}", s) else None


_RANK_NUM = re.compile(r"^\s*(\d+)")
_RANK_BRACKET = re.compile(r"\[([^\]]*)\]")


def parse_rank(deungwi):
    """From 등위 like '6', '1[壯元]', '2[探花郞]' -> (numeric_rank|None, honorific|None).
    The honorific is taken from the bracket regardless of the numeric value
    (the data carries e.g. '2[亞元]' and '1[探花郞]')."""
    deungwi = (deungwi or "").strip()
    rank = None
    m = _RANK_NUM.match(deungwi)
    if m:
        rank = int(m.group(1))
    hon = None
    b = _RANK_BRACKET.search(deungwi)
    if b:
        hon = HONORIFIC.get(b.group(1).strip())
    return rank, hon


def split_name(raw_name):
    """Nested <급제자> child -> (hangul, hanja)."""
    return hangul(raw_name), hanja(raw_name)


# ---------------------------------------------------------------------------
# Exam-type normalization (시험유형 = '{정기시|비정기시|비정기 중시}：{type}(漢字)')
# We need the regular-vs-irregular class for each sitting. Fold 중시 sittings
# into 비정기시 so the badge is a clean binary 정기시 / 비정기시.
# ---------------------------------------------------------------------------

def exam_class(siheom_yuhyeong):
    s = siheom_yuhyeong or ""
    head = s.split("：", 1)[0].strip()  # U+FF1A full-width colon
    return "정기시" if head.startswith("정기시") else "비정기시"


# ---------------------------------------------------------------------------
# Parse
# ---------------------------------------------------------------------------

def parse_records():
    root = ET.fromstring(SRC.read_text(encoding="utf-8"))
    out = []
    for rec in root.findall("급제자"):
        get = lambda tag: (rec.findtext(tag) or "").strip()
        name_raw = (rec.find("급제자").text or "").strip()  # nested name child
        n_hg, n_hj = split_name(name_raw)
        sn = surname_of(n_hg)

        seat_raw = get("본관")
        seat_hg_full = hangul(seat_raw)          # base before '('
        seat_base = strip_bracket(seat_hg_full)  # also drop any trailing [...]
        seat_hj = hanja(seat_raw)                # full Hanja, keep bracket
        # 미상 (unknown) seat -> no clan identity
        seat_known = seat_base and seat_base != "미상"
        seonggwan = f"{sn} {seat_base}" if (sn and seat_known) else None

        rank, hon = parse_rank(get("등위"))
        jangwon = "壯元" in get("등위")

        year = as_year(get("시험년"))
        birth = as_year(get("생년"))
        death = as_year(get("졸년"))
        age = None
        if year is not None and birth is not None:
            a = year - birth
            if 0 < a < 95:
                age = a

        resid = hangul(get("거주지"))
        if resid == "미상":
            resid = None

        out.append({
            "id": get("ID"),
            "name": n_hg,
            "nameH": n_hj,
            "surname": sn,
            "seat": seat_base,            # base-seat Hangul ('' if 미상/empty)
            "seatH": seat_hj,             # full seat Hanja (with bracket)
            "seonggwan": seonggwan,       # clan key or None
            "resid": resid,
            "grade": hangul(get("등급")),  # base grade Hangul ('' if empty)
            "rank": rank,
            "hon": hon,
            "year": year,
            "exam": hangul(get("시험명")),  # base exam-name Hangul
            "examFull": get("시험명"),
            "birth": birth,
            "death": death,
            "age": age,
            "king": hangul(get("왕대")),
            "jangwon": jangwon,
            "siho": hangul(get("시호")),
            "ho": hangul(get("호")),
            "ja": hangul(get("자")),
            "cls": exam_class(get("시험유형")),  # 정기시 / 비정기시
        })
    return out


# ---------------------------------------------------------------------------
# Aggregations
# ---------------------------------------------------------------------------

def pct(n, d, places=1):
    return round(100.0 * n / d, places) if d else 0.0


def build():
    recs = parse_records()
    total = len(recs)

    years = [r["year"] for r in recs if r["year"] is not None]
    year_min, year_max = min(years), max(years)

    # --- sittings: distinct (year, exam-base) ---
    sitting_keys = sorted(
        {(r["year"], r["exam"]) for r in recs if r["year"] is not None}
    )
    sittings = len(sitting_keys)

    # --- seats & seonggwan distinct ---
    # distinctSeats counts seat values at full-Hanja granularity (so 안동[舊]
    # and 안동[新] are distinct), and the 미상/未詳 (unknown) bucket counts as
    # one. This is a finer notion than the base-Hangul seat rollup used for
    # feedersBySeat / concentration, which intentionally folds those.
    distinct_seats = len({r["seatH"] for r in recs if r["seatH"]})
    distinct_seonggwan = len({r["seonggwan"] for r in recs if r["seonggwan"]})

    # --- ages ---
    ages = sorted(r["age"] for r in recs if r["age"] is not None)
    age_n = len(ages)
    median_age = int(statistics.median(ages))  # integer per spec example (34)

    meta = {
        "total": total,
        "sittings": sittings,
        "yearMin": year_min,
        "yearMax": year_max,
        "distinctSeats": distinct_seats,
        "distinctSeonggwan": distinct_seonggwan,
        "medianAge": median_age,
        "ageN": age_n,
        "source": SOURCE,
        "generated": GENERATED,
    }

    # --- feeders (by 성관) ---
    sg_n = Counter()
    sg_first = {}
    sg_last = {}
    sg_jw = Counter()
    sg_meta = {}  # key -> (sn, seat, seatH)
    total_with_clan = 0
    for r in recs:
        k = r["seonggwan"]
        if not k:
            continue
        total_with_clan += 1
        sg_n[k] += 1
        if r["jangwon"]:
            sg_jw[k] += 1
        if r["year"] is not None:
            sg_first[k] = min(sg_first.get(k, r["year"]), r["year"])
            sg_last[k] = max(sg_last.get(k, r["year"]), r["year"])
        if k not in sg_meta:
            sg_meta[k] = (r["surname"], r["seat"], r["seatH"])

    feeders_sorted = sorted(sg_n.items(), key=lambda kv: (-kv[1], kv[0]))
    feeders = []
    for i, (k, n) in enumerate(feeders_sorted, 1):
        sn, seat, seatH = sg_meta[k]
        rec = {
            "rank": i,
            "key": k,
            "sn": sn,
            "seat": seat,
            "seatH": seatH,
            "n": n,
            "pct": pct(n, total),  # feeders pct is of TOTAL passers
            "jangwon": sg_jw.get(k, 0),
        }
        if k in sg_first:
            rec["firstYear"] = sg_first[k]
            rec["lastYear"] = sg_last[k]
        feeders.append(rec)

    # --- concentration by 성관 (percent of total-with-clan) ---
    sg_counts_desc = [n for _, n in feeders_sorted]

    def topshare(counts, k):
        return pct(sum(counts[:k]), total_with_clan)

    conc_sg = {f"top{k}": topshare(sg_counts_desc, k)
               for k in (5, 10, 20, 50, 100)}

    # --- by SEAT (본관 base, ignoring surname) ---
    seat_n = Counter()
    seat_hj = {}
    seat_first = {}
    seat_last = {}
    total_with_seat = 0
    for r in recs:
        s = r["seat"]
        if not s or s == "미상":
            continue
        total_with_seat += 1
        seat_n[s] += 1
        seat_hj.setdefault(s, strip_bracket(r["seatH"]))
        if r["year"] is not None:
            seat_first[s] = min(seat_first.get(s, r["year"]), r["year"])
            seat_last[s] = max(seat_last.get(s, r["year"]), r["year"])

    seat_sorted = sorted(seat_n.items(), key=lambda kv: (-kv[1], kv[0]))
    seat_counts_desc = [n for _, n in seat_sorted]
    conc_seat = {f"top{k}": pct(sum(seat_counts_desc[:k]), total_with_seat)
                 for k in (5, 10, 20, 50, 100)}

    feeders_by_seat = []
    for i, (s, n) in enumerate(seat_sorted[:60], 1):
        feeders_by_seat.append({
            "rank": i,
            "seat": s,
            "seatH": seat_hj.get(s, ""),
            "n": n,
            "pct": pct(n, total),  # of TOTAL passers
        })

    concentration = {"bySeonggwan": conc_sg, "bySeat": conc_seat}

    # --- class by year & by 25-year period ---
    by_year = Counter(r["year"] for r in recs if r["year"] is not None)
    class_by_year = [{"y": y, "n": by_year[y]} for y in sorted(by_year)]

    period_start = 1375  # 25-year buckets covering 1375..1899
    period_n = Counter()
    for y in years:
        bucket = period_start + ((y - period_start) // 25) * 25
        period_n[bucket] += 1
    class_by_period = [{"start": s, "n": period_n.get(s, 0)}
                       for s in range(1375, 1900, 25)]

    # --- exam types (by 시험명 base) ---
    et_n = Counter(r["exam"] for r in recs if r["exam"])
    examTypes = [{"name": name, "n": n, "pct": pct(n, total)}
                 for name, n in sorted(et_n.items(),
                                       key=lambda kv: (-kv[1], kv[0]))]

    # --- grades (by 등급 base; skip empty) ---
    g_n = Counter(r["grade"] for r in recs if r["grade"])
    grades = [{"g": g, "n": n}
              for g, n in sorted(g_n.items(), key=lambda kv: (-kv[1], kv[0]))]

    # --- age distribution ---
    if ages:
        ageDist = {
            "min": ages[0],
            "p25": int(statistics.quantiles(ages, n=4, method="inclusive")[0]),
            "median": median_age,
            "mean": round(statistics.mean(ages), 1),
            "p75": int(statistics.quantiles(ages, n=4, method="inclusive")[2]),
            "max": ages[-1],
        }
    else:
        ageDist = {"min": None, "p25": None, "median": None,
                   "mean": None, "p75": None, "max": None}
    age_hist = Counter(r["age"] for r in recs if r["age"] is not None)
    ageDist["hist"] = [{"age": a, "n": age_hist[a]}
                       for a in range(10, 86) if age_hist.get(a)]

    # --- kings (chronological by earliest 시험년 of that king's records) ---
    king_n = Counter()
    king_first = {}
    for r in recs:
        k = r["king"]
        if not k:
            continue
        king_n[k] += 1
        if r["year"] is not None:
            king_first[k] = min(king_first.get(k, r["year"]), r["year"])
    kings = [{"k": k, "n": king_n[k]}
             for k in sorted(king_n, key=lambda k: (king_first.get(k, 9999), k))]

    # --- cohorts (one per sitting) ---
    # Group records by (year, exam-base).
    groups = defaultdict(list)
    for r in recs:
        if r["year"] is None:
            continue
        groups[(r["year"], r["exam"])].append(r)

    cohorts = []
    id_seen = Counter()
    for (y, exam) in sitting_keys:
        members = groups[(y, exam)]
        base_id = f"{y}-{exam}"
        id_seen[base_id] += 1
        cid = base_id if id_seen[base_id] == 1 else f"{base_id}-{id_seen[base_id]}"

        # class (정기시/비정기시) & king: take the modal value of the group
        cls = Counter(m["cls"] for m in members).most_common(1)[0][0]
        king = Counter(m["king"] for m in members if m["king"]).most_common(1)
        king = king[0][0] if king else ""

        # 장원 of the sitting
        jw = None
        for m in members:
            if m["jangwon"]:
                jw = {"n": m["name"], "h": m["nameH"]}
                break

        # topFeeder = most-represented 성관 (null if empty, or if the top is a
        # unique tie at n=1, i.e. no clan is more represented than another)
        clan_n = Counter(m["seonggwan"] for m in members if m["seonggwan"])
        top_feeder = None
        if clan_n:
            ranked = clan_n.most_common()
            top_key, top_count = ranked[0]
            tied = [k for k, c in ranked if c == top_count]
            if not (top_count == 1 and len(tied) > 1):
                top_feeder = top_key

        # grade breakdown (base grade -> count)
        gb = Counter(m["grade"] for m in members if m["grade"])
        grades_obj = {g: gb[g] for g in
                      sorted(gb, key=lambda g: (-gb[g], g))}

        cohorts.append({
            "id": cid,
            "y": y,
            "name": exam,
            "type": cls,
            "king": king,
            "n": len(members),
            "jw": jw,
            "topFeeder": top_feeder,
            "grades": grades_obj,
        })
    # sorted by year then name (sitting_keys already is)
    cohorts.sort(key=lambda c: (c["y"], c["name"]))

    # --- roster ---
    roster = []
    for idx, r in enumerate(recs):
        item = {"i": r["id"], "n": r["name"], "h": r["nameH"], "s": r["surname"]}
        if r["seat"]:
            item["b"] = r["seat"]
        if r["seatH"]:
            item["bh"] = r["seatH"]
        if r["seonggwan"]:
            item["bk"] = r["seonggwan"]
        if r["resid"]:
            item["r"] = r["resid"]
        if r["grade"]:
            item["g"] = r["grade"]
        if r["rank"] is not None:
            item["rk"] = r["rank"]
        if r["hon"]:
            item["hon"] = r["hon"]
        if r["year"] is not None:
            item["y"] = r["year"]
        if r["exam"]:
            item["e"] = r["exam"]
        if r["birth"] is not None:
            item["by"] = r["birth"]
        if r["age"] is not None:
            item["age"] = r["age"]
        if r["king"]:
            item["k"] = r["king"]
        if r["jangwon"]:
            item["z"] = 1
        if r["siho"]:
            item["sh"] = r["siho"]
        if r["ho"]:
            item["ho"] = r["ho"]
        if r["ja"]:
            item["ja"] = r["ja"]
        roster.append(item)

    data = {
        "meta": meta,
        "concentration": concentration,
        "feeders": feeders,
        "feedersBySeat": feeders_by_seat,
        "classByPeriod": class_by_period,
        "classByYear": class_by_year,
        "examTypes": examTypes,
        "grades": grades,
        "ageDist": ageDist,
        "kings": kings,
        "cohorts": cohorts,
        "roster": roster,
    }
    return data, total_with_clan


def main():
    data, total_with_clan = build()
    OUT.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    size = OUT.stat().st_size
    m = data["meta"]
    f0 = data["feeders"][0]
    et0 = data["examTypes"][0]
    jw_total = sum(1 for r in data["roster"] if r.get("z") == 1)
    print(f"WROTE {OUT}  ({size:,} bytes)")
    print(f"  total={m['total']} sittings={m['sittings']} "
          f"years={m['yearMin']}-{m['yearMax']} distinctSeats={m['distinctSeats']} "
          f"distinctSeonggwan={m['distinctSeonggwan']}")
    print(f"  medianAge={m['medianAge']} ageN={m['ageN']} "
          f"total_with_clan={total_with_clan}")
    print(f"  feeders[0]={f0['key']} n={f0['n']} pct={f0['pct']} jw={f0['jangwon']}")
    print(f"  feeders[1..4]=" +
          " / ".join(f"{x['key']} {x['n']}" for x in data["feeders"][1:5]))
    print(f"  examTypes[0]={et0['name']} {et0['n']} ({et0['pct']}%)")
    print(f"  jangwon roster total (sum z)={jw_total}")
    print(f"  cohorts={len(data['cohorts'])} kings={len(data['kings'])} "
          f"feeders={len(data['feeders'])}")


if __name__ == "__main__":
    main()
