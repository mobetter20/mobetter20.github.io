"""Render the approved newspaper entrances from committed content.

build_root owns Home and stats pages. build_sections owns Writing and Building.
Neither reads a generated page as its content source.
"""
from pathlib import Path
from html import escape, unescape
import hashlib
import json
import re
from types import SimpleNamespace

import build_comedy
import home_catalog
import image_pieces

ROOT = Path(__file__).resolve().parents[1]
BUILDING_SOURCE = ROOT / 'content/building.json'
ASSET_ROOT = ROOT / 'assets/paper'
# Editorial exclusions keep durable reader URLs and source text intact.
UNLISTED_COMEDY_SLUGS = {'10-reasons-why-you-shouldn-t-read-this-list'}
# Publication updates the archive, never this editorial choice.
WRITING_FEATURED_ESSAY_SLUG = 'dear-seoul'
ROUTES = {'home':'/', 'writing':'/is/writing/', 'building':'/is/building/', 'running':'/is/running/'}


def asset(name):
    version = hashlib.sha256((ASSET_ROOT / name).read_bytes()).hexdigest()[:10]
    return f'/assets/paper/{name}?v={version}'


def head(page):
    title = 'ajin.im' if page == 'home' else f'ajin.im is {page}'
    description = {'home':'Writing, cartoons, worlds, and builds by Ajin.', 'writing':'Comedy, cartoons, and other writing by Ajin.', 'building':'Worlds, collections, and individual builds by Ajin.'}[page]
    url = 'https://ajin.im' + ROUTES[page]
    styles = ['home.css'] if page == 'home' else ['claude-front.css', 'paper.css']
    if page == 'writing': styles.append('writing.css')
    if page == 'building': styles.append('building.css')
    stylesheet = ''.join(f'<link rel="stylesheet" href="{asset(name)}">' for name in styles)
    if page == 'building':
        stylesheet = '<link rel="stylesheet" href="/assets/entrances/cabinet.css?v=2026-11-08-night">' + stylesheet
    scripts = f'<script src="{asset("home.js" if page == "home" else "paper.js")}" defer></script>'
    if page == 'writing': scripts += f'<script src="{asset("writing.js")}" defer></script>'
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="ajin.im">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://ajin.im/assets/paper/home-preview.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Writing and builds by Ajin, with an illustrated joke and a Japanese ticket machine.">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/img/a1.png">
<link rel="apple-touch-icon" href="/img/a1.png">
<link rel="alternate" type="application/atom+xml" title="ajin.im writes" href="/writes/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=IBM+Plex+Sans:wght@400;450;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
{stylesheet}{scripts}<script src="/analytics.js" defer></script>'''


def text_only(value):
    return unescape(re.sub('<[^>]+>', '', value)).strip()


def comedy_items():
    medium, standalone = build_comedy.load_posts()
    result = []
    for post in medium:
        result.append({'slug':post.slug, 'title':post.title, 'subtitle':post.subtitle,
            'date':post.date.strftime('%Y·%m'), 'published_date':post.date.date().isoformat(), 'dateline':post.month_label,
            'paragraphs':[text_only(p) for p in re.findall(r'<p\b[^>]*>(.*?)</p>', post.body_html, re.S)]})
    for post in standalone:
        result.append({'slug':post.slug, 'title':post.title, 'subtitle':post.subtitle,
            'date':'', 'published_date':'', 'dateline':'',
            'paragraphs':[text_only(p) for p in re.findall(r'<p\b[^>]*>(.*?)</p>', build_comedy.markdown_to_html(post.body_md), re.S)]})
    return result


def local(page, current=None):
    return ROUTES[page]


def nav(current):
    links = ''.join(f'<a href="{ROUTES[key]}" target="_self" class="{("on" if key == current else "")}"' + (' aria-current="page"' if key == current else '') + f'>{label}</a>' for key,label in [('writing','is writing'),('building','is building')])
    return f'<nav class="folio site-nav" aria-label="Main navigation"><time data-today></time><span class="verbs">{links}</span></nav>'


def header(current, total=0, since=2009, as_of=''):
    mileage = f'<a class="ear" href="/is/running/" target="_self" aria-label="Running since {since}: {total:,} kilometres {escape(as_of)}. View the journey to the Moon."><small>Running since {since}</small><strong>{total:,} km</strong></a>' if current == 'home' else ''
    return f'<div class="cap" aria-hidden="true"></div><header class="plate"><h1><a href="/" target="_self" aria-label="ajin.im home">ajin.im</a></h1>{mileage}</header>{nav(current)}'


def footer(current):
    home_link = '<a href="/" target="_self">ajin.im</a>' if current != 'home' else ''
    return f'<footer class="foot">{home_link}<a href="mailto:hi@ajin.im">hi@ajin.im</a></footer>'


def home_image_lead():
    # Editorially pinned until Ajin requests a different lead. Catalogue growth
    # and featured flags must not silently change the front door.
    piece = next(piece for piece in image_pieces.load_catalog()['pieces']
                 if piece['slug'] == 'austen-at-work')
    return f'''<a class="cartoon" href="/is/writing/austen-at-work/" target="_self">
        <figure>
          <img src="{escape(piece['image'])}" width="{piece['width']}" height="{piece['height']}" alt="{escape(piece['alt'], quote=True)}" fetchpriority="high">
          <figcaption>{escape(piece['caption'])}</figcaption>
        </figure>
      </a>'''


def essay_controls(posts):
    choices = home_catalog.essay_choices(posts)
    if not choices: return ''
    links = ''.join(f'<p id="{item.href.split("/")[2]}"><a href="{escape(item.href,quote=True)}" target="_self" data-essay-slug="{item.href.split("/")[2]}">{escape(item.title)}</a></p>' for item in choices)
    return f'<section class="new-writing liners" aria-label="Recent writing">{links}</section>'


def render_home(total, since, as_of):
    progress = min(100, total / 384400 * 100)
    return f'''<div class="home">
  <header><h1><a href="/" target="_self" aria-label="ajin.im home">ajin.im</a></h1></header>
  <main id="work">
    <section class="writing" aria-labelledby="writing-heading">
      <h2 id="writing-heading"><a href="/is/writing/" target="_self"><em>is</em> writing</a></h2>
      {home_image_lead()}
    </section>
    <section class="building" aria-labelledby="building-heading">
      <h2 id="building-heading"><a href="/is/building/" target="_self"><em>is</em> building</a></h2>
      <a class="machine" href="/is/building/kenbaiki/" target="_blank" rel="noopener" aria-label="Open Kenbaiki, Japanese ticket machine practice, in a new tab">
        <figure>
          <img src="{asset("kenbaiki-preview.png")}" width="511" height="946" alt="Kenbaiki’s ivory soba ticket machine, with Japanese menu buttons, a cash display and a ticket slot.">
          <figcaption><span class="project-name">Kenbaiki</span><span class="project-description">Practise on a Japanese ticket machine.</span></figcaption>
        </figure>
      </a>
    </section>
  </main>
  <aside class="running"><a href="/is/running/" target="_self" aria-label="Running to the Moon. {total:,} kilometres since {since} {escape(as_of)}, {progress:.1f} percent of the distance.">
    <span class="run-title"><em>is</em> running to the Moon</span>
    <span class="route" style="--progress:{progress:.3f}%" aria-hidden="true"><span class="earth">🌍</span><span class="track"><span class="distance"></span><span class="runner">🏃</span></span><span class="moon">🌕</span></span>
    <span class="run-data">{total:,} km since {since}</span>
  </a></aside>
  <footer><a href="mailto:hi@ajin.im">hi@ajin.im</a></footer>
