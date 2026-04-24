// Konbini — vanilla JS MVP.
// Routes: #/, #/item/:id, #/board, #/board/:id, #/saved, #/about

const STORAGE_KEYS = {
  saved: "konbini.savedWords",
  basket: "konbini.basket",
};

const ZONE_ORDER = ["food_aisle", "drinks_fridge", "hot_case"];

const state = {
  content: null,
  saved: new Set(loadJSON(STORAGE_KEYS.saved, [])),
  basket: loadJSON(STORAGE_KEYS.basket, []), // array of itemIds; duplicates allowed
};

function loadJSON(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function persistSet(key, set) {
  try {
    localStorage.setItem(key, JSON.stringify([...set]));
  } catch {
    /* ignore quota */
  }
}

function persistBasket() {
  try {
    localStorage.setItem(STORAGE_KEYS.basket, JSON.stringify(state.basket));
  } catch {
    /* ignore */
  }
}

function basketTotal() {
  return state.basket.reduce((sum, id) => {
    const item = state.content.items[id];
    return sum + (item ? Number(item.price) || 0 : 0);
  }, 0);
}

function basketGrouped() {
  const map = new Map();
  for (const id of state.basket) {
    map.set(id, (map.get(id) ?? 0) + 1);
  }
  return [...map.entries()].map(([id, count]) => ({
    item: state.content.items[id],
    count,
  }));
}

// Rounding rule (spec delta §9, unchanged): next ¥1000; next ¥500 if total ≤ 500.
function roundUpPayment(total) {
  if (total <= 0) return 0;
  if (total <= 500) return Math.ceil(total / 500) * 500;
  return Math.ceil(total / 1000) * 1000;
}

// ── HTML escape ──
function esc(str) {
  if (str == null) return "";
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

// Resolve [word-id] markers to their vocab surface and drop 《…》 furigana notation,
// returning a plain-text comparable string (used to dedupe labels that match content).
function resolvePlain(text) {
  if (text == null) return "";
  return String(text)
    .replace(/\[([a-z0-9][a-z0-9-]*)\]/g, (full, id) => {
      const entry = state.content?.vocab?.[id];
      return entry?.surface ?? full;
    })
    .replace(/《[^》]*》/g, "")
    .trim();
}

// ── Furigana rendering ──
// Two markers in content:
//   [word-id]       → <ruby class="word" data-word="word-id">surface<rt>reading</rt></ruby>
//   漢字《ふりがな》 → <ruby>漢字<rt>ふりがな</rt></ruby>
// Word-id pass runs first. The 《》 pass only matches kanji immediately followed by 《…》,
// which cannot appear inside already-formed <ruby> tags emitted by the word-id pass.
function renderInline(text) {
  if (text == null) return "";
  const escaped = esc(text);
  const withWords = escaped.replace(
    /\[([a-z0-9][a-z0-9-]*)\]/g,
    (full, id) => {
      const entry = state.content.vocab[id];
      if (!entry) return full; // leave bracket as literal if vocab missing
      const surface = esc(entry.surface || id);
      const reading = esc(entry.reading || "");
      return (
        `<ruby class="word" data-word="${esc(id)}" tabindex="0" role="button">` +
        `${surface}<rt>${reading}</rt></ruby>`
      );
    },
  );
  // Kanji range: CJK Unified Ideographs + iteration mark 々
  return withWords.replace(
    /([\u3400-\u9FFF々]+)《([^》]+)》/g,
    (_, kanji, read) => `<ruby>${kanji}<rt>${read}</rt></ruby>`,
  );
}

// ── Router ──
function parseHash() {
  const raw = location.hash.replace(/^#/, "") || "/";
  const parts = raw.split("/").filter(Boolean);
  return parts;
}

function route() {
  const parts = parseHash();
  const app = document.getElementById("app");
  app.scrollTo?.({ top: 0 });
  window.scrollTo({ top: 0 });
  if (parts.length === 0) return renderShelves(app);
  if (parts[0] === "item" && parts[1]) return renderItem(app, parts[1]);
  if (parts[0] === "board" && parts[1]) return renderNotice(app, parts[1]);
  if (parts[0] === "board") return renderBoard(app);
  if (parts[0] === "saved") return renderSaved(app);
  if (parts[0] === "about") return renderAbout(app);
  if (parts[0] === "register" && parts[1] === "checkout")
    return renderCheckout(app);
  if (parts[0] === "register") return renderRegister(app);
  return renderShelves(app);
}

// ── Chrome nav ──
function ui(key) {
  const entry = state.content.ui_strings[key];
  return entry ? entry : { jp: key, en: key };
}

function renderChrome() {
  const nav = document.getElementById("chrome-nav");
  const basketCount = state.basket.length;
  const items = [
    { hash: "#/", key: "shelves_label" },
    { hash: "#/board", key: "board_label" },
    { hash: "#/register", key: "register_label", badge: basketCount || null },
    { hash: "#/saved", key: "saved_label" },
    { hash: "#/about", key: "about_label" },
  ];
  const hash = location.hash || "#/";
  nav.innerHTML = items
    .map((it) => {
      const label = ui(it.key);
      const active =
        (hash === "#/" && it.hash === "#/") ||
        (it.hash !== "#/" && hash.startsWith(it.hash));
      const badge =
        it.badge != null
          ? `<span class="chrome-nav-badge">${esc(it.badge)}</span>`
          : "";
      return `<a href="${it.hash}" class="${active ? "is-active" : ""}" aria-label="${esc(label.en)}">${renderInline(label.jp)}${badge}</a>`;
    })
    .join("");
}

// ── Views ──
function renderShelves(app) {
  const zonesPresent = new Map();
  for (const item of Object.values(state.content.items)) {
    if (!zonesPresent.has(item.zone)) zonesPresent.set(item.zone, []);
    zonesPresent.get(item.zone).push(item);
  }
  const orderedZones = [
    ...ZONE_ORDER.filter((z) => zonesPresent.has(z)),
    ...[...zonesPresent.keys()].filter((z) => !ZONE_ORDER.includes(z)),
  ];

  const sections = orderedZones
    .map((zone) => {
      const zoneLabel = ui(`${zone}_name`);
      const items = zonesPresent.get(zone);
      return `
        <section class="zone">
          <div class="zone-head">
            <h2>${renderInline(zoneLabel.jp)}</h2>
            <span class="zone-gloss">${esc(zoneLabel.en)}</span>
          </div>
          <div class="shelf">
            ${items.map(renderItemCard).join("")}
          </div>
        </section>
      `;
    })
    .join("");

  app.innerHTML = `
    <h1 class="app-heading">${renderInline(ui("shelves_label").jp)}</h1>
    <p class="app-sublede">${renderInline(ui("first_time_greeting").jp)}</p>
    ${sections || emptyState("basket_empty_heading")}
  `;
}

function renderItemCard(item) {
  return `
    <a class="item-card" href="#/item/${esc(item.id)}">
      <div>
        <h3 class="item-card-name">${esc(item.name_jp)}</h3>
        <p class="item-card-gloss">${esc(item.name_en)}</p>
      </div>
      <div class="item-card-meta">
        <span class="item-card-price">¥${esc(item.price)}</span>
        ${item.weight ? `<span class="item-card-weight">${esc(item.weight)}</span>` : ""}
      </div>
    </a>
  `;
}

function renderItem(app, id) {
  const item = state.content.items[id];
  if (!item) {
    app.innerHTML = `
      <a class="back-link" href="#/">${renderInline(ui("back_label").jp)}</a>
      <div class="empty">item not found: ${esc(id)}</div>
    `;
    return;
  }
  const inBasket = state.basket.includes(id);
  const ctaKey = inBasket ? "take_to_register_again" : "take_to_register_default";
  app.innerHTML = `
    <a class="back-link" href="#/">${renderInline(ui("back_label").jp)}</a>
    <article class="item-detail">
      <header class="item-header">
        <h1>${esc(item.name_jp)}</h1>
        <p class="item-desc-jp">${renderInline(item.description_jp)}</p>
        <p class="item-desc-en">${esc(item.description_en)}</p>
        <div class="item-actions">
          <span class="item-actions-price">¥${esc(item.price)}</span>
          <button class="cta" data-act="add-to-basket" data-item="${esc(item.id)}">${renderInline(ui(ctaKey).jp)}</button>
        </div>
      </header>
      <div class="package">
        <section class="package-face package-face--front" aria-label="front">
          <span class="face-tag">${esc(ui("front_label").en)}</span>
          ${item.front.map(renderBlock).join("")}
        </section>
        <section class="package-face package-face--back" aria-label="back">
          <span class="face-tag">${esc(ui("back_label_item").en)}</span>
          ${item.back.map(renderBlock).join("")}
        </section>
      </div>
    </article>
  `;
}

function handleAddToBasket(itemId, btn) {
  state.basket.push(itemId);
  persistBasket();
  renderChrome();
  // Brief "added" flash then restore CTA-again label.
  const added = ui("take_to_register_added");
  btn.innerHTML = renderInline(added.jp);
  btn.classList.add("is-added");
  setTimeout(() => {
    btn.classList.remove("is-added");
    btn.innerHTML = renderInline(ui("take_to_register_again").jp);
  }, 900);
}

function renderBlock(block) {
  switch (block.type) {
    case "banner": {
      const argPlain = resolvePlain(block.arg);
      const bodyPlain = resolvePlain(block.body);
      const showArg = block.arg && argPlain !== bodyPlain;
      return `<div class="block block-banner">${showArg ? `<span class="block-banner-arg">${renderInline(block.arg)}</span>` : ""}${renderInline(block.body)}</div>`;
    }
    case "hero":
      return `<div class="block block-hero">${renderBodyAsParagraphs(block.body)}</div>`;
    case "footer":
      return `<div class="block block-footer">${renderBodyAsParagraphs(block.body)}</div>`;
    case "section":
      return `
        <div class="block block-section">
          ${block.arg ? `<p class="block-section-arg">${renderInline(block.arg)}</p>` : ""}
          <div class="block-section-body">${renderBodyAsParagraphs(block.body)}</div>
        </div>
      `;
    case "nutrition":
      return `
        <div class="block block-nutrition">
          ${block.arg ? `<div class="block-nutrition-caption">${renderInline(block.arg)}</div>` : ""}
          ${block.rows
            .map(
              (r) => `
              <div class="block-nutrition-row">
                <span>${renderInline(r.left)}</span>
                <span class="block-nutrition-row-right">${renderInline(r.right)}</span>
              </div>
            `,
            )
            .join("")}
        </div>
      `;
    case "fineprint":
      return `<div class="block block-fineprint">${renderBodyAsParagraphs(block.body)}</div>`;
    case "heading":
      return `<h2 class="block block-heading">${renderInline(block.body)}</h2>`;
    default:
      return `<div class="block block-other">${renderBodyAsParagraphs(block.body || "")}</div>`;
  }
}

function renderBodyAsParagraphs(raw) {
  if (!raw) return "";
  return raw
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => `<p>${renderInline(line)}</p>`)
    .join("");
}

// ── Board (notices) ──
function renderBoard(app) {
  const notices = Object.values(state.content.notices);
  if (notices.length === 0) {
    app.innerHTML = `
      <a class="back-link" href="#/">${renderInline(ui("back_label").jp)}</a>
      ${deadpanEmpty("empty_board")}
    `;
    return;
  }
  app.innerHTML = `
    <a class="back-link" href="#/">${renderInline(ui("back_label").jp)}</a>
    <h1 class="app-heading">${renderInline(ui("board_label").jp)}</h1>
    <div class="board">
      ${notices.map(renderNoticeCard).join("")}
    </div>
  `;
}

function renderNoticeCard(notice) {
  const headingBlock = notice.blocks.find((b) => b.type === "heading");
  const heading = headingBlock
    ? renderInline(headingBlock.body)
    : esc(notice.id);
  const meta = [
    notice.posted_date ? esc(notice.posted_date) : null,
    notice.posted_by ? renderInline(notice.posted_by) : null,
  ]
    .filter(Boolean)
    .join(" · ");
  const styleClass =
    notice.style === "handwritten" ? " notice-card--handwritten" : "";
  const preview = notice.prose
    ? renderBodyAsParagraphs(notice.prose.split("\n").slice(0, 2).join("\n"))
    : "";
  return `
    <a class="notice-card${styleClass}" href="#/board/${esc(notice.id)}">
      <h3>${heading}</h3>
      ${meta ? `<p class="notice-card-meta">${meta}</p>` : ""}
      <div class="notice-card-body">${preview}</div>
    </a>
  `;
}

function renderNotice(app, id) {
  const notice = state.content.notices[id];
  if (!notice) {
    app.innerHTML = `
      <a class="back-link" href="#/board">${renderInline(ui("back_label").jp)}</a>
      <div class="empty">notice not found: ${esc(id)}</div>
    `;
    return;
  }
  const heading = notice.blocks.find((b) => b.type === "heading");
  const footer = notice.blocks.find((b) => b.type === "footer");
  const styleClass =
    notice.style === "handwritten" ? " notice-card--handwritten" : "";
  app.innerHTML = `
    <a class="back-link" href="#/board">${renderInline(ui("back_label").jp)}</a>
    <article class="notice-card${styleClass}" style="max-width: 620px; margin: 0 auto;">
      ${heading ? `<h3>${renderInline(heading.body)}</h3>` : ""}
      <p class="notice-card-meta">
        ${notice.posted_date ? esc(notice.posted_date) : ""}
        ${notice.posted_by ? ` · ${renderInline(notice.posted_by)}` : ""}
      </p>
      <div class="notice-card-body">${renderBodyAsParagraphs(notice.prose || "")}</div>
      ${footer ? `<p class="notice-card-meta" style="margin-top:0.8rem;">${renderInline(footer.body)}</p>` : ""}
    </article>
  `;
}

// ── Saved ──
function renderSaved(app) {
  const ids = [...state.saved];
  if (ids.length === 0) {
    app.innerHTML = `
      <a class="back-link" href="#/">${renderInline(ui("back_label").jp)}</a>
      <h1 class="app-heading">${renderInline(ui("saved_label").jp)}</h1>
      ${deadpanEmpty("empty_saved_words")}
    `;
    return;
  }
  const rows = ids
    .map((id) => state.content.vocab[id])
    .filter(Boolean)
    .map((entry) => {
      const ruby = entry.reading
        ? `<ruby>${esc(entry.surface)}<rt>${esc(entry.reading)}</rt></ruby>`
        : esc(entry.surface);
      return `
        <li class="notice-card" style="border-left-color: var(--ink-muted);">
          <h3>${ruby}</h3>
          <p class="notice-card-meta">${esc(entry.jlpt || "")} · ${esc(entry.pos || "")}</p>
          <div class="notice-card-body"><p>${esc(entry.meaning_en || "")}</p></div>
        </li>
      `;
    })
    .join("");
  app.innerHTML = `
    <a class="back-link" href="#/">${renderInline(ui("back_label").jp)}</a>
    <h1 class="app-heading">${renderInline(ui("saved_label").jp)}</h1>
    <ul class="board" style="list-style:none; padding:0; margin:0;">${rows}</ul>
  `;
}

// ── Register (basket) ──
function renderRegister(app) {
  const groups = basketGrouped();
  const total = basketTotal();
  if (groups.length === 0) {
    app.innerHTML = `
      <a class="back-link" href="#/">${renderInline(ui("back_label").jp)}</a>
      <h1 class="app-heading">${renderInline(ui("register_label").jp)}</h1>
      ${deadpanEmpty("empty_basket")}
    `;
    return;
  }
  const rows = groups
    .map(
      ({ item, count }) => `
      <li class="basket-row" data-item="${esc(item.id)}">
        <a class="basket-row-name" href="#/item/${esc(item.id)}">
          <span class="basket-row-jp">${esc(item.name_jp)}</span>
          <span class="basket-row-en">${esc(item.name_en)}</span>
        </a>
        <span class="basket-row-price">¥${esc(item.price)}</span>
        <span class="basket-row-count">×${count}</span>
        <button class="basket-row-remove" data-act="basket-remove" data-item="${esc(item.id)}" aria-label="remove one">−</button>
      </li>
    `,
    )
    .join("");
  app.innerHTML = `
    <a class="back-link" href="#/">${renderInline(ui("back_label").jp)}</a>
    <h1 class="app-heading">${renderInline(ui("register_label").jp)}</h1>
    <ul class="basket">${rows}</ul>
    <div class="basket-total">
      <span class="basket-total-label">${renderInline(ui("total_label").jp)}</span>
      <span class="basket-total-amount">¥${total.toLocaleString("en")}</span>
    </div>
    <div class="basket-actions">
      <a class="cta cta--primary" href="#/register/checkout">${renderInline(ui("checkout_button").jp)}</a>
    </div>
  `;
}

function removeOneFromBasket(itemId) {
  const idx = state.basket.lastIndexOf(itemId);
  if (idx >= 0) {
    state.basket.splice(idx, 1);
    persistBasket();
  }
  renderChrome();
  route();
}

// ── Checkout runner ──
// State machine walks the checkout-standard dialogue script one turn at a time.
// Tap-to-advance on clerk/action/exit turns; player-choice shows buttons.
// clerk-branch[id] turns only render when their id matches the most recent choice.
const checkout = {
  script: null,
  idx: 0,
  total: 0,
  payment: 0,
  change: 0,
  lastResponse: null,
  active: false,
};

function renderCheckout(app) {
  const script = state.content.dialogue["checkout-standard"]?.script;
  if (!script) {
    app.innerHTML = `<div class="empty">checkout script missing</div>`;
    return;
  }
  if (state.basket.length === 0) {
    app.innerHTML = `
      <a class="back-link" href="#/register">${renderInline(ui("back_label").jp)}</a>
      ${deadpanEmpty("empty_basket")}
    `;
    return;
  }
  checkout.script = script;
  checkout.idx = 0;
  checkout.total = basketTotal();
  checkout.payment = roundUpPayment(checkout.total);
  checkout.change = checkout.payment - checkout.total;
  checkout.lastResponse = null;
  checkout.active = true;
  app.innerHTML = `
    <a class="back-link" href="#/register">${renderInline(ui("back_label").jp)}</a>
    <div class="checkout">
      <div class="checkout-transcript" id="checkout-transcript"></div>
      <div class="checkout-prompt" id="checkout-prompt"></div>
    </div>
  `;
  advanceCheckout();
}

function advanceCheckout() {
  if (!checkout.active) return;
  const transcript = document.getElementById("checkout-transcript");
  const prompt = document.getElementById("checkout-prompt");
  if (!transcript || !prompt) return;

  while (checkout.idx < checkout.script.length) {
    const block = checkout.script[checkout.idx];
    checkout.idx += 1;

    if (block.type === "clerk") {
      appendClerkTurn(transcript, block.body);
      showTapToContinue(prompt);
      return;
    }
    if (block.type === "clerk-branch") {
      if (block.arg === checkout.lastResponse) {
        appendClerkTurn(transcript, block.body);
        showTapToContinue(prompt);
        return;
      }
      continue; // skip non-matching branch silently
    }
    if (block.type === "player-choice") {
      showChoices(prompt, block.options);
      return;
    }
    if (block.type === "action") {
      appendActionTurn(transcript, block.body.trim());
      continue; // internal marker — advance through automatically
    }
    if (block.type === "exit") {
      appendExitTurn(transcript, block.body);
      showExit(prompt);
      return;
    }
  }
  // script exhausted without explicit exit (shouldn't happen per spec)
  showExit(prompt);
}

function appendClerkTurn(transcript, rawBody) {
  const body = substituteVars(rawBody);
  transcript.insertAdjacentHTML(
    "beforeend",
    `<div class="turn turn-clerk"><div class="turn-label">店員</div><p>${renderInline(body)}</p></div>`,
  );
  scrollIntoView(transcript);
}

function appendActionTurn(transcript, marker) {
  const label =
    marker === "player_places_items"
      ? "かごを置く"
      : marker === "payment_exchange"
        ? "お金のやり取り"
        : marker;
  transcript.insertAdjacentHTML(
    "beforeend",
    `<div class="turn turn-action"><em>${esc(label)}</em></div>`,
  );
  scrollIntoView(transcript);
}

function appendPlayerTurn(transcript, text) {
  transcript.insertAdjacentHTML(
    "beforeend",
    `<div class="turn turn-player"><div class="turn-label">あなた</div><p>${renderInline(text)}</p></div>`,
  );
  scrollIntoView(transcript);
}

function appendExitTurn(transcript, rawBody) {
  transcript.insertAdjacentHTML(
    "beforeend",
    `<div class="turn turn-exit"><p>${esc(rawBody.trim())}</p></div>`,
  );
  scrollIntoView(transcript);
}

function scrollIntoView(el) {
  el.scrollTop = el.scrollHeight;
  window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
}

function showTapToContinue(prompt) {
  prompt.innerHTML = `
    <button class="tap-continue" data-act="checkout-advance">
      ${renderInline(ui("tap_to_continue").jp)}
    </button>
  `;
}

function showChoices(prompt, options) {
  prompt.innerHTML = `
    <div class="choices">
      ${options
        .map(
          (o) => `
          <button class="choice" data-act="checkout-choose" data-response-id="${esc(o.response_id || "")}" data-label="${esc(o.text)}">
            <span class="choice-label">${esc(o.label)}</span>
            <span class="choice-text">${renderInline(o.text)}</span>
          </button>
        `,
        )
        .join("")}
    </div>
  `;
}

function showExit(prompt) {
  prompt.innerHTML = `
    <button class="cta cta--primary" data-act="checkout-exit">out</button>
  `;
}

function chooseCheckout(responseId, label) {
  const transcript = document.getElementById("checkout-transcript");
  checkout.lastResponse = responseId || null;
  appendPlayerTurn(transcript, label);
  advanceCheckout();
}

function exitCheckout() {
  state.basket = [];
  persistBasket();
  checkout.active = false;
  location.hash = "#/";
}

function substituteVars(text) {
  return String(text)
    .replaceAll("{{basket_total}}", String(checkout.total))
    .replaceAll("{{payment_amount}}", String(checkout.payment))
    .replaceAll("{{change_amount}}", String(checkout.change));
}

// ── About ──
function renderAbout(app) {
  const about = state.content.ui_strings.about_body || {};
  const jp = (about.jp || "")
    .split(/\n\n+/)
    .map((p) => `<p>${renderInline(p.trim())}</p>`)
    .join("");
  app.innerHTML = `
    <a class="back-link" href="#/">${renderInline(ui("back_label").jp)}</a>
    <h1 class="app-heading">${renderInline(ui("about_label").jp)}</h1>
    <article class="item-detail" style="max-width: 620px;">
      <div class="package-face" style="line-height:1.85;">${jp}</div>
      <p class="item-desc-en" style="max-width: 620px;">${esc(about.en || "")}</p>
    </article>
  `;
}

// ── Deadpan empty states ──
function deadpanEmpty(key) {
  const msg = ui(key);
  return `<div class="empty empty--deadpan">${renderInline(msg.jp)}</div>`;
}

function emptyState(key) {
  return deadpanEmpty(key);
}

// ── Popup ──
const popupEl = document.getElementById("popup");
const scrimEl = document.getElementById("popup-scrim");

function openPopup(wordId) {
  const entry = state.content.vocab[wordId];
  if (!entry) return;
  const surfaceRuby = entry.reading
    ? `<ruby>${esc(entry.surface)}<rt>${esc(entry.reading)}</rt></ruby>`
    : esc(entry.surface);
  const saved = state.saved.has(wordId);
  const saveLabel = ui(saved ? "save_confirmed" : "save_button");
  const closeLabel = ui("close_button");
  popupEl.innerHTML = `
    <h2 class="popup-surface">${surfaceRuby}</h2>
    <p class="popup-meta">${esc(entry.jlpt || "")}${entry.pos ? ` · ${esc(entry.pos)}` : ""}</p>
    <p class="popup-meaning">${esc(entry.meaning_en || "")}</p>
    ${entry.etymology ? `<p class="popup-etym">${esc(entry.etymology)}</p>` : ""}
    ${entry.korean_parallel ? `<p class="popup-korean">${esc(entry.korean_parallel)}</p>` : ""}
    <div class="popup-actions">
      <button class="popup-btn" data-act="close">${renderInline(closeLabel.jp)}</button>
      <button class="popup-btn popup-btn--primary ${saved ? "is-saved" : ""}" data-act="save" data-word="${esc(wordId)}">${renderInline(saveLabel.jp)}</button>
    </div>
  `;
  popupEl.classList.add("is-open");
  scrimEl.classList.add("is-open");
  popupEl.setAttribute("aria-hidden", "false");
  scrimEl.setAttribute("aria-hidden", "false");
}

function closePopup() {
  popupEl.classList.remove("is-open");
  scrimEl.classList.remove("is-open");
  popupEl.setAttribute("aria-hidden", "true");
  scrimEl.setAttribute("aria-hidden", "true");
}

function toggleSave(wordId, btn) {
  if (state.saved.has(wordId)) {
    state.saved.delete(wordId);
  } else {
    state.saved.add(wordId);
  }
  persistSet(STORAGE_KEYS.saved, state.saved);
  // Update button label + class without closing
  const saved = state.saved.has(wordId);
  const label = ui(saved ? "save_confirmed" : "save_button");
  btn.innerHTML = renderInline(label.jp);
  btn.classList.toggle("is-saved", saved);
}

// ── Event delegation ──
document.addEventListener("click", (e) => {
  const word = e.target.closest(".word");
  if (word) {
    e.preventDefault();
    openPopup(word.dataset.word);
    return;
  }
  const action = e.target.closest("[data-act]");
  if (action) {
    const act = action.dataset.act;
    if (act === "close") closePopup();
    else if (act === "save") toggleSave(action.dataset.word, action);
    else if (act === "add-to-basket")
      handleAddToBasket(action.dataset.item, action);
    else if (act === "checkout-advance") advanceCheckout();
    else if (act === "checkout-choose")
      chooseCheckout(action.dataset.responseId, action.dataset.label);
    else if (act === "checkout-exit") exitCheckout();
    else if (act === "basket-remove") removeOneFromBasket(action.dataset.item);
    return;
  }
  if (e.target === scrimEl) closePopup();
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closePopup();
  if (e.key === "Enter" && e.target.classList?.contains("word")) {
    openPopup(e.target.dataset.word);
  }
});

scrimEl.addEventListener("click", closePopup);

window.addEventListener("hashchange", () => {
  renderChrome();
  route();
});

// ── Boot ──
async function boot() {
  try {
    const res = await fetch("./content.json", { cache: "no-cache" });
    state.content = await res.json();
  } catch (err) {
    document.getElementById("app").innerHTML = `
      <div class="empty">コンテンツを読み込めませんでした。<br>
      <span style="font-size:0.8em; color:var(--ink-soft);">Could not load content.json. Run <code>python3 _scripts/build_konbini.py</code>.</span></div>
    `;
    return;
  }
  renderChrome();
  route();
}

boot();
