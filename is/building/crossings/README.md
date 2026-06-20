# Crossings

An interactive record of the world's bilateral visa requirements over time. Hold a passport and watch where it could go across forty years; trace a corridor between two countries; or watch the whole world at once. The finding: the global average barely moved, while the gap between passports widened.

Live: `ajin.im/is/building/crossings/`

## Do not edit `index.html`

`index.html` is generated. Edit `_template.html`, then:

```
python3 build.py
```

`build.py` inlines the world map and the data (the JSON files in this dir) into the template and writes `index.html`. The file carries a `<!-- generated ... -->` header as a reminder.

## Data sources

- **History (1973–2013):** DEMIG VISA database, version 1.4 Full Edition (Oxford International Migration Institute, 2015). Bilateral visa requirements, annual January snapshots. The Institute's own download link is dead (SurfDrive was decommissioned); the file was recovered from the Internet Archive:
  `https://web.archive.org/web/20230512174053id_/https://surfdrive.surf.nl/files/index.php/s/UPKvWmR3j34ts3c/download`
  `extract.py` reads that workbook (`demig_visa_full.xlsx`, not committed — 27 MB) and writes `countries.json`, `pairs.json`, `global.json`, `verdict.json`.
- **Present day (2019–2025):** Passport Index dataset (github.com/ilyankou/passport-index-dataset, MIT), five snapshots collapsed onto a comparable open/mid/closed scale → `today.json`. It counts a broader set of arrivals as open (visa-on-arrival, visa-free day-counts), so its levels run higher than DEMIG; it is shown as a separate series, never spliced onto the older line.
- **Map outlines:** `world-map-country-shapes` by Luca Lischetti (github.com/sirLisko/world-map-country-shapes, MIT), based on simplemaps.com. ISO2 ids joined to ISO3 via `mapid_to_iso3.json`.

## The honesty rules baked in

- The deep record (DEMIG) stops in 2013; the present-day record starts in 2019. The **2014–2018 gap is left empty**, not bridged.
- The two sources use different rulers, so their levels are not comparable. The seam is marked loudly and the divergence-fan chart is DEMIG-only, capped at 2013.
- Where the record has no entry for a country-year, it renders as hatch (no data), never a guessed value. Sample sizes under 8 are suppressed.
- Former states (USSR, Yugoslavia, Czechoslovakia, the two Germanys, the two Yemens) are selectable as passports but absent from the modern map.