</div>'''


def excerpt(item, start=0, count=1):
    return '<div class="column-copy">' + ''.join(f'<p>{escape(p)}</p>' for p in item['paragraphs'][start:start+count]) + '</div>'

def edition_story(item, cls, paragraphs=1, start=0):
    url = f"/wrote/{item['slug']}/"
    dateline = f"      <small>{item['dateline']}</small>\n" if item['dateline'] else ''
    dek = f'      <p class="edition-dek">{escape(item["subtitle"])}</p>\n' if item['subtitle'] else ''
    return f'''<article class="edition-story {cls}">
{dateline}      <h2><a href="{url}" target="_blank" rel="noopener">{escape(item['title'])}</a></h2>
{dek}      {excerpt(item, start, paragraphs)}
      <a class="read-link" href="{url}" target="_blank" rel="noopener">Continue reading ↗</a>
    </article>'''

def edition_essay(item):
    url = f"/writes/{item['slug']}/"
    return f'''<article class="edition-story edition-brief">
      <h2><a href="{url}" target="_blank" rel="noopener">{escape(item['title'])}</a></h2>
      <div class="column-copy"><p>{escape(item.get('excerpt', ''))}</p></div>
      <a class="read-link" href="{url}" target="_blank" rel="noopener">Continue reading ↗</a>
    </article>'''


def render_writing(essays):
    comedy = comedy_items()
    by_slug = {item["slug"]:item for item in comedy}
    chocolate = by_slug["scientist-would-not-prove-chocolates-as-a-vital-nutrient"]
    step = by_slug["step-on-me-please"]
    pen = by_slug["farewell-to-the-pen-that-just-fell-behind-the-desk"]
    pokemon = by_slug["wife-evolves-into-a-scarier-pokemon"]
    featured_essay = next((item for item in essays if item['slug'] == WRITING_FEATURED_ESSAY_SLUG), None)
    if essays and featured_essay is None:
        raise ValueError(f'Writing selection refers to missing essay: {WRITING_FEATURED_ESSAY_SLUG}')
    # An entirely retracted essay registry is valid, with no empty brief slot.
    essay_slot = f'<div class="edition-bottom">{edition_essay(featured_essay)}</div>' if featured_essay else ''
    archive_items = [
        {"title": item['title'], "href": f"/wrote/{item['slug']}/", "kind": "piece", "published_date": item['published_date']}
        for item in comedy if item['slug'] not in UNLISTED_COMEDY_SLUGS
    ]
    archive_items.extend({"title":item["title"], "href":f"/writes/{item['slug']}/", "kind":"piece", "published_date": item.get('date', '')} for item in essays)
    catalog = image_pieces.load_catalog()
    cartoon = next(piece for piece in catalog['pieces'] if piece['slug'] == catalog['fallback_slug'])
    archive_items.extend({"title": piece['title'], "href": piece['href'], "kind": "image", "published_date": piece['published_date']} for piece in catalog['pieces'])
    # Full publication dates, newest first. Partial dates retain only known
    # precision; undated pieces follow dated work without an invented date.
    archive_items.sort(key=lambda item: tuple(int(part) for part in item['published_date'].split('-')) if item['published_date'] else (), reverse=True)
    archive_rows = ''.join(
        f'''<li data-kind="{item['kind']}"><a href="{item['href']}"{' target="_blank" rel="noopener"' if item['kind'] == 'piece' else ' target="_self"'}>{escape(item['title'])}</a></li>'''
        for item in archive_items
    )

    return header("writing") + f'''<main id="main" class="unified-writing wrap">
      <section id="selection" class="edition-grid" aria-label="Writing" tabindex="-1">
        <p class="archive-entry"><a href="#all">Browse all writing <span aria-hidden="true">→</span></a></p>
        <div class="edition-main">
          {edition_story(chocolate, 'edition-lead', 2)}
          <div class="edition-pair">
            {edition_story(pokemon, 'edition-feature', 2, start=1)}
            {edition_story(pen, 'edition-letter', 2)}
          </div>
          {essay_slot}
        </div>
        <aside class="edition-rail">
          {edition_story(step, 'edition-dispatch', 3)}
          <figure class="edition-cartoon" id="cartoons" tabindex="-1">
            <div class="cartoon-module-heading"><p class="eyebrow">Cartoon</p>
              <a href="/is/writing/cartoons/slides/#cartoon" target="_self">All cartoons <span aria-hidden="true">→</span></a></div>
            <a href="{cartoon['href']}" target="_self" aria-label="Read {escape(cartoon['title'], quote=True)}"><img src="{cartoon['image']}" width="{cartoon['width']}" height="{cartoon['height']}" alt="{escape(cartoon['alt'], quote=True)}"></a>
            <figcaption>{escape(cartoon['caption'])}</figcaption>
          </figure>
          <aside class="edition-sister">
            <p class="eyebrow">Sister publication</p>
            <h2><a href="/is/writing/bird-coo/" target="_blank" rel="noopener">The Municipal Coo</a></h2>
            <p>The newspaper of the Avian Municipal District.</p>
            <a class="read-link" href="/is/writing/bird-coo/" target="_blank" rel="noopener">Read the paper ↗</a>
          </aside>
        </aside>
      </section>
      <section id="all" class="writing-index" aria-labelledby="archive-heading" tabindex="-1">
        <p class="archive-return"><a href="#selection">← Back to writing</a></p>
        <h2 id="archive-heading" class="visually-hidden">Archive</h2>
        <ol id="writing-list" class="writing-list">{archive_rows}</ol>
      </section>
    </main>''' + footer("writing")

def load_building(path=None):
    data = json.loads((path or BUILDING_SOURCE).read_text())
    if data.get('schema_version') != 1 or not isinstance(data.get('projects'),list) or not data['projects']:
        raise ValueError('building catalog needs schema_version 1 and projects')
    seen = set()
    result = []
    for project in data['projects']:
        for key in ('title','href','status','description'):
            if not isinstance(project.get(key),str) or not project[key].strip():
                raise ValueError(f'building project is missing {key}')
        if project['href'] in seen: raise ValueError('duplicate building URL: '+project['href'])
        if not project['href'].startswith(('/', 'https://')): raise ValueError('invalid building URL')
        for key in ('collection','night'):
            if type(project.get(key)) is not bool: raise ValueError(f'building project needs boolean {key}')
        seen.add(project['href'])
        result.append(SimpleNamespace(**project))
    return result


def absolute(href):
    return href

def choice(item, number, main=False):
    night = ' data-room="night"' if item.night else ""
    status = item.status.replace("→", "").strip()
    return f'''<a class="choice {'world' if main else 'build'}" href="{escape(absolute(item.href), quote=True)}" target="_blank" rel="noopener"{night}>
    <span class="label"><span class="label-top"><span>{number:02d}</span><span>{escape(status)}</span></span>
    <span class="choice-title">{escape(item.title)}</span><span class="choice-desc">{escape(item.description)}</span></span>
    <span class="press-face"><span class="light" aria-hidden="true"></span><span>Open</span><span aria-hidden="true">↗</span></span></a>'''

def render_building():
    projects = load_building()
    destinations = [x for x in projects if x.collection]
    pieces = [x for x in projects if not x.collection]
    building_inner = f'''<main class="machine" id="main">
      <div class="top-cap" aria-hidden="true"></div>
      <div class="cabinet-caption"><span>Building</span><span>{len(destinations):02d} worlds &amp; collections · {len(pieces):02d} individual builds</span></div>
      <div class="machine-body"><div class="selection-bay">
        <section class="inventory" aria-label="Worlds and collections">
          <h2 class="group-title"><span>Worlds &amp; collections</span><span>{len(destinations):02d}</span></h2>
          <div class="worlds cabinet-destinations">{''.join(choice(x,i+1,True) for i,x in enumerate(destinations))}</div>
        </section>
        <section class="inventory" aria-label="Individual builds">
          <h2 class="group-title"><span>Individual builds</span><span>{len(pieces):02d}</span></h2>
          <div class="pieces">{''.join(choice(x,i+len(destinations)+1) for i,x in enumerate(pieces))}</div>
        </section>
      </div></div>
      <footer class="service-panel">
        <a class="contact-port" href="mailto:hi@ajin.im"><span class="port-label">CONTACT</span><span class="port-paper">hi@ajin.im <span aria-hidden="true">↗</span></span></a>
      </footer><div class="base" aria-hidden="true"></div>
    </main>'''
    native_header = f'''<header class="marquee"><h1 class="site-heading"><a class="brand" href="{local('home','building')}" target="_self" aria-label="ajin.im home">ajin.im</a></h1>
      <div class="marquee-note">IS BUILDING</div></header>'''
    native_inner = building_inner.replace('<div class="top-cap" aria-hidden="true"></div>', '<div class="top-cap" aria-hidden="true"></div>'+native_header, 1)
    return native_inner
