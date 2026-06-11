/* Metro Match — page logic (D17 card pivot, D20-resolved state).
   Vanilla JS. All stat data is baked into the #mm-data JSON island by
   _scripts/world_metros/build_metro_cards.py; nothing is fetched at runtime
   except the lore-back diagrams, which lazy-load on first flip. */
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
  history.replaceState(null, '', hash || '#' + name);
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
  const m = h.match(/^battle\/([a-z]+)-vs-([a-z]+)$/);
  if (m && LIVE.includes(m[1]) && LIVE.includes(m[2]) && m[1] !== m[2]) {
    battle.seed = [m[1], m[2]];
    battle.started = false;
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
  const youWins = win === 'low' ? vy < vc : vy > vc;
  if (youWins) battle.yScore += 1; else battle.cScore += 1;

  $('b-prompt').hidden = true;
  $('b-call').hidden = false;
  $('b-nums').hidden = false;
  $('b-call').textContent = upper(youWins ? you : cpu) + ' TAKES THE ROUND';
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

function dailyPair(dateStr) {
  const h = hashStr(dateStr);
  const pair = DATA.pairs[h % DATA.pairs.length].slice();
  if ((h >> 3) % 2) pair.reverse();
  return pair;
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
  const [a, b] = dailyPair(today);
  $('d-date').textContent = today;
  const btnA = $('d-a');
  const btnB = $('d-b');
  btnA.dataset.city = a;
  btnB.dataset.city = b;
  btnA.querySelector('.dname').textContent = upper(a);
  btnB.querySelector('.dname').textContent = upper(b);

  const saved = loadStore();
  if (saved && saved.d === today) {
    revealDaily(saved.pick, saved.correct, saved.streak, true);
  } else {
    [btnA, btnB].forEach((btn) => {
      btn.removeAttribute('aria-disabled');
      btn.classList.remove('correct', 'wrongpick');
      btn.querySelector('.dmeta').textContent = '?';
    });
    $('d-verdict').hidden = true;
    const streak = saved && saved.correct &&
      isYesterday(saved.d, today) ? saved.streak : 0;
    $('d-streak').textContent = streak > 0
      ? 'streak ' + streak + ' · play to keep it'
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
  if (saved && saved.d === today) return; // already played
  const [a, b] = dailyPair(today);
  const other = pick === a ? b : a;
  const correct = CITIES[pick].values.stations > CITIES[other].values.stations;
  const base = saved && saved.correct && isYesterday(saved.d, today)
    ? saved.streak : 0;
  const streak = correct ? base + 1 : 0;
  saveStore({ d: today, pick: pick, correct: correct, streak: streak });
  revealDaily(pick, correct, streak, false);
  $('d-verdict').focus();
}

function revealDaily(pick, correct, streak, fromStore) {
  const today = localDateStr(new Date());
  const [a, b] = dailyPair(today);
  const winner = CITIES[a].values.stations > CITIES[b].values.stations ? a : b;
  [$('d-a'), $('d-b')].forEach((btn) => {
    const city = btn.dataset.city;
    btn.setAttribute('aria-disabled', 'true');
    btn.querySelector('.dmeta').textContent =
      CITIES[city].values.stations + ' plotted';
    btn.classList.toggle('correct', city === winner);
    btn.classList.toggle('wrongpick', city === pick && city !== winner);
  });
  const v = $('d-verdict');
  v.hidden = false;
  v.innerHTML = (correct ? '<b>Right.</b> ' : '<b>Not this time.</b> ') +
    upper(winner) + ' plots more stations. ' +
    (fromStore ? 'You played today; new pair tomorrow.' : 'New pair tomorrow.');
  $('d-streak').textContent = correct
    ? 'streak ' + streak
    : 'streak resets · back to 0';
}

[$('d-a'), $('d-b')].forEach((btn) => {
  btn.addEventListener('click', () => {
    if (btn.getAttribute('aria-disabled') === 'true') return;
    guessDaily(btn.dataset.city);
  });
});

// ------------------------------------------------------------------- init

routeFromHash();
