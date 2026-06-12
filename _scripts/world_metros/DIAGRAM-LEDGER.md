# DIAGRAM-LEDGER — per-city familiar-diagram sourcing (D11 audit)

_Audited 2026-06-11 (Claude session). The audit D11 names as the first step of the
familiar-diagram layer: for each roster city (D3), the best freely-licensed schematic
network map in the city's own official visual idiom, its license verified on the actual
Commons file page (machine-readable page data + page wikitext checked for deletion
templates), and its **interactivity structure** verified by downloading the file and
counting label nodes. Nothing here edits BUILD-SPEC.md; D11 itself is still PROPOSED._

_Extended 2026-06-12 (gate-3 session): stanzas added for the four D23 newcomers
(Beijing, Madrid, Copenhagen, Guangzhou) under the same dual discipline: license
read from the Commons page data (API extmetadata + deletion-category check) and
structure graded by downloading the file and counting text nodes. The 2026-06-12
downloads also re-counted the nine previously audited files: every count matched
this ledger. All sixteen chosen files are now committed at
`is/building/world-metros/assets/<slug>-diagram.(svg|png)` and ride the card
lore backs._

## Structure grades (the criterion the interactivity spike added)

The spike (`mocks/diagram-interactive.html`) proved station-tap works only when labels
are real text nodes:

- **interactive-ready** — station labels are `<text>`/`<tspan>` elements; pan/zoom AND
  label-tap both work when embedded inline.
- **pan-zoom-only** — label text converted to outline paths (a print-export habit);
  viewBox pan/zoom works, no label is addressable. Station-tap would need a separate
  hit-target overlay built from our OSM station coordinates — possible, not free.
- **raster-only** — PNG/JPG; CSS-transform pan/zoom only.

A clean pattern emerged: the print-faithful recreations (Yveltal's Shanghai/Tokyo,
CountZ's NYC) ship outlined; the long-maintained "Wikipedia working maps" (sameboat
lineage HK/London/Moscow, Satellizer Seoul, Aforl Singapore, Rigil Paris) keep real text.

## License obligations (header note)

- **CC BY-SA files (most of the set): share-alike binds modified versions.** Embedding
  the unmodified SVG inline and driving it with page JS (the spike's approach — viewBox
  changes, style on tap) does **not** modify the work; the attribution line in the page
  chrome satisfies BY. If the build step ever **edits a file** (prune a language layer,
  recolor, crop), the modified SVG must itself stay CC BY-SA with credit intact —
  acceptable: this repo is public and the file ships openly. Keep any in-file credit
  blocks when editing.
- Per-city attribution strings below; render them in the Diagram-mode footer exactly as
  the spike does for Seoul.
- Paris is **CC BY** (no share-alike), Hong Kong is **public domain**, Cairo is **CC0** —
  lightest obligations in the set.

## Summary

| city | chosen file | license | structure | verdict |
|---|---|---|---|---|
| Shanghai | Shanghai Metro Linemap.svg | CC BY-SA 4.0 | pan-zoom-only (0 text) | use-with-caveat |
| Tokyo | Tokyo Subway Linemap en.svg | CC BY-SA 4.0 | pan-zoom-only (0 text) | use-with-caveat |
| Seoul | Seoul Metropolitan Subway network map.svg | CC BY-SA 4.0 | interactive-ready (1,847) | use |
| Hong Kong | Hong Kong Railway Route Map en.svg | public domain | interactive-ready (299) | use |
| Singapore | Singapore MRT and LRT System Map.svg | CC BY-SA 3.0 | interactive-ready (381) | use |
| Delhi | Delhi Metro Network 2020.svg | CC BY-SA 4.0 | interactive-ready (522) | use-with-caveat |
| Moscow | Moscow metro map sb.svg | CC BY-SA 4.0 | interactive-ready (2,535) | use |
| London | London Underground Overground DLR Crossrail map.svg | CC BY-SA 4.0 | interactive-ready (655) | use |
| Paris | Carte Métro de Paris.svg | CC BY 3.0 | interactive-ready (380) | use |
| New York | NYC subway-5.svg | CC BY-SA 3.0 | pan-zoom-only (35 text, bus notes only) | use-with-caveat |
| Mexico City | Plano del Metro de la Ciudad de México.svg | CC BY-SA 4.0 | pan-zoom-only (33 text, line nos.) | use-with-caveat |
| Cairo | CairoMetro.svg | CC0 | interactive-ready (151) | use |
| Beijing | Beijing Subway System Map.svg | CC BY-SA 4.0 | pan-zoom-only (0 text) | use |
| Madrid | Madrid Metro Map.svg | CC BY-SA 4.0 | pan-zoom-only (0 text) | use |
| Copenhagen | Copenhagen Metro 2024.svg | CC BY-SA 4.0 | interactive-ready (6,719) | use |
| Guangzhou | Guangzhou Metro Network.png | CC BY-SA 4.0 | raster-only (PNG 4200px) | use-with-caveat |

