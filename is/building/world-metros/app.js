/* Metro Match — page logic (gate-3 state: full deck of 16).
   Vanilla JS. All stat data is baked into the #mm-data JSON island by
   _scripts/world_metros/build_metro_cards.py; nothing is fetched at runtime
   except the lore-back diagrams, which lazy-load on first flip. City keys
   are slugs (hong-kong, mexico-city). Battle and daily run on the core six;
   the deck's theme switch (D24) is CSS-only via data-theme. */
'use strict';

const DATA = JSON.parse(document.getElementById('mm-data').textContent);
const LIVE = DATA.live;
const CITIES = DATA.cities;

const $ = (id) => document.getElementById(id);
const upper = (k) => CITIES[k].name.toUpperCase();

// ------------------------------------------------------------------- tabs

const TAB_NAMES = ['deck', 'battle', 'daily', 'method'];
const tabs = TAB_NAMES.map((n) => $('tab-' + n));
const panels = TAB_NAMES.map((n) => $('panel-' + n));

function selectTab(name) {
  TAB_NAMES.forEach((n, i) => {
    const on = n === name;
    tabs[i].setAttribute('aria-selected', String(on));
    tabs[i].tabIndex = on ? 0 : -1;
    panels[i].hidden = !on;
  });
  if (name === 'battle' && !battle.started) dealRound(battle.seed);
  if (name === 'daily') renderDaily();
}

function go(name, hash) {
  selectTab(name);
  // battle owns its own hash (dealRound writes the #battle/you-vs-cpu pair so
  // the matchup URL is shareable); don't clobber it with a bare #battle.
  if (hash) history.replaceState(null, '', hash);
  else if (name !== 'battle') history.replaceState(null, '', '#' + name);
}

tabs.forEach((tab, i) => {
  tab.addEventListener('click', () => go(TAB_NAMES[i]));
  tab.addEventListener('keydown', (e) => {
    let j = null;
    if (e.key === 'ArrowRight') j = (i + 1) % tabs.length;
    if (e.key === 'ArrowLeft') j = (i + tabs.length - 1) % tabs.length;
    if (e.key === 'Home') j = 0;
    if (e.key === 'End') j = tabs.length - 1;
    if (j !== null) {
      e.preventDefault();
      go(TAB_NAMES[j]);
      tabs[j].focus();
    }
  });
});

