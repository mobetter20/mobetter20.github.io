from __future__ import annotations

import html
import os
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo


REPO_ROOT = Path(__file__).resolve().parents[1]
BIRD_COO_ROOT = REPO_ROOT / "is" / "writing" / "bird-coo"
ISSUES_ROOT = BIRD_COO_ROOT / "issues"
SEOUL = ZoneInfo("Asia/Seoul")

SITE_TITLE = "The Municipal Coo"
SITE_SUBTITLE = "Court notices, domestic affairs & district classifieds"
SITE_DISTRICT = "Avian Municipal District"
COURT_FOOTER = "Nest Court of the Avian Municipal District · 14 Municipal Oak, Third Fork · Sycamore District"
FOOTER_COPY = (
    "The Municipal Coo is the local online edition for the Avian Municipal District. "
    "Court notices are published as scheduled. Box replies remain with this publication unless otherwise directed. "
    "All matters domestic."
)


@dataclass(frozen=True)
class AdBlock:
    title: str
    tagline: str
    body_paragraphs: list[str]
    testimonial: str | None = None
    contact_lines: list[str] | None = None


@dataclass(frozen=True)
class Issue:
    issue_number: str
    issue_date: date
    lead_headline: str
    lead_dateline: str
    lead_paragraphs: list[str]
    court_title: str
    court_paragraphs: list[str]
    classified_title: str
    classified_paragraphs: list[str]
    classified_reply: str | None
    personal_title: str
    personal_paragraphs: list[str]
    personal_reply: str
    display_ad: AdBlock
    letter_title: str | None
    letter_paragraphs: list[str]
    letter_signature: str
    letter_editor_note: str | None = None

    @property
    def slug(self) -> str:
        return self.issue_date.isoformat()

    @property
    def date_label(self) -> str:
        return f"{self.issue_date.strftime('%A, %B')} {self.issue_date.day}, {self.issue_date.year}"

    @property
    def archive_label(self) -> str:
        return f"{self.issue_date.strftime('%B')} {self.issue_date.day}, {self.issue_date.year}"