No city is at **no-good-option**. The caveats are interactivity (six pan-zoom-only,
one raster) and currency (Delhi, Mexico City).

## Official-artwork checks (D11 grade 1 — the rare permissive exceptions)

- **Seoul — KOGL, verified: Type 3 (attribution + no-derivatives).** Seoul Metro's own
  4-language map set is published on the open-data portal as KOGL 제3유형
  (출처표시 + 변경금지), JPG only, updated 2025-12-08
  (https://www.data.go.kr/data/15120713/fileData.do). Legal as an unmodified static
  image with attribution; raster + ND makes it useless as the interactive layer. The
  Commons recreation stays the pick.
- **Mexico City — LGACDMX exists, but does not clear the artwork.** The actual official
  map (Lance Wyman iconography) was uploaded to Commons 2026-05 as
  `File:STC Metro Mapa Iconográfico.svg` under CC BY-SA 4.0 + LGACDMX (Mexico City's
  open-government license). It carries an **active deletion nomination (2026-05-19)**:
  the iconography/typography is registered with the Mexican Institute of Industrial
  Property, and LGACDMX explicitly excludes third-party IP. Do **not** build on it.
  Caveat extends in principle to any recreation that faithfully reproduces the Wyman
  pictograms — see the Mexico City stanza.
- **Delhi — no open license found.** DMRC publishes a current official map
  (site PDF dated 2026-03-23) but no copyright/open-license policy page was locatable;
  GODL-India covers data.gov.in datasets, not DMRC artwork. Treat as © DMRC.
- **Everyone else: assumed copyrighted** per the verified TfL posture generalized in
  DATA-CONTRACT.md (idiom-not-artwork is the rule; these Commons recreations are the
  legal stand-ins).

---

## Per-city stanzas

### Shanghai — USE-WITH-CAVEAT
- **Chosen:** https://commons.wikimedia.org/wiki/File:Shanghai_Metro_Linemap.svg —
  SVG, 4.6 MB, 6134×3792, latest revision 2025-12-27 (actively maintained; ~10
  revisions 2022–2025).
- **Author / license:** Yveltal — CC BY-SA 4.0 (`{{self|cc-by-sa-4.0}}` on page; no
  deletion flags).
- **Attribution string:** “Shanghai Metro Linemap” by Yveltal, Wikimedia Commons, CC BY-SA 4.0.
- **Structure:** 0 `<text>` / 0 `<tspan>` / 13,496 paths → **pan-zoom-only** (all
  labels outlined).
- **Currency:** revision is dated two days after the Dec-2025 network additions and the
  author updates on openings; Airport Link Line (opened 2024-12-27, Hongqiao↔Pudong)
  falls inside the maintained window. Line 22 (ex-Chongming; trial ops expected
  end-2026 per Shanghai gov) correctly not yet open mid-2026. **Because the text is
  outlined, currency could not be grep-verified — needs one visual check at embed
  time** (look for 机场联络线 / Airport Link).
- **Fallback:** `File:Shanghai Metro and Suburban Railway plan nh2024.svg` (2024-09,
  12 MB — heavy, structure unverified) or the official-style PNG renders (raster-only).
- **Verdict:** use-with-caveat — best-in-class currency and idiom; no station tap.

### Tokyo — USE-WITH-CAVEAT
- **Chosen:** https://commons.wikimedia.org/wiki/File:Tokyo_Subway_Linemap_en.svg —
  SVG, 1.8 MB, 2952×2148, single revision 2020-06-27.
- **Author / license:** Yveltal — CC BY-SA 4.0 (no deletion flags).
- **Attribution string:** “Tokyo Subway Linemap” by Yveltal, Wikimedia Commons, CC BY-SA 4.0.
- **Structure:** 0 `<text>` / 0 `<tspan>` / 5,551 paths → **pan-zoom-only**.
- **Currency:** the network is the audit's most stable: no Tokyo Metro/Toei station has
  opened since Toranomon Hills (2020-06-06, three weeks before the file date; its
  presence needs the one visual check) and nothing new arrives before the 2030s
  (Haneda link, Yurakucho/Namboku extensions). A June-2020 map is effectively current
  for mid-2026. Sibling files: ja/zh/ru variants, same structure.
- **Fallback:** none current with real text — `File:TokyoSubway.svg` (PD, 2009) and
  `File:Tokyo subway map en jp.svg` (CC BY-SA 3.0, 2008, charmingly pre-outlined-era
  with clickable links) are 15+ years stale.
- **Verdict:** use-with-caveat — current and in the official bilingual idiom; no tap.

### Seoul — USE
- **Chosen:** https://commons.wikimedia.org/wiki/File:Seoul_Metropolitan_Subway_network_map.svg —
  SVG, 419 KB, latest revision 2023-09-09. The committed copy
  `mocks/assets/seoul-diagram.svg` (429,775 B) matches this revision.
- **Author / license:** Satellizer — CC BY-SA 4.0 (no deletion flags).
- **Attribution string:** “Seoul Metropolitan Subway network map” by Satellizer,
  Wikimedia Commons, CC BY-SA 4.0 (already rendered in the spike footer).
- **Structure:** 1,847 `<text>` + 2,369 `<tspan>` → **interactive-ready** (proven live:
  zoomTo/tap on Hongik University in the spike).
- **Currency:** base = Sep 2023, bilingual ko/en, future lines drawn with dated tags
  (“개장 2026 / Opening 2026”). vs mid-2026 reality: GTX-A's two operating segments
  (Suseo–Dongtan 2024-03; Unjeong-jungang–Seoul Stn 2024-12; gap link planned 2026,
  Samseong 2027-06) still appear as *planned*; Sinansan line drawn as future but its
  real opening slipped to 2028-12 after the Apr-2025 Gwangmyeong collapse; Dongbuk LRT
  drawn as future (correct — unopened mid-2026); GTX-B/C absent (correct). The 2026
  tags will read slightly optimistic on a 2026 site — a one-line “diagram dated 2023,
  future lines as then planned” note covers it.
- **Official-artwork check:** KOGL Type 3 (see header section) — static-only, not the pick.
- **Fallback:** official KOGL-3 JPG (static display with attribution only).
- **Verdict:** use — the file the whole D11 layer was proven on.

### Hong Kong — USE
- **Chosen:** https://commons.wikimedia.org/wiki/File:Hong_Kong_Railway_Route_Map_en.svg —
  SVG, 74 KB, 1557×1425, latest revision 2022-09-06.
- **Author / license:** Sameboat — **public domain** (`{{PD-user}}`; airport icon from a
  PD source; no deletion flags). No attribution required.
- **Attribution string (courtesy):** “Hong Kong Railway Route Map” by Sameboat,
  Wikimedia Commons, public domain.
- **Structure:** 299 `<text>` + 418 `<tspan>` → **interactive-ready**. Carries 197
  `systemLanguage` switch variants (multilingual labels incl. en/zh; browser picks by
  locale when embedded inline — pin the page's lang or prune at build if needed; note
  pruning = modification is unrestricted here, PD).
- **Currency:** fully current for mid-2026 — includes the 2021–22 additions verified in
  the file (Tuen Ma line complete, Sung Wong Toi/To Kwa Wan, East Rail cross-harbour to
  Exhibition Centre/Admiralty). Nothing new opens before Kwu Tung / Tung Chung East
  (2027+); no speculative future lines drawn.
- **Fallback:** zh/multi variants of the same family; `File:Hong Kong Railway Future
  Route Map en.svg` if a future-overlay is ever wanted.
- **Verdict:** use — the cleanest file in the set (PD + current + interactive).

### Singapore — USE
- **Chosen:** https://commons.wikimedia.org/wiki/File:Singapore_MRT_and_LRT_System_Map.svg —
  SVG, 44 KB, 1410×1007, latest revision 2026-01-12; in-file note “Correct as at
  15 June 2025”.
- **Author / license:** Aforl — CC BY-SA 3.0 (no deletion flags).
- **Attribution string:** “Singapore MRT and LRT System Map” by Aforl, Wikimedia
  Commons, CC BY-SA 3.0.
- **Structure:** 381 `<text>` + 404 `<tspan>` → **interactive-ready**. Official LTA
  System-Map idiom, quadrilingual title block.
- **Currency:** includes Hume (2025-02), Punggol Coast (2024-12), full TEL4; future
  JRL/CRL/TEL5 drawn with an explicit “alignment of future lines are speculative”
  disclaimer. vs mid-2026: nothing missing — TEL5/DTL3e (Bedok South/Sungei Bedok/Xilin)
  opens H2-2026 and is drawn as future; Founders' Memorial (2028) likewise.
- **Fallback:** the author's Korean-language sibling (CC **BY** 4.0, rev 2025-01) — a
  lighter license but non-English labels defeat “familiar”; or
  `File:Singapore MRT system Map multilingual.svg` (older base).
- **Verdict:** use.

### Delhi — USE-WITH-CAVEAT (weakest currency in the set)
- **Chosen:** https://commons.wikimedia.org/wiki/File:Delhi_Metro_Network_2020.svg —
  SVG, 143 KB, revision 2020-01-24.
- **Author / license:** AshuArtsNew — CC BY-SA 4.0 (no deletion flags).
- **Attribution string:** “Delhi Metro Network 2020” by AshuArtsNew, Wikimedia Commons,
  CC BY-SA 4.0.
- **Structure:** 522 `<text>` → **interactive-ready** structurally.
- **Currency: stale by four named openings.** Base Jan 2020 (full Phase 3, Grey line,
  Najafgarh; Dhansa Bus Stand drawn as then-future). Missing vs mid-2026: Airport
  Express ext to Yashobhoomi Dwarka Sec-25 (2023-09), Magenta Janakpuri West→Krishna
  Park ext (2025-01), Pink Majlis Park→Deepali Chowk section (2026-03-08); and the
  end-2026 wave (Magenta→RK Ashram, Golden Aerocity–Tughlakabad) will widen the gap.
  DMRC's official map (PDF dated 2026-03-23 on delhimetrorail.com) is current but
  © DMRC — no open license found (see header).
- **Fallback:** `File:Delhi metro rail network.svg` (PlaneMad, CC BY-SA 2.5, 2017 base —
  older still; its page requests the specific credit “CC-by-sa PlaneMad/Wikimedia”);
  `File:Rapid Transit Map of Delhi.jpg` (Chumwa, CC BY-SA 2.0, rev 2025-06) is current
  but raster + geographic-style, not the DMRC idiom.
- **Verdict:** use-with-caveat — ship with an explicit “network shown as of 2020;
  Phase-4 openings not yet drawn” label, or accept the idiom miss and show Chumwa's
  2025 geographic raster. Flagged as the roster's weakest diagram option.

### Moscow — USE
- **Chosen:** https://commons.wikimedia.org/wiki/File:Moscow_metro_map_sb.svg —
  SVG, 396 KB, 1320×1900, latest revision 2026-05-18 (the most current file in the set).
- **Author / license:** Sameboat (original), extended and maintained by IKhitron —
  CC BY-SA 4.0 (no deletion flags).
- **Attribution string:** “Moscow metro map” by Sameboat & IKhitron, Wikimedia Commons,
  CC BY-SA 4.0.
- **Structure:** 2,535 `<text>` + 2,511 `<tspan>` → **interactive-ready** (richest label
  set in the audit). Clean bilingual `systemLanguage` switch: 836 en + 836 ru label
  groups — pin/prune language at embed time (share-alike applies to a pruned copy).
- **Currency:** includes Troitskaya line Phase 1 complete (ZIL→Novomoskovskaya,
  finished Sept 2025), Potapovo, Vnukovo. Draws under-construction futures (Troitsk
  Phase 2, Rublyovo-Arkhangelskaya, Biryulyovskaya) — matching the official scheme's
  habit; Rublyovo-Arkhangelskaya's first section is planned for 2026 and is still
  future-correct mid-2026. Nothing missing.
- **Fallback:** `File:Moscow metro map sb draft.svg` (same family); the older
  ru-only sb files.
- **Verdict:** use.

### London — USE
- **Chosen:** https://commons.wikimedia.org/wiki/File:London_Underground_Overground_DLR_Crossrail_map.svg —
  SVG, 219 KB, 2500×1320, latest revision 2025-07-29.
- **Author / license:** Sameboat — CC BY-SA 4.0 (no deletion flags). (The D11 reference
  file — used across 100+ Wikipedia pages.)
- **Attribution string:** “London Underground Overground DLR Crossrail map” by
  Sameboat, Wikimedia Commons, CC BY-SA 4.0.
- **Structure:** 655 `<text>` + 232 `<tspan>` → **interactive-ready**. Includes fare-zone
  annotations (part of the tube-map idiom).
- **Currency:** fully current for mid-2026 — six named Overground lines post-Nov-2024
  renaming (Mildmay/Lioness/Windrush… verified in-file), Battersea Power
  Station/Nine Elms (2021), full Elizabeth line. No future-proposal clutter found
  (Thamesmead/Old Oak Common absent). Nothing opens before ~2030.
- **Note:** this is idiom-not-artwork in its strongest form — TfL's enforcement posture
  (DATA-CONTRACT) is exactly why the Commons recreation, not the official map, is the
  legal route to “the Tube map feeling”.
- **Fallback:** the same author's single-mode variants (Underground-only etc.).
- **Verdict:** use.

### Paris — USE
- **Chosen:** https://commons.wikimedia.org/wiki/File:Carte_M%C3%A9tro_de_Paris.svg —
  SVG, 819 KB, 2000×1397, latest revision 2024-07-11.
- **Author / license:** Rigil — **CC BY 3.0** (dual-licensed with GFDL; no share-alike
  obligation; no deletion flags).
- **Attribution string:** “Carte Métro de Paris” by Rigil, Wikimedia Commons, CC BY 3.0.
- **Structure:** 380 `<text>` + 452 `<tspan>` → **interactive-ready**.
- **Currency:** schematic in the RATP idiom — the file's own note says it is drawn
  “à partir des plans actuels de la RATP” (not geographic; RER appears only as
  interchange hints, matching the Métro-proper map). Includes the June-2024 openings
  (M14 Saint-Denis Pleyel + Orly, M11 ext incl. Serge Gainsbourg) and M4 Bagneux
  (2022). vs mid-2026: complete — Grand Paris Express Line 15 Sud slipped to Apr 2027
  (web-verified), so no Métro-map change lands before then.
- **Fallback:** `File:Paris Metro map.svg` (Pmx, public domain, but geographic-scale —
  wrong idiom for the familiar layer; rev 2022); `File:Paris Metro map complete.svg`
  (CC BY-SA 4.0, 2011 base — stale).
- **Verdict:** use — and the lightest CC attribution burden in the set.

### New York — USE-WITH-CAVEAT
- **Chosen:** https://commons.wikimedia.org/wiki/File:NYC_subway-5.svg —
  SVG, 2.1 MB, latest revision 2025-12-23, described by its uploader as “current as of
  December 2025”.
- **Author / license:** CountZ (Jake Berman), updated/uploaded by TFSyndicate —
  CC BY-SA 3.0 (no deletion flags). Berman's file page notes a link to his site is
  appreciated (not required).
- **Attribution string:** “NYC subway map” by CountZ (Jake Berman) & TFSyndicate,
  Wikimedia Commons, CC BY-SA 3.0.
- **Structure:** 35 `<text>` (bus-connection notes only; all station labels outlined
  among 10,584 paths) → **pan-zoom-only**.
- **Currency:** Dec 2025 = current through mid-2026 (no subway openings before SAS
  Phase 2, ~2029+). One curatorial wrinkle: this is the **Tauranac-lineage idiom** —
  the map New Yorkers knew for 45 years; the MTA's official map switched to the new
  2025 diagram, which has no free recreation yet. For “the familiar map”, the Tauranac
  form is arguably *more* familiar; note it on the city card.
- **Fallback:** `File:NYC subway-4D.svg` (same Tauranac lineage, 2022 state, also
  outlined). Worth a future look: `File:New_York_Subway_Map_Alargule.svg` (Alargule,
  CC BY-SA 3.0, rev 2025-12-08, 2.2 MB, schematic idiom) — a *current* schematic that,
  if its labels are real text, would upgrade NYC off pan-zoom-only; its structure was
  **not graded** here (Wikimedia upload CDN rate-limited the download during this audit),
  so it is recorded as an ungraded candidate, not a verified one.
- **Verdict:** use-with-caveat — current and deeply familiar; no station tap. (Re-grade
  the Alargule schematic when the CDN cooperates; it could promote NYC to a clean “use”.)

### Mexico City — USE-WITH-CAVEAT
- **Chosen:** https://commons.wikimedia.org/wiki/File:Plano_del_Metro_de_la_Ciudad_de_M%C3%A9xico.svg —
  SVG, 1.5 MB, 5631×5633, latest revision 2023-09-14 (“actualizado a los tramos con
  servicio”).
- **Author / license:** ManuelContreras1996 — CC BY-SA 4.0, claimed own work (no
  deletion flags; unlike the official upload, no LGACDMX dependency).
- **Attribution string:** “Plano del Metro de la Ciudad de México” by
  ManuelContreras1996, Wikimedia Commons, CC BY-SA 4.0.
- **Structure:** 33 `<text>` (line numbers only; station labels outlined among 2,481
  paths, 3 embedded raster images) → **pan-zoom-only**.
- **Currency:** drawn to in-service sections as of Sep 2023 — mid-renewal: Line 1's
  western half and parts of L12's elevated section were then closed, both fully back by
  2024–25 (L12 restored 2024-01; L1 fully reopened with Observatorio by late 2025).
  **Visual check required at embed time: if the file shows L1/L12 truncated, it
  misstates the 2026 network** and needs either the 2022 CC BY sibling or an on-card
  note.
- **Icon-IP caveat:** the STC idiom includes the Wyman station pictograms, registered
  with IMPI (see header). Any recreation that faithfully reproduces them carries the
  same residual exposure the official upload is being deleted over. Mitigation options:
  prefer label-zoom interactions over icon close-ups, or fall back to
  `File:Mapa del Metro de la Ciudad de México.svg` (CC BY 4.0 + LGACDMX-tagged,
  rev 2022) / `File:Map of the STC Metro of Mexico City (English).svg` (Fluence,
  CC BY 3.0, 2010 — stale but icon-light).
- **Verdict:** use-with-caveat — no tap, 2023 service-state, icon IP unresolved. After
  Delhi, the set's second-weakest option.

### Cairo — USE
- **Chosen:** https://commons.wikimedia.org/wiki/File:CairoMetro.svg —
  SVG, 265 KB, revision 2024-10-20.
- **Author / license:** Momooh — **CC0** (public-domain dedication; no deletion flags).
  No attribution required.
- **Attribution string (courtesy):** “Cairo Metro map” by Momooh, Wikimedia Commons, CC0.
- **Structure:** 151 `<text>` + 174 `<tspan>` / only 3 paths → **interactive-ready**
  (labels are real text; near-zero outlining). English single-language labels (no
  `systemLanguage` switch).
- **Currency:** base Oct 2024 — Lines 1–3 complete (incl. the 2024 L3 finale,
  Rod el-Farag / Kit Kat / Heliopolis area verified in-file), and Line 4 drawn and
  explicitly tagged “(Under Construction)” (Grand Egyptian Museum / El-Remaya /
  Al-Ahramat present) — correct for its 2028 horizon. The file draws **neither** the
  East Nile Monorail (public 2026-05-06) nor the Adly Mansour LRT (since 2022) — but
  our atlas scope **excludes LRT + monorail** (DATA-CONTRACT system scopes), so for the
  metro-proper network this is current and on-scope. The fidelity gap exists only if
  “familiar map” is later defined to include those modes.
- **Fallback:** `File:Cairo Metro map.png` (عبد المؤمن, CC BY-SA 4.0, rev 2025-08,
  5178×3778 — newest coverage incl. under-construction lines per its description, but
  raster-only → pan-zoom-only); `File:Cairo-metro-plans.svg` (ODbL, 2017 — stale, and
  ODbL is the wrong license family for artwork).
- **Verdict:** use — CC0, interactive-ready, current and on-scope for the metro proper.
  The only roster city whose best file is fully public-domain *and* tap-able.

### Beijing · USE (added 2026-06-12, D23 newcomer audit)
- **Chosen:** https://commons.wikimedia.org/wiki/File:Beijing_Subway_System_Map.svg :
  SVG, 6.26 MB (6,562,313 B), 2400x2400 canvas, latest revision 2026-05-15.
- **Author / license:** Painjet, own work. CC BY-SA 4.0 (verified 2026-06-12 via the
  file page's machine-readable data, extmetadata LicenseShortName plus the page
  wikitext license template; no deletion or dispute categories).
- **Attribution string:** "Beijing Subway System Map" by Painjet, Wikimedia Commons,
  CC BY-SA 4.0.
- **Structure:** 0 `<text>` / 0 `<tspan>` (counted on the downloaded file 2026-06-12):
  labels outlined, **pan-zoom-only**.
- **Currency:** maintained per opening. Revision comments record Line 3 and Line 12
  added 2024-12-14, Line 16 Lize Shangwuqu Jan 2025, Line 17 middle plus Line 18 plus
  Line 6 Luyang Dec 2025; last revised 2026-05-15. Current for mid-2026. English
  station labels; a zh companion file by the same author updates in lockstep.
- **Fallback:** `File:Beijing Subway System Map zh.svg` (same author and license,
  Chinese labels, revised in lockstep).
- **Verdict:** use. The en.wiki network diagram, fully current; no station tap.

### Madrid · USE (added 2026-06-12, D23 newcomer audit)
- **Chosen:** https://commons.wikimedia.org/wiki/File:Madrid_Metro_Map.svg :
  SVG, 2.28 MB (2,390,049 B), latest revision 2025-04-30.
- **Author / license:** Javitomad (original, 2007), maintained by Snooze123 and other
  Commons users. CC BY-SA 4.0, multi-licensed with older CC BY-SA versions and GFDL
  (verified 2026-06-12 via the file page's machine-readable data; no deletion flags).
  An en.wiki Featured Picture, used in the en and es article infoboxes.
- **Attribution string:** "Madrid Metro Map" by Javitomad and contributors, Wikimedia
  Commons, CC BY-SA 4.0.
- **Structure:** 0 `<text>` / 0 `<tspan>` (counted on the downloaded file 2026-06-12):
  labels outlined, **pan-zoom-only**.
- **Currency:** revision log tracks the network promptly (Line 3 to El Casar added
  2025-04-20). Nothing newer opened by mid-2026; current. Spanish labels, official
  line colours and numbering, the long-standing free recreation of the official plano.
- **Fallback:** `File:Madrid Metro Map inc ML-4.svg` (same idiom incl. Metro Ligero,
  CC BY-SA 4.0, frozen Oct 2018: dated); `File:Madrid Metro Map 2019-2023.svg`
  (projection map, draws planned extensions: wrong kind of map for a current card).
- **Verdict:** use. Current and canonical; no station tap.

### Copenhagen · USE (added 2026-06-12, D23 newcomer audit)
- **Chosen:** https://commons.wikimedia.org/wiki/File:Copenhagen_Metro_2024.svg :
  SVG, 3.46 MB (3,625,421 B), latest revision 2026-01-13.
- **Author / license:** Tomtom24, own work. CC BY-SA 4.0 (verified 2026-06-12 via the
  file page's machine-readable data plus wikitext; no deletion flags; the page carries
  only SVG-validator maintenance notes).
- **Attribution string:** "Copenhagen Metro 2024" by Tomtom24, Wikimedia Commons,
  CC BY-SA 4.0.
- **Structure:** 6,719 `<text>` + 7,079 `<tspan>` (counted on the downloaded file
  2026-06-12): **interactive-ready**, the richest label set in the ledger (embedded
  da/en `systemLanguage` switch translations).
- **Currency:** the M4 Sydhavn extension to Koebenhavn Syd was added 2024-06-22, its
  opening day; later revisions are label fixes. The metro network is unchanged since;
  current for mid-2026. Official line colours (M1 green, M2 yellow, M3 red, M4 blue);
  the standard diagram on en.wiki and da.wiki, own design rather than a copy of the
  Metroselskabet in-station map.
- **Fallback:** `File:Copenhagen Metro with City Circle Line map.svg` (closest to the
  official idiom, CC BY-SA 3.0, but pre-Sydhavn: dated 2019); `File:Copenhagen Metro
  2020.svg` (same family, historical 2020-2024 state by design).
- **Verdict:** use. Current, interactive-ready, clean license.

### Guangzhou · USE-WITH-CAVEAT (added 2026-06-12, D23 newcomer audit)
- **Chosen:** https://commons.wikimedia.org/wiki/File:Guangzhou_Metro_Network.png :
  PNG raster, 1.82 MB (1,913,352 B), 4200x4200 px, latest revision 2026-02-13.
- **Author / license:** Alan Fan Pei, own work. CC BY-SA 4.0 (verified 2026-06-12 via
  the file page's machine-readable data plus wikitext; no deletion flags).
- **Attribution string:** "Guangzhou Metro Network" by Alan Fan Pei, Wikimedia
  Commons, CC BY-SA 4.0.
- **Structure:** **raster-only** (PNG; pan-zoom via CSS transform only, no tap).
- **Currency:** maintained per opening with English revision comments: Line 11 loop
  (Dec 2024), the 2025 openings, Line 22 extension (Dec 2025), SYSU South Gate
  (Jan 2026), Chigang on Line 12 with the Line 8 interchange (Feb 2026). Current for
  mid-2026; the lead map on the en.wiki Guangzhou Metro article.
- **Why not the SVGs:** the only current SVG
  (`File:Guangzhou-Foshan Metro Diagram by Tim.svg`, rev 2026-05-06, CC BY-SA 4.0)
  carries an in-image author watermark (a Commons `{{watermark}}` maintenance flag)
  and a personal style with Guangfo-wide scope; the official-idiom SVG
  (`File:Guangzhou Metro Linemap.svg`, Yveltal family) is frozen at the 2023-01-01
  network state, roughly ten openings stale, and would contradict the card's own
  19 line pills. On the fastest-growing network in the deck, currency outranks
  vector format; revisit the SVGs at the next refresh.
- **Verdict:** use-with-caveat: current and clean-licensed, but a raster (the only
  one in the set) and not the in-station idiom.