function routeFromHash() {
  const h = (location.hash || '').replace(/^#/, '');
  const m = h.match(/^battle\/([a-z-]+)-vs-([a-z-]+)$/);
  if (m && LIVE.includes(m[1]) && LIVE.includes(m[2]) && m[1] !== m[2]) {
    // a shared matchup link starts that pairing as a clean match
    battle.seed = [m[1], m[2]];
    battle.started = false;
    battle.round = 1;
    battle.yScore = 0;
    battle.cScore = 0;
    selectTab('battle');
    return;
  }
  selectTab(TAB_NAMES.includes(h) ? h : 'deck');
}

window.addEventListener('hashchange', routeFromHash);

// ------------------------------------------------------- deck: card flips

function loadDiagram(scope) {
  scope.querySelectorAll('img[data-src]').forEach((img) => {
    img.src = img.dataset.src;
    img.removeAttribute('data-src');
  });
}

document.querySelectorAll('.flipbox').forEach((box) => {
  const unit = box.closest('.cardunit');
  const btn = unit.querySelector('.flipbtn');
  const front = box.querySelector('.face:not(.backface)');
  const back = box.querySelector('.face.backface');
  const toggle = () => {
    const flipped = box.classList.toggle('flipped');
    if (flipped) loadDiagram(back);
    btn.setAttribute('aria-pressed', String(flipped));
    btn.textContent = flipped ? 'FLIP · PLAY SIDE' : 'FLIP · LORE SIDE';
    front.setAttribute('aria-hidden', String(flipped));
    back.setAttribute('aria-hidden', String(!flipped));
  };
  btn.addEventListener('click', toggle);
  box.addEventListener('click', toggle); // pointer convenience; button is the keyboard path
});

// ----------------------------------------------------- deck: theme switch

const deckgrid = document.getElementById('deckgrid');
const setBtns = Array.from(document.querySelectorAll('.themebtn'));
setBtns.forEach((btn) => {
  btn.addEventListener('click', () => {
    deckgrid.dataset.set = btn.dataset.set;
    setBtns.forEach((b) =>
      b.setAttribute('aria-pressed', String(b === btn)));
  });
});

// ----------------------------------------------------------------- battle

const battle = {
  started: false, seed: null,
  you: null, cpu: null, round: 1, yScore: 0, cScore: 0, phase: 'pick',
};

function showCard(prefix, city) {
  LIVE.forEach((c) => { $(prefix + '-' + c).hidden = c !== city; });
}

function clearHot(scope) {
  scope.querySelectorAll('.crow.hot').forEach((r) => r.classList.remove('hot'));
}

function dealRound(seedPair) {
  battle.started = true;
  let you, cpu;
  if (seedPair) {
    [you, cpu] = seedPair;
    battle.seed = null;
  } else {
    you = LIVE[Math.floor(Math.random() * LIVE.length)];
    const rest = LIVE.filter((c) => c !== you);
    cpu = rest[Math.floor(Math.random() * rest.length)];
  }
  battle.you = you;
  battle.cpu = cpu;
  battle.phase = 'pick';
  showCard('you', you);
  showCard('cpu', cpu);
  clearHot($('panel-battle'));
  $('you-' + you).querySelectorAll('button.crow').forEach((b) => {
    b.removeAttribute('aria-disabled');
  });
  $('cpu-slot').classList.remove('revealed');
  $('b-round').textContent = 'ROUND ' + battle.round;
  $('b-prompt').hidden = false;
  $('b-call').hidden = true;
  $('b-nums').hidden = true;
  $('b-next').hidden = true;
  $('b-again').hidden = true;
  renderScore();
  history.replaceState(null, '', '#battle/' + you + '-vs-' + cpu);
}

function renderScore() {
  $('b-score').textContent =
    'you ' + battle.yScore + ' · cpu ' + battle.cScore + ' · first to 3';
}

function pickStat(stat) {
  if (battle.phase !== 'pick') return;
  battle.phase = 'reveal';
  const { you, cpu } = battle;
  $('you-' + you).querySelectorAll('button.crow').forEach((b) => {
    b.setAttribute('aria-disabled', 'true');
  });
  [$('you-' + you), $('cpu-' + cpu)].forEach((card) => {
    const row = card.querySelector('[data-stat="' + stat + '"]');
    if (row) row.classList.add('hot');
  });
  $('cpu-slot').classList.add('revealed');

  const win = DATA.stats[stat].win;
  const vy = CITIES[you].values[stat];
  const vc = CITIES[cpu].values[stat];
  const tie = vy === vc;
  const youWins = win === 'low' ? vy < vc : vy > vc;
  if (!tie) { if (youWins) battle.yScore += 1; else battle.cScore += 1; }

  $('b-prompt').hidden = true;
  $('b-call').hidden = false;
  $('b-nums').hidden = false;
  $('b-call').textContent = tie ? 'DEAD HEAT · NOBODY SCORES'
    : upper(youWins ? you : cpu) + ' TAKES THE ROUND';
  $('b-nums').textContent =
    CITIES[you].disp[stat] + ' vs ' + CITIES[cpu].disp[stat];
  renderScore();

  const over = battle.yScore === 3 || battle.cScore === 3;
  if (over) {
    $('b-call').textContent =
      (battle.yScore === 3 ? 'YOU TAKE THE MATCH' : 'CPU TAKES THE MATCH');
    $('b-nums').textContent = upper(youWins ? you : cpu) + ' closes it';
    $('b-again').hidden = false;
    $('b-again').focus();
  } else {
    $('b-next').hidden = false;
    $('b-next').focus();
  }
}

$('you-slot').addEventListener('click', (e) => {
  const btn = e.target.closest('button.crow[data-stat]');
  if (btn && btn.getAttribute('aria-disabled') !== 'true') {
    pickStat(btn.dataset.stat);
  }
});

$('b-next').addEventListener('click', () => {
  battle.round += 1;
  dealRound();
});

$('b-again').addEventListener('click', () => {
  battle.round = 1;
  battle.yScore = 0;
  battle.cScore = 0;
  dealRound();
});

// ------------------------------------------------------------------ daily

const DAY_MS = 86400000;
const STORE_KEY = 'metro-match-daily';

/* Two question forms, picked deterministically per day (D30, owner flag:
   "which plots more stations, HK vs Shanghai" was a giveaway):
   DUEL: head-to-head between two CLOSE systems only, never a blowout.
   PICK: one city, four candidate values; the wrong three are other
   cities' real figures nearest the truth. */
const DUEL_Q = {
  opened: 'Which opened earlier?',
  stations: 'Which plots more stations?',
  span: 'Which reaches further?',
  density: 'Which packs stations tighter?',
  routekm: 'Which reports more route-km?',
  ridership: 'Which carries more riders a year?',
};
const DUEL_VERB = {
  opened: 'opened earlier',
  stations: 'plots more stations',
  span: 'reaches further',
  density: 'packs them tighter',
  routekm: 'reports more route-km',
  ridership: 'carries more riders',
};
const PICK_Q = {
  opened: 'When did %C% open?',
  stations: 'How many stations does %C% plot?',
  span: 'How far apart are %C%\u2019s furthest stations?',
  density: 'How many stations per square km does %C% pack?',
  routekm: 'How many route-km does %C% report?',
  ridership: 'How many rides a year does %C% report?',
};
const PICK_LEAD = {
  opened: 'opened in',
  stations: 'plots',
  span: 'spans',
  density: 'packs',
  routekm: 'reports',
  ridership: 'reports',
};

function localDateStr(d) {
  return d.getFullYear() + '-' +
    String(d.getMonth() + 1).padStart(2, '0') + '-' +
    String(d.getDate()).padStart(2, '0');
}

function hashStr(s) {
  let h = 0;
  for (let i = 0; i < s.length; i += 1) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return h;
}

// a duel is only fair when the values are close: within 30 percent, or
// twelve years for opened, and never equal
function isClose(stat, a, b) {
  if (a === b) return false;
  if (stat === 'opened') return Math.abs(a - b) <= 12;
  return Math.max(a, b) / Math.min(a, b) <= 1.3;
}

function closePairs(stat) {
  return DATA.pairs.filter((p) =>
    isClose(stat, CITIES[p[0]].values[stat], CITIES[p[1]].values[stat]));
}

function dispFor(stat, value) {
  for (const c of LIVE) {
    if (CITIES[c].values[stat] === value) return CITIES[c].disp[stat];
  }
  return String(value);
}

// Deterministic per-day challenge: the stat, the form and the contestants
// all derive from the date.
function dailyChallenge(dateStr) {
  const h = hashStr(dateStr);
  const stat = DATA.statOrder[h % DATA.statOrder.length];
  if (Math.floor(h / 11) % 2 === 0) {
    const pool = closePairs(stat);
    if (pool.length) {
      const pair = pool[Math.floor(h / 7) % pool.length].slice();
      if (Math.floor(h / 53) % 2) pair.reverse();
      return { mode: 'duel', stat: stat, pair: pair };
    }
  }
  const city = LIVE[Math.floor(h / 13) % LIVE.length];
  const truth = CITIES[city].values[stat];
  const others = [];
  LIVE.forEach((c) => {
    const v = CITIES[c].values[stat];
    if (v !== truth && others.indexOf(v) === -1) others.push(v);
  });
  others.sort((x, y) => Math.abs(x - truth) - Math.abs(y - truth));
  const values = others.slice(0, 3);
  values.splice(Math.floor(h / 29) % 4, 0, truth);
  return { mode: 'pick', stat: stat, city: city, values: values, truth: truth };
}

function betterCity(stat, x, y) {
  const low = DATA.stats[stat].win === 'low';
  const vx = CITIES[x].values[stat];
  const vy = CITIES[y].values[stat];
  return (low ? vx < vy : vx > vy) ? x : y;
}

function bandHTML(city) {
  return CITIES[city].lines.map((l) =>
    '<i style="background:' + l.color + '"></i>').join('');
}

function pickButtons() {
  return Array.from(document.querySelectorAll('#d-mc .dopt'));
}

function loadStore() {
  try {
    return JSON.parse(localStorage.getItem(STORE_KEY)) || null;
  } catch (e) {
    return null;
  }
}

function saveStore(state) {
  try {
    localStorage.setItem(STORE_KEY, JSON.stringify(state));
  } catch (e) { /* private mode: the daily still plays, the streak forgets */ }
}

function renderDaily() {
  const today = localDateStr(new Date());
  const ch = dailyChallenge(today);
  $('d-date').textContent = today;
  $('d-stat').textContent = 'TODAY \u00b7 ' + ch.stat.toUpperCase();
  $('d-duel').hidden = ch.mode !== 'duel';
  $('d-mc').hidden = ch.mode !== 'pick';
  if (ch.mode === 'duel') {
    $('d-q').textContent = DUEL_Q[ch.stat];
    const btnA = $('d-a');
    const btnB = $('d-b');
    btnA.dataset.city = ch.pair[0];
    btnB.dataset.city = ch.pair[1];
    btnA.querySelector('.dname').textContent = upper(ch.pair[0]);
    btnB.querySelector('.dname').textContent = upper(ch.pair[1]);
    btnA.querySelector('.dpills').innerHTML = bandHTML(ch.pair[0]);
    btnB.querySelector('.dpills').innerHTML = bandHTML(ch.pair[1]);
  } else {
    $('d-q').textContent = PICK_Q[ch.stat].replace('%C%', upper(ch.city));
    $('d-mc-band').innerHTML = bandHTML(ch.city);
    pickButtons().forEach((btn, i) => {
      btn.querySelector('.doptval').textContent = dispFor(ch.stat, ch.values[i]);
    });
  }
  const saved = loadStore();
  if (saved && saved.d === today && saved.mode === ch.mode) {
    revealDaily(saved.pick, saved.correct, saved.streak, true);
  } else {
    [$('d-a'), $('d-b')].forEach((btn) => {
      btn.removeAttribute('aria-disabled');
      btn.classList.remove('correct', 'wrongpick');
      btn.querySelector('.dmeta').textContent = '?';
    });
    pickButtons().forEach((btn) => {
      btn.removeAttribute('aria-disabled');
      btn.classList.remove('correct', 'wrongpick');
    });
    $('d-verdict').hidden = true;
    const streak = saved && saved.correct &&
      isYesterday(saved.d, today) ? saved.streak : 0;
    $('d-streak').textContent = streak > 0
      ? 'streak ' + streak + ' \u00b7 play to keep it'
      : 'one guess, once a day';
  }
}

function isYesterday(dateStr, todayStr) {
  const d = new Date(dateStr + 'T12:00:00');
  return localDateStr(new Date(d.getTime() + DAY_MS)) === todayStr;
}

function guessDaily(pick) {
  const today = localDateStr(new Date());
  const saved = loadStore();
  if (saved && saved.d === today && saved.mode) return; // already played
  const ch = dailyChallenge(today);
  const correct = ch.mode === 'duel'
    ? pick === betterCity(ch.stat, ch.pair[0], ch.pair[1])
    : ch.values[pick] === ch.truth;
  const base = saved && saved.correct && isYesterday(saved.d, today)
    ? saved.streak : 0;
  const streak = correct ? base + 1 : 0;
  saveStore({ d: today, mode: ch.mode, pick: pick, correct: correct, streak: streak });
  revealDaily(pick, correct, streak, false);
  $('d-verdict').focus();
}

function revealDaily(pick, correct, streak, fromStore) {
  const today = localDateStr(new Date());
  const ch = dailyChallenge(today);
  const v = $('d-verdict');
  const tail = fromStore
    ? 'You played today; new question tomorrow.'
    : 'New question tomorrow.';
  if (ch.mode === 'duel') {
    const winner = betterCity(ch.stat, ch.pair[0], ch.pair[1]);
    const loser = ch.pair[0] === winner ? ch.pair[1] : ch.pair[0];
    [$('d-a'), $('d-b')].forEach((btn) => {
      const city = btn.dataset.city;
      btn.setAttribute('aria-disabled', 'true');
      btn.querySelector('.dmeta').textContent = CITIES[city].disp[ch.stat];
      btn.classList.toggle('correct', city === winner);
      btn.classList.toggle('wrongpick', city === pick && city !== winner);
    });
    v.innerHTML = (correct ? '<b>Right.</b> ' : '<b>Not this time.</b> ') +
      upper(winner) + ' ' + DUEL_VERB[ch.stat] + ' (' +
      CITIES[winner].disp[ch.stat] + ' vs ' + CITIES[loser].disp[ch.stat] +
      '). ' + tail;
  } else {
    pickButtons().forEach((btn, i) => {
      btn.setAttribute('aria-disabled', 'true');
      btn.classList.toggle('correct', ch.values[i] === ch.truth);
      btn.classList.toggle('wrongpick', i === pick && ch.values[i] !== ch.truth);
    });
    v.innerHTML = (correct ? '<b>Right.</b> ' : '<b>Not this time.</b> ') +
      upper(ch.city) + ' ' + PICK_LEAD[ch.stat] + ' ' +
      dispFor(ch.stat, ch.truth) + '. ' + tail;
  }
  v.hidden = false;
  $('d-streak').textContent = correct
    ? 'streak ' + streak
    : 'streak resets \u00b7 back to 0';
}

[$('d-a'), $('d-b')].forEach((btn) => {
  btn.addEventListener('click', () => {
    if (btn.getAttribute('aria-disabled') === 'true') return;
    guessDaily(btn.dataset.city);
  });
});

pickButtons().forEach((btn, i) => {
  btn.addEventListener('click', () => {
    if (btn.getAttribute('aria-disabled') === 'true') return;
    guessDaily(i);
  });
});

// ------------------------------------------------------------------- init

routeFromHash();
