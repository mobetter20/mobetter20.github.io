# Approved writing releases

This is `~/Documents/Ajin-Publishing/`. Keep drafts in your private writing folder.
Only an approved, top-level `.md` file with `publish: true` is picked up for the
public site. The Mac must be awake and connected.

This guide is installed from the site's
`_scripts/writes_publisher/RELEASE-README.md`. Change that source and update this
copy together. This `_README.md` file is skipped by the publisher.

## Publish a piece

Save the approved release here with this block above the writing:

```markdown
---
title: Your piece title
publish: true
date: 2026-11-21
slug: your-piece-title
excerpt: A complete introductory sentence.
---

Your writing starts here.
```

Use the actual publication date. Only `title` and `publish: true` are required.
An explicit `slug` is recommended: it keeps the URL stable when the title changes.
Use plain `key: value` lines without YAML quotation marks. `date` accepts
`YYYY-MM-DD`, `YYYY-MM` or `YYYY`; use the full date when known. The publisher
assigns its internal ordering number. The excerpt is used if the piece is chosen
for the Writing selection.

After editing stops, the stability wait normally takes 5 to 10 minutes before the
release is pushed. The notice means **pushed; deployment pending**. GitHub Pages
still has to deploy. This watcher does not verify the live page. The expected URL
is `https://ajin.im/writes/your-piece-title/`.

New prose appears in Browse all writing and the prose feed. Publication does not
change the hand-picked Writing selection or Home. For the current choices and
how to change them, use the site's [publishing guide](https://github.com/mobetter20/mobetter20.github.io/blob/master/PUBLISHING.md).

## Edit a published piece

Edit the same approved release file here. Keep its explicit `slug` and publication
date. If the slug was omitted, add the current URL slug before retitling the piece.
The change republishes after the stability wait. Editing a private manuscript
elsewhere does not update the release export.

If the site source was changed independently, publishing stops rather than
overwriting it. Ask the agent to reconcile the two copies. Keep one release file
per URL; every member of a slug collision is held until it is resolved.

## Keep a draft private or take work down

Keep private drafts outside this folder. Omitting `publish: true`, or setting
`publish: false`, prevents a new automatic release.

Deleting an export or changing that flag does **not** retract an existing page.
Ask for either removal from the list or retirement of the direct URL. Retraction
must also prevent this folder from restoring the piece on a later tick.

## Formatting and images

Use ordinary Markdown paragraphs, headings, lists, quotes and public links.
`[[wikilinks]]` are rejected. Local attachments are not copied.

Use **Publish Cartoon.app** for cartoons. Ask the agent to add an illustration to
existing prose. Do not put image files in this folder and expect publication.

If no notice arrives after about 15 minutes, check the Mac is awake and the release
has `publish: true`, then ask the agent to inspect read-only status and logs. Do
not delete publisher state or run its `--dry-run` as a harmless check: that mode
can still fetch, rebase and push.
