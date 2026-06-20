#!/usr/bin/env python3
"""Extract compact, honest JSON from DEMIG VISA for the border-friction tool.
Direction: a row = (dest=visa issuer col2, origin=traveller nationality col6).
'Can origin X enter dest Y' lives where origin==X, dest==Y.
Values: 0=no visa, 1=visa required, 2=no admission, blank=no data.
We NEVER silently fill blanks; we record counts so the UI can show gaps honestly.
"""
import openpyxl, json, statistics as st, os
from collections import defaultdict

OUT = "/tmp/bf-build"
os.makedirs(OUT, exist_ok=True)
wb = openpyxl.load_workbook(OUT + "/../demig_visa_full.xlsx", read_only=True, data_only=True)
ws = wb["DEMIG VISA"]; rows = ws.iter_rows(values_only=True)
next(rows); hdr = next(rows)

DEST_ISO, ORI_ISO, PM = 2, 6, 7
ycols = {}
for i, v in enumerate(hdr):
    s = str(v).strip() if v is not None else ""
    if s.isdigit() and len(s) == 4 and 1973 <= int(s) <= 2013:
        ycols[int(s)] = i
YEARS = sorted(ycols)               # 1973..2013
YIDX = {y: k for k, y in enumerate(YEARS)}
NY = len(YEARS)

def nm(v):
    if v is None: return None
    s = str(v).strip()
    return s if s else None

names = {}          # iso3 -> display name (prefer dest-name spelling)
# per (origin,dest) visa series, list length NY of 0/1/2/None
series = {}         # (ori,dest) -> [vals]
for row in rows:
    pm = nm(row[PM])
    if not pm or not pm.lower().startswith("visa"):  # VISA measure only (exit-permit handled separately later)
        continue
    dest = nm(row[DEST_ISO]); ori = nm(row[ORI_ISO])
    if not dest or not ori:
        continue
    names.setdefault(dest, nm(row[0]))
    names.setdefault(ori, nm(row[3]))
    arr = [None] * NY
    for y, ci in ycols.items():
        val = nm(row[ci]) if ci < len(row) else None
        if val in ("0", "1", "2"):
            arr[YIDX[y]] = int(val)
    series[(ori, dest)] = arr
wb.close()

ISOS = sorted(names)
print(f"entities: {len(ISOS)}  dyads: {len(series)}  years: {YEARS[0]}-{YEARS[-1]} ({NY})")

# ---- country-level metrics per year ----
# passportPower[ori][yi] = % of dests visa-free (val==0) among dests with data
# destOpenness[dest][yi] = % of origins visa-free among origins with data
pp_free = defaultdict(lambda: [0]*NY); pp_n = defaultdict(lambda: [0]*NY)
do_free = defaultdict(lambda: [0]*NY); do_n = defaultdict(lambda: [0]*NY)
visareq = [0]*NY; filled = [0]*NY     # global: dyads requiring visa / filled
for (ori, dest), arr in series.items():
    if ori == dest:
        continue
    for yi, v in enumerate(arr):
        if v is None:
            continue
        filled[yi] += 1
        if v in (1, 2):
            visareq[yi] += 1
        free = 1 if v == 0 else 0
        pp_free[ori][yi] += free; pp_n[ori][yi] += 1
        do_free[dest][yi] += free; do_n[dest][yi] += 1

def pct_series(free, n):
    return [round(100*free[i]/n[i]) if n[i] else None for i in range(NY)]

countries = {}
for iso in ISOS:
    power = pct_series(pp_free[iso], pp_n[iso])
    openn = pct_series(do_free[iso], do_n[iso])
    if all(x is None for x in power) and all(x is None for x in openn):
        continue
    countries[iso] = {
        "name": names[iso],
        "power": power, "pN": pp_n[iso],     # passport power + sample size
        "open": openn, "oN": do_n[iso],      # destination openness + sample size
    }

# ---- global trend: mean & sd of passport power across origins with >=20 dests ----
power_mean = []; power_sd = []; pct_visa = []; n_orig = []
for yi in range(NY):
    vals = [100*pp_free[o][yi]/pp_n[o][yi] for o in ISOS if pp_n[o][yi] >= 20]
    power_mean.append(round(st.mean(vals), 1) if vals else None)
    power_sd.append(round(st.pstdev(vals), 1) if len(vals) > 1 else None)
    n_orig.append(len(vals))
    pct_visa.append(round(100*visareq[yi]/filled[yi], 1) if filled[yi] else None)