ISSUES = [
    Issue(
        issue_number="01",
        issue_date=date(2026, 4, 6),
        lead_headline="Birch Court Residents Report Recurring Visitor",
        lead_dateline="Birch Court · District Desk",
        lead_paragraphs=[
            'Residents on the west end of Birch Court have reported a male dove visiting the same balcony four evenings in a row. The visits last between forty minutes and two hours. The male has been described as "well-groomed for someone who doesn\'t live here." The balcony\'s occupant has not filed a complaint. Two neighbors have.',
        ],
        court_title="Hearing Notice — AMNC-2026-007B",
        court_paragraphs=[
            'Dove v. Dove. Hearing on the merits scheduled April 14, 2026, 9:30 AM, Chamber B. Both parties ordered to appear in person. The Court reminds the Respondent that "in person" refers to a perch inside the courtroom. The branch visible through the east window is not the courtroom and has never been the courtroom.',
            "Presiding: Hon. M. Owl. Clerk: T. Nuthatch. Public seating limited. Spectators who have already formed opinions are asked to keep them at foraging volume.",
        ],
        classified_title="Nest Materials — Assorted",
        classified_paragraphs=[
            "Two (2) twigs, lightly used. One (1) zip tie, provenance confirmed. Receipt paper (CVS, undated, structural). Quantity of dryer lint. All items currently load-bearing. Seller prefers not to discuss why availability has changed. Collection from meter box, rear of Building C. Bring your own bag. No questions after 6 PM.",
        ],
        classified_reply=None,
        personal_title="Recently Available — Male, Dove",
        personal_paragraphs=[
            '47. Quiet. Previously committed. Good with structural concepts but better at describing them than executing them. Looking for a patient female who values intention. I have been told I am "not unpleasant to be around when I am actually around." South-facing branches preferred. No rush. I have time. I have had time for a while.',
        ],
        personal_reply="Reply to: Box 7B-R, c/o this publication. Character references preferred over recent ones.",
        display_ad=AdBlock(
            title="Karen Hawk",
            tagline="Attorney at Law · Rapid Descents · Clean Separations",
            body_paragraphs=[
                'Specializing in contested nest divisions, emergency no-perch orders, and situations where he says it was "just drinks." Eighteen years of family law experience. Exposed to every version of "it\'s not what it looks like." Still not impressed.',
            ],
            testimonial='"She got me the branch, the eggs, and an apology I could use in future proceedings." — former client',
            contact_lines=[
                "Free consultation · Evening and weekend appointments",
                "I do not do couples counseling. That ship has sailed, sunk, and been entered into evidence.",
            ],
        ),
        letter_title="Perch Usage After Separation",
        letter_paragraphs=[
            'My ex-husband has begun using the same perch I use every afternoon at the south end of the park. He claims it was always his perch. It was not always his perch. I introduced him to that perch in 2023 during what he now calls "a transitional period" but which I call "our marriage."',
            "I am not asking The Municipal Coo to arbitrate. I am asking whether the district has a policy on post-separation perch usage, and if not, why not.",
        ],
        letter_signature="Margaret H., Birch Court",
    ),
    Issue(
        issue_number="02",
        issue_date=date(2026, 4, 13),
        lead_headline="Sycamore Lane Flower Arrangement Sparks Speculation",
        lead_dateline="Sycamore Lane · District Desk",
        lead_paragraphs=[
            "A flower arrangement on the south-facing ledge at 16 Sycamore Lane has been changed for the fourth consecutive month, drawing comment from residents who had previously considered the ledge decorative but not strategic.",
            'The resident responsible, who is known to most of the street and has asked not to be named, confirmed the arrangement is seasonal and "not for anyone in particular." She added that dried lavender was chosen for its calming properties, not because it is visible from two branches and a parking structure.',
            'Three neighbors described the arrangement as "very noticeable." A fourth described it as "pointed." The resident has declined further comment but has since added rosemary.',
        ],
        court_title="Status Update — AMNC-2025-022C",
        court_paragraphs=[
            'Starling v. Starling. Egg custody. Case closed. Final order entered. Custody arrangement approved as submitted: alternating weekends, shared Wednesday evenings, and one floating holiday to be agreed upon annually. The Court reminds both parties that "floating" refers to the schedule, not the method of transport.',
            "Clerk: T. Nuthatch.",
        ],
        classified_title="FOR SALE: One (1) spice rack, wall-mounted",
        classified_paragraphs=[
            "Cedar. Eight compartments. Previously organized alphabetically by someone who is no longer in the household. Current owner does not cook but has retained the rack on principle. Some compartments are empty. Others contain spices purchased in 2022 that may or may not still be active. The oregano smells like a decision made too late.",
            "Asking: reasonable. Will accept sympathy.",
        ],
        classified_reply="Box 022, c/o this publication.",
        personal_title="FEMALE, FINCH, 34",
        personal_paragraphs=[
            'Recently out of a thing. Not looking for another thing. Looking for someone who can sit on a branch without narrating what they see. Strong opinions are fine if they stay inside. Must not describe previous relationships as "learning experiences" in the first conversation. I have been learned from enough.',
            "Evenings only. No owls.",
        ],
        personal_reply="Reply to: Box 34-F.",
        display_ad=AdBlock(
            title="KAREN HAWK, ATTORNEY AT LAW",
            tagline='When "I just need space" means he took the good branch.',
            body_paragraphs=[
                'Emergency no-perch orders filed same day. Contested nest divisions resolved before the eggs get cold. Seventeen years of experience telling males that "thinking about it" is not a legal position.',
            ],
            testimonial='"I called Karen on a Tuesday. By Thursday I had the nest, the eggs, and a clear sightline. He got the drainage pipe and a receipt." — G.F., Sycamore District',
            contact_lines=[
                "Evening appointments. Weekend filings. I answer my phone because your situation will not improve by Monday.",
            ],
        ),
        letter_title=None,
        letter_paragraphs=[
            'I would like to address the bird at the south end of the park who has begun singing at 4:45 AM. I am not opposed to singing. I am opposed to singing that sounds like it was written during a custody hearing and performed for an audience of one ex-wife who lives three trees over and has asked, publicly, for it to stop.',
            "If this is therapy, do it indoors. If this is a performance, sell tickets. If this is grief, I am sorry, but it is also 4:45.",
        ],
        letter_signature="R. Nuthatch, Municipal Oak (no relation to the Clerk)",
    ),
    Issue(
        issue_number="03",
        issue_date=date(2026, 4, 20),
        lead_headline="Disturbance Reported at Birch Court Intersection",
        lead_dateline="Birch Court / Sycamore Lane · District Desk",
        lead_paragraphs=[
            'A verbal altercation between two female doves near the Birch Court intersection on Thursday morning disrupted pedestrian foraging for approximately twelve minutes. Witnesses described the exchange as "direct," "overdue," and "audible from the utility pole."',
            'The dispute reportedly concerned a length of vine that one party described as "a gift" and the other described as "evidence." No physical contact was made, though one witness noted that both parties were "fully puffed," which in her experience indicated either territorial assertion or an unwillingness to be the first to leave.',
            "The vine was left at the scene. It has not been claimed.",
        ],
        court_title="Case Filed — AMNC-2026-009A",
        court_paragraphs=[
            'Wren v. Wren. Noise complaint (domestic). Petitioner alleges Respondent has been "deliberately humming" during shared meal times, creating a hostile dining environment. Respondent denies intent and characterizes the sound as "digestive." Hearing date to be scheduled. The Court notes it has reviewed similar claims before and reminds both parties that digestion, while involuntary, is not typically rhythmic.',
            "Clerk: T. Nuthatch.",
        ],
        classified_title="LOST: Photo album, small, brown cover",
        classified_paragraphs=[
            "Last seen on the shared bookshelf before the move-out. Contains approximately forty images, mostly from the first two seasons. Some are labeled. Most are not, which was fine when we both remembered.",
            "Not valuable except to one party, who is requesting its return, and possibly to the other party, who may not have noticed it is missing, which is the problem in general.",
        ],
        classified_reply="Contact: Box 009, c/o this publication. No reward. Just return it.",
        personal_title="MALE, HERON, 52",
        personal_paragraphs=[
            'Tall. Patient. Comfortable with silence, possibly too comfortable. My last partner said I "made every room feel like a waiting room." I have considered this and I think she was describing a quality.',
            "I enjoy standing in one place for long periods of time. I am told this is \"a lot\" but I believe it demonstrates commitment. Looking for someone who does not require constant motion to feel accompanied.",
            "No sparrows. Nothing personal. I just can't keep up.",
        ],
        personal_reply="Reply to: Box 52-H.",
        display_ad=AdBlock(
            title="PERCH & PERCH FAMILY LAW",
            tagline="Est. 2021 · Sycamore District",
            body_paragraphs=[
                "Martin Perch and Diane Perch have been practicing family law for five years and have yet to take a case personally, which they consider their greatest professional achievement.",
                "Practice Areas: Nest abandonment · Egg custody · Territorial disputes · No-perch orders · Vine provenance · Shared-branch mediation",
            ],
            testimonial='"They were calm when I wasn\'t, organized when I couldn\'t be, and honest about my chances without making me feel like a case number." — anonymous client, AMNC-2025',
            contact_lines=[
                "14 Municipal Oak, Suite 2 (above the Clerk's office)",
                "Consultations by appointment. We do not take walk-ins because the staircase is narrow and emotions are wide.",
            ],
        ),
        letter_title=None,
        letter_paragraphs=[
            "My name is Milo and I am in the second year. I have a question.",
            "If my dad's nest is on Sycamore and my mom's nest is on Birch Court, and I have to fly between them every Wednesday and every other weekend, how many miles do I fly in a year? My teacher said I should estimate but I want the exact number because I am putting it in my journal for the judge.",
            "Thank you.",
        ],
        letter_signature="Milo S., age not specified but clearly young",
        letter_editor_note="Editor's note: The Municipal Coo does not provide navigational calculations. We wish Milo well.",
    ),
    Issue(
        issue_number="04",
        issue_date=date(2026, 4, 27),
        lead_headline="Municipal Park Bench Increasingly Occupied by Single Male, Evenings",
        lead_dateline="Municipal Park · District Desk",
        lead_paragraphs=[
            'A male pigeon has been observed on the third bench of Municipal Park between the hours of 5:30 and 7:15 PM for the past eleven consecutive evenings. The male, who has not been identified by name but has been described by multiple sources as "the one who sighs," sits facing the pond and does not forage, sing, or engage with passersby.',
            'Park maintenance has confirmed the bench is public property and no reservation system exists, "despite what some birds seem to believe about their afternoons."',
            'A female robin who uses the adjacent bench for her evening routine said she initially found his presence "melancholy," then "familiar," then "honestly a little annoying, because he keeps looking at the water like it owes him something."',
            'The male was approached by this publication for comment. He said he was fine.',
        ],
        court_title="Hearing Notice — AMNC-2026-007B (Continued)",
        court_paragraphs=[
            "Dove v. Dove. The hearing previously scheduled for April 14, 2026 will proceed as calendared. Counsel for neither party has been retained, as both continue to represent themselves. The Court has been informed that the Respondent may attempt to introduce a character witness. The Court reminds the Respondent that a character witness should speak to the Respondent's character, not to the inadequacy of the Petitioner's, and that the distinction has historically been lost on doves.",
            "Presiding: Hon. M. Owl.",
        ],
        classified_title="FREE: Self-help books, assorted",
        classified_paragraphs=[
            'Twelve titles. Topics include boundaries, attachment styles, co-dependency, and "the language of leaving." All purchased in a two-week period in January. Three have been opened. One has been underlined. The underlined passages are about recognizing when you are the problem, which the owner would like noted was a brave thing to underline even if no subsequent action was taken.',
            "Available immediately. Pickup from drainage pipe adjacent to Building C, east side. Ask for Greg. Or don't. He's there.",
        ],
        classified_reply=None,
        personal_title="SEEKING: Walking partner, female, any species",
        personal_paragraphs=[
            'Not a date. Genuinely just walking. My therapist — well, the owl I talk to on Tuesdays who may or may not be a licensed therapist — suggested I "re-enter social environments without expectations." This is that.',
            "Route: Municipal Park loop, Wednesday evenings, 6 PM. Pace: slow. Conversation: optional. If we happen to enjoy each other's company, I will not mention it until the fourth walk. I have been told I rush things. I have also been told I wait too long. I am looking for the window between those.",
        ],
        personal_reply="Reply to: Box 88-P.",
        display_ad=AdBlock(
            title="KAREN HAWK, ATTORNEY AT LAW",
            tagline='If he calls it "thinking," I call it billing.',
            body_paragraphs=[
                "Now accepting new clients for the spring filing season. Nest abandonment claims processed within 48 hours. Emergency no-perch orders available on weekends.",
            ],
            testimonial='"She didn\'t sugarcoat it. She said, \'He left, you locked it, the Court will decide who was faster.\' Then she won." — D.D., Sycamore Lane',
            contact_lines=[
                "Karen Hawk does not offer marriage counseling, reconciliation services, or sympathy. She offers results, receipts, and a very clear retainer agreement.",
            ],
        ),
        letter_title=None,
        letter_paragraphs=[
            "I am writing to ask whether other readers have experienced the following: you are sitting on the branch with your partner of nine years, the evening is warm, the light is good, and neither of you has anything to say. Not because you are at peace. Because you have both run out of ways to describe the same dissatisfaction without starting the same argument.",
            "I am not writing to complain. I am writing because I saw your classified section and realized I have begun reading personal ads for birds I will never contact, just to remember what it sounds like when someone is still hopeful.",
            "Is that normal?",
        ],
        letter_signature="Name withheld, west district",
    ),
    Issue(
        issue_number="05",
        issue_date=date(2026, 5, 4),
        lead_headline="Noise Complaint Filed Against Morning Singer; Singer Files Counter-Complaint",
        lead_dateline="Municipal Oak · District Desk",
        lead_paragraphs=[
            "The unidentified male bird previously reported for singing at 4:45 AM near the south end of Municipal Park has filed a counter-complaint against the resident who complained about him in a recent letter to this publication.",
            'The original complaint, submitted by R. Nuthatch of Municipal Oak, described the singing as disruptive, therapeutic in nature, and "performed for an audience of one ex-wife." The singer, who has now identified himself as Conrad, disputes this characterization. In his counter-filing he states that the singing is "artistic expression" and that R. Nuthatch\'s letter constituted "public shaming of a bird in recovery."',
            'R. Nuthatch has responded by stating that recovery "does not require an amplifier."',
            'The matter has been referred to the Clerk\'s office. The Clerk\'s office has indicated it will address the filing "in due course," which historically means when the Clerk feels like it.',
        ],
        court_title="New Filing — AMNC-2026-011A",
        court_paragraphs=[
            'Municipal District v. Conrad (species: Mockingbird). Noise/nuisance. Filed by the Clerk\'s office on behalf of three residents of Municipal Oak and one resident of Sycamore Lane who submitted a joint petition describing the Respondent\'s pre-dawn vocal performances as "emotionally specific and therefore worse than random noise." Hearing to be scheduled.',
            "Clerk: T. Nuthatch. The Clerk notes for the record that he lives on Municipal Oak and has recused himself from commentary but not from filing.",
        ],
        classified_title="WANTED: One (1) zip tie",
        classified_paragraphs=[
            "Must be load-bearing. Color immaterial. Previous ownership acceptable if provenance is not contested. Needed for nest repair following structural reassessment.",
            'Buyer is aware that zip ties are available at hardware stores. Buyer does not wish to visit the hardware store because the hardware store is next to the branch where her ex-husband now conducts what he calls "consulting." Buyer will pay above market rate for delivery.',
        ],
        classified_reply="Box 014, c/o this publication. Discretion appreciated.",
        personal_title="MALE, OWL, 61",
        personal_paragraphs=[
            "Judicial temperament. Patient within reason. Reason is a finite municipal resource. Looking for companionship that does not require me to explain what I meant by what I said. I said what I said.",
            "Evenings only. I am not available during business hours and I am not available to discuss why. Interested parties should be comfortable with silence, low lighting, and the occasional professional frustration brought home in the form of a stare.",
            "No doves. I cannot do another dove.",
        ],
        personal_reply="Reply to: Box 61-O. Correspondence only. Do not approach the bench.",
        display_ad=AdBlock(
            title="PERCH & PERCH FAMILY LAW",
            tagline="Your nest. Your eggs. Your terms.",
            body_paragraphs=[
                "Spring filing season is here. If you've been thinking about it since January, you've been thinking about it long enough.",
                "Now handling: Contested vine claims · Pre-nesting agreements · Shared-branch dissolution · Post-separation perch disputes",
            ],
            testimonial='"I kept saying I\'d deal with it next season. Diane Perch said, \'It is next season.\' That was the conversation I needed." — client, 2026',
            contact_lines=[
                "14 Municipal Oak, Suite 2",
                "Walk-ins now accepted on Tuesdays. The staircase has been widened.",
            ],
        ),
        letter_title=None,
        letter_paragraphs=[
            "My wife and I used to read The Municipal Coo together on Sunday mornings. She would read the classifieds out loud in a voice she thought was funny. I would pretend to be annoyed. This was the best part of the week for six years.",
            "She moved to the coast in February. I still get the paper. I don't read the classifieds out loud because it isn't funny when you do it alone.",
            "I'm not sure why I'm writing this. Maybe because the classifieds section looked smaller this week and I wanted someone else to notice.",
        ],
        letter_signature="Arthur P., Sycamore Lane",
        letter_editor_note="Editor's note: The classifieds section has not changed in size.",
    ),
]


def today_in_seoul() -> date:
    override = os.environ.get("BIRD_COO_BUILD_DATE")
    if override:
        return date.fromisoformat(override)
    return datetime.now(SEOUL).date()


def text(value: str) -> str:
    return html.escape(value, quote=False)


def build_paragraphs(paragraphs: list[str]) -> str:
    return "\n".join(f"<p>{text(paragraph)}</p>" for paragraph in paragraphs)


def footer_link_html(href: str, label: str) -> str:
    return f'<a href="{html.escape(href, quote=True)}">{text(label)}</a>'


def issue_page_html(
    issue: Issue,
    *,
    styles_href: str,
    analytics_href: str,
    archive_href: str,
    canonical_href: str,
) -> str:
    classified_reply = (
        f'\n<div class="box-reply">{text(issue.classified_reply)}</div>' if issue.classified_reply else ""
    )
    letter_editor_note = (
        f'\n<div class="editor-note">{text(issue.letter_editor_note)}</div>' if issue.letter_editor_note else ""
    )
    letter_title = f'\n<h4>{text(issue.letter_title)}</h4>' if issue.letter_title else ""
    ad_testimonial = (
        f'\n<div class="ad-testimonial">{text(issue.display_ad.testimonial)}</div>'
        if issue.display_ad.testimonial
        else ""
    )
    ad_contact = ""
    if issue.display_ad.contact_lines:
        ad_contact = (
            '\n<div class="ad-contact">\n'
            + "\n".join(f"<p>{text(line)}</p>" for line in issue.display_ad.contact_lines)
            + "\n</div>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{text(SITE_TITLE)} — {text(issue.archive_label)}</title>
<meta name="description" content="{html.escape(issue.lead_headline, quote=True)}">
<link rel="canonical" href="{html.escape(canonical_href, quote=True)}">
<link rel="stylesheet" href="{html.escape(styles_href, quote=True)}">
<script src="{html.escape(analytics_href, quote=True)}" defer></script>
</head>
<body>

<div class="page">

<header class="masthead">
<div class="mast-district">{text(SITE_DISTRICT)}</div>
<h1 class="mast-title">{text(SITE_TITLE)}</h1>
<div class="mast-subtitle">{text(SITE_SUBTITLE)}</div>
<div class="mast-meta">
<span>{text(issue.date_label)}</span>
<span>Online Edition</span>
<span>Est. unrecorded</span>
</div>
</header>

<nav class="nav">
<a href="#district">District</a>
<a href="#court">Court Notices</a>
<a href="#classifieds">Classifieds</a>
<a href="#personals">Personals</a>
<a href="#services">Services</a>
<a href="#letters">Letters</a>
</nav>

<main class="content">

<article class="lead-story" id="district">
<div class="section-label">Around the District</div>
<h2 class="lead-headline">{text(issue.lead_headline)}</h2>
<div class="lead-dateline">{text(issue.lead_dateline)}</div>
<div class="lead-text">
{build_paragraphs(issue.lead_paragraphs)}
</div>
</article>

<hr class="section-rule heavy">

<div class="section-label" id="court">Court Notices</div>
<div class="court-notice">
<div class="court-notice-header">Avian Municipal Nest Court — Branch Division</div>
<h3>{text(issue.court_title)}</h3>
{build_paragraphs(issue.court_paragraphs)}
<div class="court-notice-footer">{text(COURT_FOOTER)}</div>
</div>

<hr class="section-rule">

<div class="columns-2" id="classifieds">

<div class="classified">
<div class="section-label">Classified</div>
<h4>{text(issue.classified_title)}</h4>
{build_paragraphs(issue.classified_paragraphs)}{classified_reply}
</div>

<div class="personal" id="personals">
<div class="section-label">Personal</div>
<h4>{text(issue.personal_title)}</h4>
{build_paragraphs(issue.personal_paragraphs)}
<div class="box-reply">{text(issue.personal_reply)}</div>
</div>

</div>

<hr class="section-rule heavy">

<div id="services">
<div class="display-ad">
<h3>{text(issue.display_ad.title)}</h3>
<div class="ad-tagline">{text(issue.display_ad.tagline)}</div>
<div class="ad-body">
{build_paragraphs(issue.display_ad.body_paragraphs)}
</div>{ad_testimonial}{ad_contact}
</div>
</div>

<hr class="section-rule">

<div class="letter" id="letters">
<div class="section-label">Letters</div>
<h3 class="letter-section-head">Letters to the Editor</h3>
<div class="letter-disclaimer">Letters may be edited for length and clarity. Views expressed are the author's.</div>
{letter_title}
<div class="salutation">Dear Editor,</div>
<div class="letter-body">
{build_paragraphs(issue.letter_paragraphs)}
</div>
<div class="sig">— {text(issue.letter_signature)}</div>{letter_editor_note}
</div>

</main>

<footer class="page-footer">
<p>{text(FOOTER_COPY)}</p>
<p>{footer_link_html(archive_href, "Past Issues")}</p>
</footer>

</div>

</body>
</html>
"""


def archive_page_html(
    published_issues: list[Issue],
    current_issue: Issue,
    *,
    styles_href: str,
    analytics_href: str,
    canonical_href: str,
) -> str:
    if published_issues:
        items = []
        for issue in reversed(published_issues):
            current_badge = " · Current" if issue == current_issue else ""
            current_class = " current" if issue == current_issue else ""
            items.append(
                f"""<article class="archive-item{current_class}">
<a href="./{issue.slug}.html">
<div class="archive-meta">
<span>Issue {text(issue.issue_number)}{text(current_badge)}</span>
<span>{text(issue.archive_label)}</span>
</div>
<h2 class="archive-title">{text(issue.lead_headline)}</h2>
<p class="archive-summary">{text(issue.lead_dateline)}</p>
</a>
</article>"""
            )
        archive_items = "\n".join(items)
    else:
        archive_items = '<p class="archive-empty">No issues have been published yet.</p>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{text(SITE_TITLE)} Archive</title>
<meta name="description" content="Past issues of The Municipal Coo">
<link rel="canonical" href="{html.escape(canonical_href, quote=True)}">
<link rel="stylesheet" href="{html.escape(styles_href, quote=True)}">
<script src="{html.escape(analytics_href, quote=True)}" defer></script>
</head>
<body>

<div class="page">
<header class="masthead">
<div class="mast-district">{text(SITE_DISTRICT)}</div>
<h1 class="mast-title">{text(SITE_TITLE)}</h1>
<div class="mast-subtitle">Archive of published issues</div>
<div class="mast-meta">
<span>{text(current_issue.date_label)}</span>
<span>Issue Archive</span>
<span>Published editions</span>
</div>
</header>

<div class="archive-shell">
<p class="archive-intro">Past and current issues of The Municipal Coo are listed below in reverse chronological order. Future editions are withheld until publication.</p>
<section class="archive-list">
{archive_items}
</section>
</div>

<footer class="page-footer">
<p>{footer_link_html('../index.html', 'Return to current issue')}</p>
</footer>
</div>

</body>
</html>
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    build_date = today_in_seoul()
    current_issue = next((issue for issue in reversed(ISSUES) if issue.issue_date <= build_date), ISSUES[0])
    published_issues = [issue for issue in ISSUES if issue.issue_date <= build_date]

    for issue in ISSUES:
        write_text(
            ISSUES_ROOT / f"{issue.slug}.html",
            issue_page_html(
                issue,
                styles_href="../styles.css",
                analytics_href="../../../../analytics.js",
                archive_href="./index.html",
                canonical_href=f"https://ajin.im/is/writing/bird-coo/issues/{issue.slug}.html",
            ),
        )

    write_text(
        ISSUES_ROOT / "index.html",
        archive_page_html(
            published_issues,
            current_issue,
            styles_href="../styles.css",
            analytics_href="../../../../analytics.js",
            canonical_href="https://ajin.im/is/writing/bird-coo/issues/",
        ),
    )

    write_text(
        BIRD_COO_ROOT / "index.html",
        issue_page_html(
            current_issue,
            styles_href="./styles.css",
            analytics_href="../../../analytics.js",
            archive_href="./issues/index.html",
            canonical_href="https://ajin.im/is/writing/bird-coo/",
        ),
    )

    print(
        f"Built The Municipal Coo for {build_date.isoformat()} "
        f"(current issue: {current_issue.issue_number} / {current_issue.slug})."
    )


if __name__ == "__main__":
    main()