glob = {"years": YEARS, "powerMean": power_mean, "powerSd": power_sd,
        "pctVisaReq": pct_visa, "nOrigins": n_orig}

# ---- verdict numbers: fixed-nationality panel divergence (1973 vs 2013) ----
def power_on_common(ori):
    pairs = [(s[YIDX[1973]], s[YIDX[2013]]) for (o, d), s in series.items()
             if o == ori and o != d
             and s[YIDX[1973]] in (0,1,2) and s[YIDX[2013]] in (0,1,2)]
    if len(pairs) < 20:
        return None
    f73 = sum(1 for a, b in pairs if a == 0)/len(pairs)*100
    f13 = sum(1 for a, b in pairs if b == 0)/len(pairs)*100
    return f73, f13, len(pairs)
panel = {}
for iso in ISOS:
    r = power_on_common(iso)
    if r:
        panel[iso] = r
p73 = [v[0] for v in panel.values()]; p13 = [v[1] for v in panel.values()]
deltas = sorted(((round(v[1]-v[0]), iso) for iso, v in panel.items()))
verdict = {
    "panelN": len(panel),
    "mean73": round(st.mean(p73), 1), "mean13": round(st.mean(p13), 1),
    "sd73": round(st.pstdev(p73), 1), "sd13": round(st.pstdev(p13), 1),
    "gained": sum(1 for d, _ in deltas if d > 2),
    "lost": sum(1 for d, _ in deltas if d < -2),
    "flat": sum(1 for d, _ in deltas if -2 <= d <= 2),
    "losers": [{"iso": i, "name": names.get(i, i), "d": d} for d, i in deltas[:8]],
    "winners": [{"iso": i, "name": names.get(i, i), "d": d} for d, i in deltas[-8:]][::-1],
    # fixed dyad panel (composition-controlled visa-required share)
}
# fixed dyad panel
both = [0, 0, 0]
for (o, d), s in series.items():
    if o == d: continue
    a, b = s[YIDX[1973]], s[YIDX[2013]]
    if a in (0,1) and b in (0,1):
        both[0]+=1; both[1]+= (a==1); both[2]+= (b==1)
verdict["dyadPanelN"] = both[0]
verdict["dyadReq73"] = round(100*both[1]/both[0], 1)
verdict["dyadReq13"] = round(100*both[2]/both[0], 1)

# ---- pairs: transition-encoded for corridor mode (v: 0/1/2, -1 = no data) ----
def encode(arr):
    out = []; prev = object()
    for yi, v in enumerate(arr):
        cur = v if v is not None else -1
        if cur != prev:
            out.append([yi, cur]); prev = cur
    return out
pairs = defaultdict(dict)
for (ori, dest), arr in series.items():
    if ori == dest:
        continue
    if all(v is None for v in arr):
        continue
    enc = encode(arr)
    # skip pairs that are a single constant -1 (all no-data) -- already excluded
    pairs[ori][dest] = enc

# ---- write ----
def dump(name, obj):
    p = f"{OUT}/{name}"
    with open(p, "w") as f:
        json.dump(obj, f, separators=(",", ":"))
    return os.path.getsize(p)

s1 = dump("countries.json", countries)
s2 = dump("global.json", glob)
s3 = dump("verdict.json", verdict)
s4 = dump("pairs.json", pairs)
s5 = dump("iso3_names.json", names)
print(f"countries.json {s1//1024}KB  global.json {s2}B  verdict.json {s3}B  pairs.json {s4//1024}KB  names {s5//1024}KB")
print("\nVERDICT:", json.dumps({k: verdict[k] for k in ("panelN","mean73","mean13","sd73","sd13","gained","lost","flat","dyadPanelN","dyadReq73","dyadReq13")}, indent=0))
print("LOSERS:", [(x["name"], x["d"]) for x in verdict["losers"]])
print("WINNERS:", [(x["name"], x["d"]) for x in verdict["winners"]])
print("countries with data:", len(countries))
