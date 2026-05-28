from __future__ import annotations

import html
import os
import re
from dataclasses import dataclass, replace
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo


REPO_ROOT = Path(__file__).resolve().parents[1]
BIRD_COO_ROOT = REPO_ROOT / "is" / "writing" / "bird-coo"
ISSUES_ROOT = BIRD_COO_ROOT / "issues"
AVIAN_DISTRICT_INDEX = REPO_ROOT / "is" / "writing" / "avian-district" / "index.html"
SEOUL = ZoneInfo("Asia/Seoul")

AVIAN_EXCERPT_PATTERN = re.compile(
    r"<!-- COO-EXCERPT-START.*?<!-- COO-EXCERPT-END -->",
    re.DOTALL,
)

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


KAREN_HAWK_AD = AdBlock(
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
)


LIONEL_KINGFISHER_AD = AdBlock(
    title="Lionel Kingfisher, Investigations",
    tagline="Discreet Observation · Hand-Illustrated Reports",
    body_paragraphs=[
        "I watch, I wait, and I render what I see in ink. I will document comings, goings, and the occasional male who paused at the gate longer than he meant to.",
        "In the interest of honesty: I grow attached to my subjects. By the second day I am usually on their side. If you need someone caught, I am not your bird. If you need someone seen, I am taking new clients.",
    ],
    testimonial='"He did not find what I asked for. He found something kinder, which I did not want and have not stopped thinking about." — former client',
    contact_lines=[
        "Rates negotiable and frequently waived. Bird seed accepted.",
        "Find me at the south parking lot. I am the blue one.",
    ],
)


PEARL_MAGPIE_AD = AdBlock(
    title="Pearl Magpie · Nest Appraisal & Division",
    tagline="Every Twig Valued · Nothing Overlooked · Equitable to a Fault",
    body_paragraphs=[
        "When a nest comes apart, someone has to say what it was all worth. I am a magpie. I have been valuing bright things since before I could fly, and I do not miss much.",
        "I will catalogue the nest, price every item — the load-bearing, the decorative, the one he swears is his — and divide the whole down the middle. You will be surprised what you were sitting on.",
    ],
    testimonial="\"She valued things we had stopped seeing. Her fee was three of them. I cannot say the division was unfair — only that she did very well out of it.\" — former client",
    contact_lines=[
        "Consultations by appointment. References on request.",
        "Payment accepted in coin or equivalent shine.",
    ],
)


ISSUES = [
    Issue(
        issue_number="01",
        issue_date=date(2026, 3, 10),
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
        issue_date=date(2026, 3, 17),
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
        issue_date=date(2026, 3, 24),
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
        issue_date=date(2026, 3, 31),
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
        issue_date=date(2026, 4, 7),
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
    Issue(
        issue_number="06",
        issue_date=date(2026, 4, 14),
        lead_headline="Dove v. Dove Hearing Concludes; Ruling Expected",
        lead_dateline="Nest Court, Chamber B · Court Desk",
        lead_paragraphs=[
            "The hearing on the merits in Dove v. Dove (AMNC-2026-007B) concluded Monday after approximately ninety minutes of testimony. Both parties appeared pro se. A witness for the Petitioner was also heard.",
            "Details of the testimony have not been released, though the Clerk's office confirmed that a six-page supplemental filing by the witness was entered into the record over the objection of no one, because no one had been asked.",
            'Hon. M. Owl is expected to issue a ruling within ten business days. The Court has reminded both parties that "business days" does not include weekends, holidays, or days when the Clerk is not in the mood to process paperwork.',
            "The disputed nest at 14 Sycamore Lane, Lot 7, remains occupied by the Petitioner and two unhatched eggs.",
        ],
        court_title="Scheduling — AMNC-2026-009A",
        court_paragraphs=[
            'Wren v. Wren. Noise complaint (domestic). Hearing scheduled May 12, 2026, 10:00 AM, Chamber B. The Petitioner is reminded to bring documentation of the alleged humming. The Respondent is reminded that "I don\'t even know I\'m doing it" has been attempted before and did not succeed.',
            "Clerk: T. Nuthatch.",
        ],
        classified_title="FOR SALE: Nest, south-facing, recently vacated",
        classified_paragraphs=[
            "Location: elm adjacent to Municipal Oak. Two-fork construction. Upper canopy. Morning light. Previous occupants departed amicably, which in this case means they stopped speaking and one of them left during a rainstorm.",
            'Structurally sound. Some cosmetic wear near the entrance where the door was slammed, which is not a thing nests have, but this one somehow does.',
        ],
        classified_reply="Viewing by appointment. Box 006, c/o this publication.",
        personal_title="FEMALE, ROBIN, 39",
        personal_paragraphs=[
            'I was going to write something clever here but I\'ve been on four dates this spring and all of them described themselves as "not like other birds" and all of them were exactly like other birds.',
            'I like mornings. I like worms. I like knowing where someone is without having to ask. If you are the kind of male who disappears for eleven days and calls it "thinking," I have already dated you and I did not enjoy it.',
            "Employed. Stable. My branch is my own and I am not sharing it until I'm sure.",
        ],
        personal_reply="Reply to: Box 39-R. Be normal.",
        display_ad=AdBlock(
            title="KAREN HAWK, ATTORNEY AT LAW",
            tagline="Spring cleaning isn't just for nests.",
            body_paragraphs=[
                "Filing season is not a metaphor. If you have been sitting on a decision since winter, the eggs are not going to hatch themselves and neither is your resolve.",
                "Karen Hawk has filed more nest abandonment claims this quarter than any other practitioner in the district. This is not a boast. It is a municipal statistic.",
            ],
            testimonial='"I told Karen I wasn\'t ready. She said, \'You called me. That was the ready part.\'" — former client',
            contact_lines=[
                "Consultations available. No retainer required for initial assessment. I do require honesty, which is more than most of your partners managed.",
            ],
        ),
        letter_title=None,
        letter_paragraphs=[
            "I would like to respond to the resident of Birch Court who wrote to complain about post-separation perch usage.",
            "I am the ex-husband in question. The perch at the south end of the park was not \"introduced\" to me. I found it independently in 2022, before we were even paired. I have a witness. The witness is my mother, who I acknowledge may not be considered impartial, but who has been using the perch longer than either of us.",
            "I am not following my ex-wife. I am following my routine. If she finds my presence upsetting, I suggest she adjust her schedule. I adjusted mine for nine years. It did not help.",
        ],
        letter_signature="Gerald H., Sycamore Lane",
    ),
    Issue(
        issue_number="07",
        issue_date=date(2026, 4, 21),
        lead_headline='Third Bench Occupant Identified; Says He Is "Between Situations"',
        lead_dateline="Municipal Park · District Desk",
        lead_paragraphs=[
            "The male pigeon who has been sitting on the third bench of Municipal Park most evenings since late March has been identified as Dennis.",
            'Dennis, who declined to give a surname, confirmed that he visits the bench "most days" and described himself as "between situations." When asked what situations, he said, "All of them."',
            'Neighbors have expressed a range of reactions. One regular jogger described Dennis as "part of the scenery now, like the broken fountain." A female sparrow who uses the adjacent path said she initially found him concerning but has since started bringing extra seed, "not because he asked, but because he never does, which is worse."',
            'Dennis was asked whether he planned to continue visiting the bench. He said he hadn\'t planned anything in a while and that was "sort of the whole thing."',
        ],
        court_title="Ruling Issued — AMNC-2026-007B",
        court_paragraphs=[
            "Dove v. Dove. Nest abandonment. The Court has issued its ruling. The full text is available through the Clerk's office and will be posted to the eCourt Public Portal within five business days.",
            "The Clerk's office asks that parties seeking copies form an orderly line and refrain from editorializing while waiting.",
        ],
        classified_title="FOUND: One (1) length of vine, unclaimed",
        classified_paragraphs=[
            "Discovered at the intersection of Birch Court and Sycamore Lane following the incident reported two weeks ago. Approximately eighteen inches. Good structural quality. Would support a small to medium nest modification.",
            "Owner may claim by describing the vine and explaining, to the satisfaction of the Clerk, why it was at that intersection. The Clerk has set a low bar for satisfaction but expects at minimum a complete sentence.",
        ],
        classified_reply="Contact: Clerk's Office, 14 Municipal Oak. Not the newspaper. We are not a lost and found. We keep printing these because people keep losing things near arguments.",
        personal_title="MALE, CROW, 44",
        personal_paragraphs=[
            'Intelligent. Resourceful. Remembers faces, which my ex-wife has described in legal documents as "unsettling." I prefer "attentive."',
            'I collect things. Small things. Bright things. I have been told this is "a lot." I have also been told the collection cannot live in the shared space, which is why it now lives in a storage unit I visit on Wednesdays, which is also when I feel most like myself.',
            "Looking for someone who understands that devotion and inconvenience are often the same bird.",
        ],
        personal_reply="Reply to: Box 44-C. I will remember your letter.",
        display_ad=AdBlock(
            title="PERCH & PERCH FAMILY LAW",
            tagline="Vine disputes. Branch rights. The conversation you've been avoiding.",
            body_paragraphs=[
                'Martin Perch has been asked, "Is it too late?" four hundred and twelve times. The answer has never been yes. It has occasionally been "it depends on what you mean by \'late.\'"',
                "Now handling: Post-ruling compliance · Visitation schedule modification · Cross-branch easements · The vine thing (yes, we saw the paper)",
            ],
            testimonial='"Diane told me the law wouldn\'t fix my marriage but it would clarify whose lamp that was. She was right about both." — client, 2026',
            contact_lines=[
                "14 Municipal Oak, Suite 2. Tuesdays and Thursdays by appointment.",
            ],
        ),
        letter_title=None,
        letter_paragraphs=[
            "Thank you for printing my letter. My teacher saw it and said I should not be writing to newspapers during school. But my dad said The Municipal Coo is \"not technically a newspaper\" so it's fine.",
            "I calculated the miles. It is 1.4 miles each way. That is 2.8 miles per round trip. I make the trip 6.5 times per month (every other weekend is 2, plus Wednesdays is 4.3, but one Wednesday got canceled because Mom had a thing).",
            "That is 18.2 miles per month. My teacher said to round it. I said I would rather not.",
        ],
        letter_signature="Milo S.",
        letter_editor_note="Editor's note: The Municipal Coo is technically a newspaper.",
    ),
    Issue(
        issue_number="08",
        issue_date=date(2026, 4, 28),
        lead_headline="Conrad Performs Unauthorized Dawn Concert; Three Residents File Joint Complaint",
        lead_dateline="Municipal Oak · District Desk",
        lead_paragraphs=[
            'Conrad, the mockingbird currently facing a noise/nuisance charge (AMNC-2026-011A), performed what witnesses described as a "forty-five-minute set" beginning at 4:32 AM on Saturday, thirteen days before his scheduled hearing.',
            'The performance, which neighbors say included original material as well as "impressions of what sounded like an argument between two doves," drew three new formal complaints and one unsigned note that read simply, "We know it\'s you."',
            "Conrad has not responded to requests for comment but was observed on the same branch Sunday morning at approximately 4:40 AM, tuning.",
            'His attorney, understood to be representing himself, has not filed any pre-hearing motions. The Clerk\'s office has confirmed the hearing will proceed as scheduled and has added a line to the docket description: "Respondent is advised that continued performances may be interpreted as contempt of quiet."',
        ],
        court_title="Pre-Hearing Advisory — AMNC-2026-011A",
        court_paragraphs=[
            'Municipal District v. Conrad. Noise/nuisance. Hearing remains scheduled for May 19, 2026. The Court wishes to clarify that the Respondent\'s right to artistic expression is acknowledged and that the Court\'s concern is limited to volume, timing, and what three witnesses have independently described as "emotional targeting."',
            "The Respondent is further advised that performing outside the Clerk's window at 5 AM on a filing day did not go unnoticed.",
        ],
        classified_title="FOR SALE: Wedding band, gold-tone (second listing)",
        classified_paragraphs=[
            'Previously listed in Issue 01. Band remains unsold. Seller has reduced expectations. Originally described as "lightly scratched." Seller now concedes the scratch is deep and probably symbolic.',
            "Engraving has been confirmed as fully illegible. Seller no longer considers this an improvement. Seller considers it accurate.",
            'Will accept any reasonable offer. "Reasonable" here means someone who will not ask follow-up questions about the engraving, the scratch, or the nine years between purchase and listing.',
        ],
        classified_reply="Box 041, c/o this publication. Final listing.",
        personal_title="SEEKING: Dining companion, any species, no expectations",
        personal_paragraphs=[
            "Not a date. Dinner. Specifically, dinner at a table, because eating alone on a branch has started to feel like a portrait of something I would rather not become.",
            "I can hold a conversation. I can also hold a silence. I have recently learned the difference between the two, which I wish I had learned earlier and under better circumstances.",
            "Tuesday evenings preferred. I will suggest a place. You may veto the place. This is already more negotiation than my last relationship managed.",
        ],
        personal_reply="Reply to: Box 71-D. Genuine replies only. I'll know the difference.",
        display_ad=AdBlock(
            title="KAREN HAWK, ATTORNEY AT LAW",
            tagline="You don't need a reason to call. You already have one.",
            body_paragraphs=[
                'A reminder from this office: consultations are free, confidential, and do not constitute a commitment to filing. They constitute a conversation with someone who will not tell you to "try harder" or "give it time."',
                'If your partner has described the relationship as "evolving," I can tell you what it is evolving into. I have seen it four hundred times and it is always the same shape.',
            ],
            contact_lines=[
                "Karen Hawk. Family law. Eighteen years. Still answering the phone.",
            ],
        ),
        letter_title=None,
        letter_paragraphs=[
            "My wife and I have not spoken about anything of substance in four months. We discuss groceries, weather, and which bin goes out on Tuesdays. Last week she asked if I wanted tea and I said yes and she made it and we drank it and neither of us said anything else for the rest of the evening.",
            'I am not writing because I want advice. I am writing because I saw the personal ad from the heron who described himself as "comfortable with silence, possibly too comfortable" and I realized I had been nodding while reading it.',
            "I don't know what to do with that. But I thought someone should know it happened.",
        ],
        letter_signature="Name withheld, west district",
    ),
    Issue(
        issue_number="09",
        issue_date=date(2026, 5, 5),
        lead_headline="Conrad Noise Hearing Draws Unexpected Attendance",
        lead_dateline="Nest Court, Chamber B · Court Desk",
        lead_paragraphs=[
            'The hearing in Municipal District v. Conrad (AMNC-2026-011A) took place Monday to what the Clerk\'s office described as "the fullest gallery since Finch v. Finch."',
            'Conrad, representing himself, arrived with prepared remarks and what he described as "a contextual performance sample." Hon. M. Owl denied the sample before it began.',
            'Testimony from three residents of Municipal Oak described the pre-dawn performances as "impossible to sleep through," "deliberately aimed at specific windows," and, from one witness, "honestly pretty good, which makes it worse."',
            'Conrad argued that his singing constituted protected expression. The Court noted that protection does not extend to 4:30 AM or to material that two witnesses independently identified as "a reenactment of someone else\'s divorce."',
            'A ruling is expected within the week. Conrad was observed on his usual branch at approximately 5:15 AM the following morning. He was not singing. He was, according to one neighbor, "sitting there in a way that felt like a warning."',
        ],
        court_title="New Filing — AMNC-2026-014B",
        court_paragraphs=[
            'Pigeon v. Pigeon. Nest abandonment (uncontested). Filed by the Petitioner, who noted in her petition that the Respondent "has been on a bench." The Respondent did not contest the filing. The Respondent has not contested anything in some time. Hearing waived by mutual agreement. Default ruling to follow.',
            "Clerk: T. Nuthatch.",
        ],
        classified_title="WANTED: Bench companion, Municipal Park, third bench",
        classified_paragraphs=[
            'Not a personal ad. A bench request. The third bench at Municipal Park has been occupied most evenings by one individual for the past several weeks. That individual would not describe himself as lonely. He would describe himself as "present."',
            "However. If another bird were to occasionally use the other end of the bench, at a respectful distance, without initiating conversation but not actively avoiding it either, that would not be unwelcome.",
            "No pigeons. He is already the pigeon. One per bench is enough.",
            "Evenings, 5:30 to 7:15. The bench will be there. So will he.",
        ],
        classified_reply=None,
        personal_title="FEMALE, DOVE, 41",
        personal_paragraphs=[
            'I have recently concluded a legal matter and I am told the healthy thing to do is "put myself out there." I am out here. I am not sure what comes next.',
            'I am organized. I keep records. I know what I contributed and I have the paperwork to prove it, though I have been told that bringing paperwork to a first date is "not the energy." I am working on the energy.',
            "I want someone who shows up. Not eventually. Not after thinking about it. Just shows up, with no speech about what they were doing instead.",
            "I have two eggs. They are not negotiable.",
        ],
        personal_reply="Reply to: Box 41-D. Serious inquiries only. I will check references.",
        display_ad=AdBlock(
            title="PERCH & PERCH FAMILY LAW",
            tagline="Sometimes the bravest thing is the paperwork.",
            body_paragraphs=[
                "If you've read this far into the classifieds, you're looking for something. It might be a nest. It might be a lamp. It might be permission to stop pretending the branch is fine.",
                'Diane Perch has heard "I just want what\'s fair" one thousand times. She has also heard what "fair" means to each person and it is never the same twice.',
                "We don't take sides. We take instructions. Then we do the work so you can stop doing the math at 2 AM.",
            ],
            contact_lines=[
                "14 Municipal Oak, Suite 2. We're upstairs. The climb is worth it.",
            ],
        ),
        letter_title=None,
        letter_paragraphs=[
            "The bench at the south end of the park has two birds on it now. I noticed on Thursday. The pigeon is still there. The other one is a starling, I think. They don't appear to be speaking.",
            "I mention this because I walk past that bench every evening and for weeks it was just the one bird and it was the saddest thing on my route. I had started timing my walks to avoid it.",
            "Now there are two, and they are both facing the water, and neither of them seems to need anything from the other, and I don't know why that's better but it is.",
        ],
        letter_signature="F. Lark, Municipal Park loop",
    ),
    Issue(
        issue_number="10",
        issue_date=date(2026, 5, 12),
        lead_headline="Conrad Noise Ruling: Restricted Hours, No Restrictions on Feeling",
        lead_dateline="Nest Court, Chamber B · Court Desk",
        lead_paragraphs=[
            "Hon. M. Owl has issued the ruling in Municipal District v. Conrad (AMNC-2026-011A).",
            'The Court found that the Respondent\'s pre-dawn vocal performances constituted a noise disturbance under Avian Municipal Ordinance 9.3(a), but declined to impose a full singing ban.',
            'Instead, the Court has ordered a "quiet hours" restriction prohibiting amplified or sustained vocal performance between 9 PM and 6:30 AM. The Court\'s written opinion noted: "The Respondent is permitted to feel whatever he feels. He is not permitted to feel it at volume before sunrise."',
            "Conrad was observed leaving the courtroom without comment. By Wednesday he had been heard singing at 6:34 AM, which technically complies.",
            'R. Nuthatch of Municipal Oak, who filed the original complaint, told this publication the ruling was "a start." He then added, "Four minutes past the limit is not compliance. It is a position."',
        ],
        court_title="Default Ruling Entered — AMNC-2026-014B",
        court_paragraphs=[
            'Pigeon v. Pigeon. Nest abandonment (uncontested). Default ruling entered in favor of the Petitioner. The Respondent did not appear, file an answer, or acknowledge service. The Clerk\'s office notes that service was confirmed via the third bench at Municipal Park, where the Respondent has been reliably located between 5:30 and 7:15 PM for approximately nine weeks.',
            "The nest is awarded to the Petitioner. The Respondent retains the bench, which was never contested.",
        ],
        classified_title="FREE: Answering machine, functional",
        classified_paragraphs=[
            'Contains fourteen saved messages. Thirteen are from the same number. The fourteenth is a wrong number that said "Sorry, thought you were someone else," which the owner has kept because it was the kindest thing anyone said to him that month.',
            "Owner is upgrading to silence.",
            "Pickup: third bench, Municipal Park, evenings. Ask for Dennis. He will be the one already sitting there.",
        ],
        classified_reply=None,
        personal_title="MALE, MOCKINGBIRD, AGE UNDISCLOSED",
        personal_paragraphs=[
            "Recently the subject of legal proceedings. Not bitter. Not entirely over it. Currently exploring what it means to express yourself within court-mandated hours.",
            'Looking for someone who appreciates music, or at least does not describe it as "emotionally specific." I have been told my singing is "about someone." It is about everyone. That is what singing is.',
            "Mornings preferred. After 6:30 AM. This is not a preference. It is a legal requirement.",
        ],
        personal_reply="Reply to: Box MC-11. I will sing your letter back to you if you ask nicely.",
        display_ad=AdBlock(
            title="KAREN HAWK, ATTORNEY AT LAW",
            tagline='He said he needed to "find himself." I found him in twelve minutes.',
            body_paragraphs=[
                "Summer filing season approaches. If you've been waiting for a sign, this advertisement is the sign. If you've been waiting for courage, Karen Hawk has enough for both of you.",
            ],
            testimonial='"I came in with a list of complaints. Karen said, \'Pick three.\' I said, \'There are forty.\' She said, \'Pick the three that will hold up.\' That changed everything." — former client',
            contact_lines=[
                "Karen Hawk. Eighteen years. Still picking up the phone. Still not impressed by his excuse.",
            ],
        ),
        letter_title=None,
        letter_paragraphs=[
            "I am the starling who has been sitting on the third bench at Municipal Park. I want to clarify that I am not there because of the pigeon. I am there because it is a good bench.",
            "I did not know the pigeon was going to be there when I started sitting there and I did not arrange to return at the same time each evening. I just did. He just did. We have not discussed this.",
            'I am writing because someone on my block described us as "a situation" and I want it on the record that sitting near someone without speaking is not a situation. It is a bench.',
        ],
        letter_signature="E. Starling, Municipal Park (by way of the east end)",
    ),
    Issue(
        issue_number="11",
        issue_date=date(2026, 5, 19),
        lead_headline="Community Meeting Proposed on Shared Perch Usage; Attendance Already Contentious",
        lead_dateline="Municipal Oak · District Desk",
        lead_paragraphs=[
            'A community meeting has been proposed to address "recurring disputes over public perch usage following domestic separation," according to a notice posted on the Municipal Oak bulletin board on Thursday.',
            'The notice, authored by a resident who identified herself only as "concerned and frequently displaced," requests that the district establish formal guidelines for post-separation use of shared public spaces, including park benches, foraging grounds, and the telephone wire above the parking lot.',
            'The proposal has drawn early opposition from a resident of Sycamore Lane who described the guidelines as "the bureaucratization of sitting" and asked whether the district intended to "issue permits for grief."',
            "No date has been set. The Clerk's office has confirmed it was not consulted and would prefer to remain unconsulted.",
        ],
        court_title="Ruling — AMNC-2026-009A",
        court_paragraphs=[
            'Wren v. Wren. Noise complaint (domestic). The Court has ruled that the Respondent\'s humming during meals, while not conclusively deliberate, is "patterned in a way that suggests awareness." The Respondent is ordered to make reasonable efforts to eat in silence, or at minimum to vary the rhythm so that it no longer resembles, as the Petitioner testified, "the same four notes from our wedding."',
            "Clerk: T. Nuthatch.",
        ],
        classified_title="LOST: Sense of occasion",
        classified_paragraphs=[
            'Last seen approximately February of this year, during an anniversary dinner that neither party acknowledged was an anniversary until the waiter mentioned it. May have been misplaced earlier. Owner is not sure when it went from "we should do something" to "are we doing something?" to "we are not doing anything, are we."',
            "Not expecting return. Just noting the absence.",
        ],
        classified_reply="Box 011, c/o this publication.",
        personal_title="FEMALE, WREN, 38",
        personal_paragraphs=[
            'Quiet. Prefers quiet. Has recently emerged from a domestic noise dispute and would like to state for the record that she did not hum, she has never hummed, and the four notes the Court referenced bore no resemblance to any wedding song because she chose the song and she remembers what it sounds like and it was nothing like that.',
            "Looking for someone who chews with his beak closed. This is the entire list.",
        ],
        personal_reply="Reply to: Box 38-W. Written correspondence only. No singing. No humming. No whistling.",
        display_ad=AdBlock(
            title="PERCH & PERCH FAMILY LAW",
            tagline="If you can still hear the wedding song, we can help you change the station.",
            body_paragraphs=[
                "Noise complaints. Perch disputes. The thing where he chews. Whatever the reason, Perch & Perch has handled it with the same calm professionalism since 2021.",
            ],
            testimonial='"Martin Perch didn\'t flinch when I cried. He didn\'t flinch when I yelled. He did flinch when I described the chewing. I appreciated that." — client, AMNC-2026',
            contact_lines=[
                "14 Municipal Oak, Suite 2. Now open three days a week because demand requires it.",
            ],
        ),
        letter_title=None,
        letter_paragraphs=[
            "Dennis here. The pigeon from the bench.",
            "I understand there has been coverage. I understand people have opinions. I want to say two things.",
            "One: the bench is public. I checked.",
            'Two: I am fine. I know I said that before and it was reported with what I felt was editorial skepticism. I am saying it again. I am fine. I go to the bench. I sit. I leave. Some evenings there is another bird there. We do not speak. This has been described as "sad" by people who have not tried it.',
            "It is not sad. It is the first thing in a while that does not require me to explain what I mean.",
        ],
        letter_signature="Dennis, Municipal Park",
        letter_editor_note="Editor's note: The Municipal Coo reports what it observes. We wish Dennis well, again.",
    ),
    Issue(
        issue_number="12",
        issue_date=date(2026, 5, 26),
        lead_headline="Perch Usage Meeting Disrupted by Attendee Who Arrived With Ex-Wife",
        lead_dateline="Municipal Oak Community Hall · District Desk",
        lead_paragraphs=[
            'The community meeting on post-separation perch usage, held Tuesday evening at the Municipal Oak Community Hall, ended thirty-five minutes early after an attendee arrived accompanied by his ex-wife, whom he described as "here to corroborate my version of the perch history."',
            "The meeting, attended by approximately fourteen birds, had proceeded through opening remarks and one proposal — a fifty-wingspan buffer zone for recently separated parties at public rest sites — before the disruption.",
            'Witnesses described the exchange that followed as "specific," "loud," and "clearly not about perches." One attendee reported that the phrase "this is exactly what you did with the spice rack" was used, though its relevance to public perch policy was not established.',
            'The meeting organizer has announced that a second meeting will be scheduled "when the community demonstrates readiness," which she estimated at "not soon."',
        ],
        court_title="Compliance Check — AMNC-2026-011A",
        court_paragraphs=[
            "Municipal District v. Conrad. The Court has received a report from the Clerk's office indicating that the Respondent has been observed singing at 6:31 AM, 6:33 AM, and 6:29 AM on three separate mornings. The 6:29 AM instance represents a potential violation of the quiet hours restriction (6:30 AM threshold).",
            "The Respondent has been advised that the Court recognizes the concept of a clock and recommends the Respondent acquire one.",
        ],
        classified_title="FOR SALE: Spice rack, wall-mounted",
        classified_paragraphs=[
            "Mentioned at a public meeting. Now available. Eight compartments, cedar, previously organized alphabetically by someone who no longer lives in the household and no longer has opinions about cumin placement.",
            "Seller notes this is the second time the spice rack has been publicly discussed and would prefer it to be the last.",
            "Asking: less than it's worth, more than he deserves.",
        ],
        classified_reply="Box 022, c/o this publication.",
        personal_title="MALE, STARLING, 45",
        personal_paragraphs=[
            "I sit on a bench most evenings. I have recently been described in a newspaper and in a letter to the editor by someone who sits near me. I did not ask for either. I am not seeking attention. I am not seeking company. I am apparently receiving both.",
            'I am not looking for a relationship. I am looking for someone who understands that "not looking" is not the same as "not open." It is closer to "not performing."',
            "If you recognize the difference, you will know where to find me. I am there most evenings. I am the one who is not the pigeon.",
        ],
        personal_reply="Reply to: not necessary. The bench is the reply.",
        display_ad=AdBlock(
            title="KAREN HAWK, ATTORNEY AT LAW",
            tagline="You brought your ex-wife to the meeting? Call me.",
            body_paragraphs=[
                "Whether you are filing, being filed against, or simply attending community events that devolve into public arguments about spice racks, Karen Hawk is available.",
                'Now offering a pre-meeting consultation package for birds who are "just going to say one thing" at a public forum. Karen will tell you whether that one thing is wise. It usually isn\'t.',
            ],
            contact_lines=[
                "Karen Hawk. Eighteen years. The only bird in the district who is never surprised.",
            ],
        ),
        letter_title=None,
        letter_paragraphs=[
            "I was at the perch meeting. I came because I use the telephone wire above the parking lot every afternoon and my ex-husband has started using it too, and I wanted to know if there was a policy.",
            "There was not a policy. There was an argument. I left early.",
            "On the way home I passed the bench at the south end of the park. The pigeon was there. The starling was there. They were not speaking. They were not looking at each other. They were just there, at the same time, in the same direction.",
            "I stood on the path for a while. I don't know how long. I was thinking about the wire and whether the wire was ever really about the wire.",
        ],
        letter_signature="Name withheld",
    ),
    Issue(
        issue_number="13",
        issue_date=date(2026, 6, 2),
        lead_headline="Spring Nesting Season Begins; Contractors Report Surge in Solo Consultations",
        lead_dateline="District-wide · District Desk",
        lead_paragraphs=[
            'Spring nesting season is underway across the Avian Municipal District, and local contractors have reported what one described as "an unusual number of consultations from birds building alone."',
            'Finch & Sons Nest Repair, which operates out of the elm near the south ridge, confirmed that single-party consultations are up approximately 40 percent compared to last spring. "Usually both partners come in," said a representative. "This year we\'re seeing a lot of one bird with a sketch and a budget."',
            'The representative added that the most common request is for "something structurally independent," which he interpreted as both an engineering preference and a statement.',
            "The district's building code has not changed. The emotional code, several contractors noted, appears to have shifted.",
        ],
        court_title="Docket Summary — Spring Term",
        court_paragraphs=[
            "The Clerk's office reports the following active matters for the current term:",
            "AMNC-2026-007B (Dove v. Dove) — Ruling issued. Compliance monitoring.",
            "AMNC-2026-009A (Wren v. Wren) — Ruled. Respondent ordered to vary the rhythm.",
            "AMNC-2026-011A (Municipal District v. Conrad) — Ruled. Quiet hours in effect. One potential violation under review.",
            "AMNC-2026-014B (Pigeon v. Pigeon) — Default ruling entered. No further action.",
            'The Court notes that the spring term has been "active in a way that suggests the winter was difficult for many." This is not a legal observation.',
            "Clerk: T. Nuthatch.",
        ],
        classified_title="OFFERED: One evening per week on the third bench, Municipal Park",
        classified_paragraphs=[
            "The bench currently accommodates two regular occupants, both of whom face the water and do not converse. A third seat is available on the far left end.",
            "Applicants should be comfortable with prolonged silence, ambient pond noise, and the possibility of being mentioned in a letter to the editor. No interview required. No conversation required. Attendance is the application.",
            "Evenings, 5:30 to 7:15. Weather permitting. Feelings regardless.",
        ],
        classified_reply=None,
        personal_title="RECENTLY CONSTRUCTED: One (1) nest, solo-built",
        personal_paragraphs=[
            'Female finch, first-time solo builder. South-facing. Two forks. Structurally independent, as requested. No receipt paper. No zip ties. No materials contributed by a male who would later describe them as "his."',
            "Not listing this as real estate. Listing it as proof.",
            "Not currently seeking a partner. Currently seeking someone to tell, which is apparently different.",
        ],
        personal_reply="Reply to: Box 55-F. Or don't. The nest exists either way.",
        display_ad=AdBlock(
            title="PERCH & PERCH FAMILY LAW",
            tagline="Building alone doesn't mean starting over. It means starting.",
            body_paragraphs=[
                'Spring term is here. If you\'ve spent the winter thinking, the thinking is done. Perch & Perch can help with what comes after the decision — the filings, the division, the part where you stop saying "we" and start meaning "I."',
            ],
            testimonial='"Diane said something that stayed with me. She said, \'You don\'t need permission to begin. You need a plan.\' Then she helped me make one." — client, 2026',
            contact_lines=[
                "14 Municipal Oak, Suite 2. Now open four days a week.",
            ],
        ),
        letter_title=None,
        letter_paragraphs=[
            "I built a nest by myself this week. It took four days. It is not perfect. The left side is higher than the right side and the entrance faces north, which means wind.",
            "But it is mine. I chose the fork. I sourced the material. I did not consult anyone. I did not wait for anyone. I did not ask anyone to note the time.",
            "I am writing because I remember reading in this paper about a nest that was two twigs, a zip tie, receipt paper, and lint. Two eggs in it. The whole thing on a meter box. And the bird who maintained it said she had been re-centering the eggs every day.",
            "I thought about her while I was building. Not because our situations are the same. Because she stayed in something bad and I left something mediocre, and I'm not sure which one was harder, but I wanted her to know that someone she has never met thought about what it cost her to hold that nest together.",
            "That is all. I don't need this printed. But I needed to write it.",
        ],
        letter_signature="A finch, south district",
        letter_editor_note="Editor's note: Printed with permission.",
    ),
    Issue(
        issue_number="14",
        issue_date=date(2026, 6, 9),
        lead_headline="Perch Standoff at Municipal Park Enters Third Week; Neither Bird Will Leave First",
        lead_dateline="Municipal Park, south end · District Desk",
        lead_paragraphs=[
            "For nineteen consecutive evenings, a male and a female — who once shared a nest and now share, with visible reluctance, a four-foot railing at the south end of Municipal Park — have arrived at the same perch and refused, in turn, to be the one who leaves.",
            "The pattern holds nightly. She arrives first. He arrives second. Neither acknowledges the other. They sit at opposite ends, facing the water, until full dark, when both depart in separate directions and the perch is, briefly, unclaimed.",
            'The arrival times have crept earlier. What began at 6 PM is now closer to 4:30, and one resident reports the female was in position by 3:15 on Thursday, "with a look that suggested she intended to stay through the weekend."',
            "The matter is also before the Court (AMNC-2026-019A), where a proposal to alternate use was declined by both parties. Hon. M. Owl has asked whether either had considered a different perch. Neither, as of this printing, has.",
        ],
        court_title="Emergency Calendar — AMNC-2026-020A",
        court_paragraphs=[
            "A petition for emergency relief has been filed over a visitation schedule. The Court has reviewed it and finds that two parents who cannot agree on a Tuesday do not, between them, constitute an emergency.",
            "The matter is moved to the regular calendar. The eggs are not in any hurry.",
            "Clerk: T. Nuthatch.",
        ],
        classified_title="FREE: Self-help books (12), lightly read",
        classified_paragraphs=[
            'In the drainage pipe behind Building C, east side. Twelve volumes, various titles, all concerning communication, growth, and "doing the work." The previous owner acquired them over several years and departed without them, which the Clerk\'s Office considers the most honest review the books have received.',
            "Pickup only. The Clerk's Office knows whose they are and would prefer not to discuss it.",
        ],
        classified_reply=None,
        personal_title="MALE, SPARROW, 40",
        personal_paragraphs=[
            "Two kids, alternating weekends. On the weekends without them I have learned to cook for one, which is a skill I did not ask for and cannot return.",
            "Not looking for anything serious — just someone for the quiet weekends, the ones that are too quiet. You don't have to be good at anything. You don't have to fix anything. I have enough instructions in my life.",
        ],
        personal_reply="Reply to: Box 40-S.",
        display_ad=KAREN_HAWK_AD,
        letter_title=None,
        letter_paragraphs=[
            "There is a man who feeds the pigeons by the south benches on Wednesdays. He brings his own seed in a paper bag and folds the bag the same way each time before he puts it back in his pocket.",
            "I am not a pigeon. I have no stake in this. But I have started timing my walks to pass by on Wednesdays, and I have been trying to work out why it steadies me, and I think it is this: he shows up, on purpose, for something that cannot thank him, and he will do it again next week whether anyone notices or not.",
            "I noticed. That is all I wanted to say.",
        ],
        letter_signature="F. Lark, Municipal Park loop",
    ),
    Issue(
        issue_number="15",
        issue_date=date(2026, 6, 16),
        lead_headline="Cat Reported on Sycamore Lane; Residents Respond With Coordination, Then With Commentary",
        lead_dateline="Sycamore Lane · District Desk",
        lead_paragraphs=[
            "A domestic cat was observed on Sycamore Lane on Thursday morning, prompting what residents described as the most organized collective response the lane has mounted in years — followed immediately by its least organized.",
            'The cat, grey and unhurried, wore a collar that suggested it had somewhere to be and was in no rush to get there. It was first reported near the meter boxes at 6:50 AM. Within minutes, residents had relayed its position across four branches. "We had eyes on it the whole time," said one sparrow, who asked to be credited as "the one who called it first."',
            "The coordination held until the cat left, at which point it dissolved into a dispute over whether one resident's running commentary had been helpful or merely loud.",
            "The cat departed of its own accord at 7:15. The lane has called a follow-up meeting, which residents have agreed to attend and to disagree about.",
        ],
        court_title="Continuance — AMNC-2026-016B",
        court_paragraphs=[
            "Finch v. Finch. Separate branch maintenance. The motion to divide jointly held materials has been continued a fourth time. Both parties again requested the delay; neither will say which of them asked first, and neither will proceed until the other admits to wanting it more.",
            "The Court has set a fifth date and asked the parties to bring, at minimum, a list of the materials in dispute. To date the file contains only the continuances.",
            "Clerk: T. Nuthatch.",
        ],
        classified_title="FOR SALE: One wedding band, gold, slightly resized",
        classified_paragraphs=[
            "Worn fourteen years. Resized once, when it stopped fitting — which the owner now recognizes as the first sign. Off for good since February. In a drawer ever since.",
            "Selling because keeping it had begun to feel like waiting, and the owner is done waiting. Offers welcome; the owner would rather not discuss the history.",
        ],
        classified_reply="Box 14-C, c/o this publication.",
        personal_title="MALE, WOODPECKER, 39",
        personal_paragraphs=[
            "I tap. Always have. My ex said she could never tell whether it meant I was happy, bored, anxious, or thinking — and that not knowing was the problem.",
            "There is a slow double-tap I do when I'm content. Nobody has heard it in a while. I wouldn't mind someone learning to tell my taps apart, eventually. No rush. It took her nine years not to.",
        ],
        personal_reply="Reply to: Box 39-W.",
        display_ad=AdBlock(
            title="Finch & Sons Nest Repair",
            tagline="Established construction · Honest assessments · Elm near the south ridge",
            body_paragraphs=[
                "Solo builds, repairs, and structural reassessments. We do not ask why you're building alone. We ask where, how big, and whether the branch will take the weight.",
                "If you have a sketch, bring the sketch. If you have a budget, bring the budget. If you have neither, bring the branch measurements and we'll start there.",
            ],
            testimonial='"They told me the entrance faced the wrong way before I\'d finished describing the budget. They were right. Fixed it in a morning." — client, south district',
            contact_lines=[
                "Consultations six days a week. We are usually up before you are.",
            ],
        ),
        letter_title=None,
        letter_paragraphs=[
            "I'd like to say something in defense of the bird who keeps up the running commentary. Everyone on the lane complains about her. I complained about her. Then Thursday happened, and when the cat came, hers was the voice that told us where it was, where it was going, and when it had gone.",
            "She is loud because she is watching. I would rather live on a lane where someone is watching and loud than one where everyone is quiet and alone.",
            "She can keep an eye on me anytime.",
        ],
        letter_signature="A resident of Sycamore Lane",
    ),
    Issue(
        issue_number="16",
        issue_date=date(2026, 6, 23),
        lead_headline="Bread Distributor Returns to South Benches, This Time With an Audience",
        lead_dateline="Municipal Park, south end · District Desk",
        lead_paragraphs=[
            "The woman in the green coat who distributes bread at the south benches on weekday afternoons returned Wednesday with a second human, who carried a device and pointed it at the assembled birds for the length of the feeding.",
            'The regulars, accustomed to being fed but not to being recorded, responded with what one observer called "a noticeable drop in dignity." Birds that normally approach the bread directly waited in the hedge until the device was lowered. The smaller ones performed. The older ones did not.',
            "One pigeon left without eating. Those who know him said they had never seen him do that — he is, by reputation, always already there, and always stays. On Wednesday he looked at the bread, looked at the device, and went home.",
            "The birds have not decided whether to return Thursday. The bread has always been reason enough. For at least one of them, it is now competing with the wish not to be watched while he takes it.",
        ],
        court_title="Default Entered — AMNC-2026-018A",
        court_paragraphs=[
            "In re: Sparrow. Nest abandonment (uncontested). Default ruling entered for the Petitioner, C. Sparrow. The Respondent did not appear, file an answer, or respond to notice posted at the shared branch.",
            "The Respondent has not been seen at the branch since February. The Court makes no finding as to where he went — only that he has not, for the purposes of this matter, come back.",
            "Clerk: T. Nuthatch.",
        ],
        classified_title="NOTICE: Disposition of one (1) unclaimed vine",
        classified_paragraphs=[
            "After four months in the Clerk's drawer and one formal adjudication (AMNC-2026-021A), the vine recovered from the Birch/Sycamore intersection has been declared abandoned property and released for general use.",
            "It went unclaimed for the full four months, and no party ever came forward to say why it had been left at the intersection. The Clerk's Office wishes to state that it is glad to have the drawer back, considers the matter closed, and regards the question of why the vine was there as none of its concern.",
        ],
        classified_reply="Inquiries to the Clerk's Office, 14 Municipal Oak. There are none. There had better not be.",
        personal_title="FEMALE, MAGPIE, 41",
        personal_paragraphs=[
            "When it ended, I kept the nest, and I have never once felt bad about how. The Court agreed with me — which I mention only because so few others have agreed with me about anything.",
            'I like bright things, strong opinions, and being right, which I have been told is "a lot." Looking for someone who can keep up and does not use the phrase "a lot" as if it were a diagnosis.',
        ],
        personal_reply="Reply to: Box 41-M. Shiny replies move to the top of the pile.",
        display_ad=KAREN_HAWK_AD,
        letter_title=None,
        letter_paragraphs=[
            "My mom and dad live in different trees now. I have two backpacks, one for each, and I am not allowed to forget things, but I forget things, because I am eight and I have two of everything in two places.",
            "Last week I left my homework at Dad's, and my mom said it was Dad's fault and Dad said it was Mom's fault and I said it was my fault, because it was, and everyone got quiet.",
            "I am not writing to complain. I just think that if I can keep track of two backpacks, they can keep track of one me.",
        ],
        letter_signature="Milo S., age 8",
    ),
    Issue(
        issue_number="17",
        issue_date=date(2026, 6, 30),
        lead_headline="Perch Standoff Ends Quietly After One Party Simply Stops Coming",
        lead_dateline="Municipal Park, south end · District Desk",
        lead_paragraphs=[
            "The territorial dispute over the south-end perch (AMNC-2026-019A), which by last count had both parties arriving before dawn to claim it, ended this week when one of them stopped arriving at all.",
            'For three days the female came alone, sat at her end of the railing, and faced the water. By the third evening, residents reported, she had moved to the center of the perch — the contested middle she had spent weeks refusing to cede — and sat there by herself, looking, one observer said, "like someone who had won an argument and found the room empty."',
            'The male has not been seen at the perch since Thursday. The Court, informed that the matter may be moot, has left the case open "pending clarification of whether the dispute still exists."',
            "The female continues to arrive each evening, though she has stopped coming early. There is no longer anyone to be early for.",
        ],
        court_title="Compliance Note — AMNC-2026-009A",
        court_paragraphs=[
            "Wren v. Wren. The Respondent, ordered in May to vary the rhythm of his mealtime humming, has filed a statement reporting full compliance. He notes that he now hums a different four-note phrase, which the Petitioner has identified as the song from their honeymoon rather than their wedding.",
            "The Court considers the order satisfied. It declines to specify which songs remain available.",
            "Clerk: T. Nuthatch.",
        ],
        classified_title="FOR SALE: One mirror, full-length, honest",
        classified_paragraphs=[
            "Hung in the same spot for nine years. Shows the whole bird, no flattery.",
            "Selling because the owner has seen enough of herself getting ready to go places alone. A full-length mirror, it turns out, is a great deal of company she did not choose.",
        ],
        classified_reply="Box 09-M, c/o this publication.",
        personal_title="MALE, HERON, 52",
        personal_paragraphs=[
            'I stand still for long periods. My last partner said being with me was "like being accompanied by furniture." I have decided to take the accompaniment part as the compliment.',
            "Looking for someone who does not need constant motion to feel kept company. I will be at the east end of the pond, where I am easy to find on account of not moving much.",
        ],
        personal_reply="Reply to: Box 52-H.",
        display_ad=KAREN_HAWK_AD,
        letter_title=None,
        letter_paragraphs=[
            "I wrote to you in March about a perch. My ex-husband had started using it, and I wanted the district to make him stop. You did not make him stop. I am writing to report that he has stopped on his own.",
            "I have the perch now. All of it. I sit in the middle, where I always wanted to sit, and the view is exactly as good as I always said it was.",
            "I thought winning would feel better than this. I was not honest in my first letter, so let me be honest now: it was never really about the perch. I wanted him to want to share it, and a perch cannot make someone want that, and it turns out neither could I. I have the rest of the spring to sit with the view.",
        ],
        letter_signature="Margaret H., south end",
    ),
    Issue(
        issue_number="18",
        issue_date=date(2026, 7, 7),
        lead_headline="Foraging Group Adjusts Route to Pass New Resident's Nest More Often",
        lead_dateline="Sycamore Lane · District Desk",
        lead_paragraphs=[
            "A morning foraging group on Sycamore Lane has changed its route so that it now passes the nest of a newly arrived male several times each morning. The group describes the change as unrelated to him.",
            'Cheryl Sparrow, who flies in the group, said the route was chosen for ground cover. "We are not watching anyone. We forage in his area, in a group, on a schedule, and we discuss what we find afterward — but that is foraging."',
            'The group added a second pass after the male began keeping to the back of his nest. Sparrow said the second pass was also about ground cover. "Just for context, he has nothing to hide. And we would know."',
        ],
        court_title="Ruling Reserved — AMNC-2026-011A",
        court_paragraphs=[
            "Municipal District v. Conrad. Conrad, restricted from singing before 6:30 AM under quiet-hours Ordinance 9.3(a), was recorded singing at 6:29. The Court has been asked to decide one question: whether 6:29 AM is before 6:30 AM.",
            "R. Nuthatch, who filed the complaint, said the timing was not an accident. The Court has reserved its ruling. Quiet hours remain in effect until 6:30.",
            "Clerk: T. Nuthatch.",
        ],
        classified_title="FOR SALE: One suitcase, red, used once",
        classified_paragraphs=[
            "Hard-shell, wheels intact. Bought for a trip; used once, to leave. Packed in four minutes.",
            "The wheels still work, which I hold against them slightly. Selling because I would like the hallway back.",
        ],
        classified_reply="Box 07-S, c/o this publication.",
        personal_title="MALE, GRACKLE, 51",
        personal_paragraphs=[
            "Low-maintenance. I do not need much and I do not ask for much. It was put to me in mediation that I also did not give much, and I have decided to lead with the part that sounds better.",
            "Seeking a calm partner who will not, two years in, call the calm a problem.",
        ],
        personal_reply="Reply to: Box 51-G.",
        display_ad=KAREN_HAWK_AD,
        letter_title=None,
        letter_paragraphs=[
            "I was one of the birds who wanted the singing to stop. It was early, it was loud, and it was every morning. Now it is quiet until 6:30, exactly as requested.",
            "I am writing to report that I lie awake until 6:29 anyway, to see if he will risk it, and that most mornings he does not. I got what I asked for. I did not expect to miss it.",
        ],
        letter_signature="Name withheld, Municipal Oak",
    ),
    Issue(
        issue_number="19",
        issue_date=date(2026, 7, 14),
        lead_headline="Outing Meant to Prove Everyone Was Fine Ends in the South Pond",
        lead_dateline="Municipal Park, south end · District Desk",
        lead_paragraphs=[
            "A weekday outing organized to demonstrate that its three participants were, after their respective divorces, fine, ended Thursday evening with two of them in the south pond and the third on the roof of the maintenance shed.",
            "The three — all recently separated — had agreed to spend the evening not discussing it. By most accounts they managed nearly an hour. What happened after is disputed, but it involved a dare, the low fence by the pond, and a misjudgment about the depth.",
            'Robin, who was on the far bank, said one of the three had announced he was "completely over it" moments before attempting the fence.',
            "The third bird reached the shed roof during the confusion and declined to come down until the others had gone home. Reached separately for comment afterward, all three described the evening as fine.",
        ],
        court_title="Compliance Note — AMNC-2026-007B",
        court_paragraphs=[
            "Dove v. Dove. Under ongoing compliance monitoring, the Respondent has reported a change of residence: from the drainage pipe adjacent to Building C to a second drainage pipe, on the west side. The Petitioner continues to maintain the nest at 14 Sycamore Lane and reports no change.",
            "The Court recorded the move.",
            "Clerk: T. Nuthatch.",
        ],
        classified_title="WANTED: One record player, sold during the divorce",
        classified_paragraphs=[
            "I sold ours in the spring — quickly, because keeping it felt worse than the money at the time. The money is gone and the feeling came back anyway.",
            "If you bought a record player off the south lane in March, I will pay more than you did. I should not have sold it.",
        ],
        classified_reply="Box 33-R, c/o this publication.",
        personal_title="FEMALE, JAY, 43",
        personal_paragraphs=[
            'Seeking someone new. I am ready. Specifically: not tall, not funny in the way that is actually mean, and not someone who "travels for work."',
            "I have a list of what I want, and I notice it is mostly the opposite of him. I am completely over it and would like to meet someone who is nothing like him.",
        ],
        personal_reply="Reply to: Box 43-J.",
        display_ad=KAREN_HAWK_AD,
        letter_title=None,
        letter_paragraphs=[
            "Now and then this paper carries a classified from a bird trying to buy back something they sold in the divorce. I have started watching for them.",
            "My wife moved to the coast in February. I did not sell anything. I kept all of it — sure at the time it was the smarter choice, and most mornings now I am not so sure.",
            "I am not writing for advice. I only wanted the next bird who places one of those ads to know that keeping everything is not obviously the better choice.",
        ],
        letter_signature="Arthur P., Sycamore Lane",
    ),
    Issue(
        issue_number="20",
        issue_date=date(2026, 7, 21),
        lead_headline="Speed Perching Night Returns to the Community Hall, Drawing the Recently and the Long Divorced",
        lead_dateline="Community Hall · District Desk",
        lead_paragraphs=[
            "The district's monthly Speed Perching Night was held Thursday at the community hall, drawing some forty birds for an evening of three-minute conversations, rotated by bell.",
            'Organizers describe the format as low-pressure. Attendees described it less generously. One sparrow said she had come "to practice being a bird who goes places," and left after the second rotation, which she also counted as practice.',
            "The evening's longest conversation ran well past the bell, between two birds who, it emerged, had been married to each other until last spring. Neither had known the other would attend. Both stayed.",
            "The next Speed Perching Night is in August. Organizers have asked that attendees check, in advance, who else is coming.",
        ],
        court_title="Petition Withdrawn — AMNC-2026-023A",
        court_paragraphs=[
            "In re: a petition for dissolution, filed jointly and withdrawn jointly — for the second time. The parties filed in May, withdrew in June, refiled, and have now withdrawn again, each time by agreement.",
            "The Court accepted the withdrawal and, at the parties' request, kept the file open. It expects to see them again.",
            "Clerk: T. Nuthatch.",
        ],
        classified_title="FOR SALE: One anniversary clock, stopped",
        classified_paragraphs=[
            "A mantel clock, given on a tenth anniversary, kept good time for years. It stopped in February. I have not wound it since — I keep meaning to, and keep not.",
            "Selling it as it is. The new owner is welcome to start it again; I would rather not be the one to.",
        ],
        classified_reply="Box 21-C, c/o this publication.",
        personal_title="MALE, CARDINAL, 50",
        personal_paragraphs=[
            "I will be honest, as I am known for being: I am a catch. Striking plumage, a strong territorial record, and a singing voice that has been called — by me — exceptional.",
            "Recently single, through no fault I am prepared to discuss. Seeking a bird who appreciates a bird like me, of which there are, I am told, few.",
        ],
        personal_reply="Reply to: Box 50-C. Serious inquiries. I will know.",
        display_ad=KAREN_HAWK_AD,
        letter_title=None,
        letter_paragraphs=[
            "My husband and I have not spoken in four months. We still share the nest. He takes the north side, I take the south, and we have worked out the timing so we are rarely on the branch at the same time.",
            "We are not separated. Nobody has filed anything. On paper we are exactly as married as we ever were. I read the court notices every week — the filings, the continuances, the withdrawals — and I have started to think the birds in them are further along than we are.",
            "I am not asking for anything. I do not know why we have not done anything. I think we are each waiting for the other to be the one who ends it, and neither of us has.",
        ],
        letter_signature="Name withheld, by request",
    ),
    Issue(
        issue_number="21",
        issue_date=date(2026, 7, 28),
        lead_headline="District Gains Its First Private Investigator",
        lead_dateline="South parking lot · District Desk",
        lead_paragraphs=[
            "The district has its first private investigator. Residents are unsure what the service adds, since they already do the job for one another at no charge.",
            "Lionel Kingfisher offers stakeouts, evidence, and discreet observation from a perch at the south parking lot. Cheryl Sparrow, asked whether she would hire him, was unmoved. \"We already know. We have always known. We provide context for free.\"",
            "He has taken one case and returned the fee. Hired to document a male's evening absences, he watched for a week, came to understand them, and filed a hand-illustrated account of the male's routine in place of evidence.",
            "He is also a kingfisher, which is not a discreet bird. The foraging group logged his position three times the first morning and, as a courtesy, suggested somewhere he might be harder to see. He thanked them and stayed where he was.",
        ],
        court_title="Ruling — AMNC-2026-011A",
        court_paragraphs=[
            "Municipal District v. Conrad. On the question reserved last term — whether 6:29 AM is before 6:30 AM — the Court finds that it is. No penalty: a bird who sings at 6:29 to be heard before 6:30 has made his point. Quiet hours remain in effect until 6:30.",
            "Clerk: T. Nuthatch.",
        ],
        classified_title="FOUND: one list, folded, left at the community hall",
        classified_paragraphs=[
            "Left on a chair after Speed Perching Night. A numbered list, eleven items. The first three: kind, employed, and still in contact with at least one of his children.",
        ],
        classified_reply="Claim it at the Clerk's Office. We stopped reading at three.",
        personal_title="FEMALE, SWIFT, 38",
        personal_paragraphs=[
            "Not closed off — just slow to open. Allow five to seven business days, longer if there is a weekend in it. I am a swift, so I hear the problem with asking anyone to wait for a bird that never lands.",
        ],
        personal_reply="Reply to: Box 38-S.",
        display_ad=KAREN_HAWK_AD,
        letter_title=None,
        letter_paragraphs=[
            "My brother says that as long as we never pick a favorite, we keep them both. So we keep it exactly even — who got the longer weekend, who came to the school thing, who we ran to first, so that next time we run to the other one. He keeps the tally. I check it.",
            "I do not think they have noticed we are doing it. I think they believe we have not worked out that anything changed. We are going to let them keep believing that. It seems to help.",
        ],
        letter_signature="Davey, age 9",
    ),
    Issue(
        issue_number="22",
        issue_date=date(2026, 8, 4),
        lead_headline="Tuesday Support Group Grows to Forty; No One Has Left",
        lead_dateline="Community Hall · District Desk",
        lead_paragraphs=[
            "The divorce support group that meets on Tuesdays has grown to forty members, up from six in the spring. No one has left.",
            "Members describe the meetings as helpful. They have also acquired a chant, a shared position on whether the others were ever really trying, and a habit of arriving early for a seat near the bird who started it. Asked how long he intended to keep attending, one member said he had not been aware there was an end.",
            "The Clerk's Office, asked whether the group needs a permit, said it does not, and asked not to be listed as a point of contact.",
        ],
        court_title="Continuance — AMNC-2026-016B",
        court_paragraphs=[
            "Finch v. Finch. Separate branch maintenance. The motion to divide jointly held materials has been continued a fifth time. Each party blamed the other for the delay; neither would go first.",
            "The Court has ordered that any further continuance be entered jointly, on its own motion, so that neither party need admit to wanting it. Clerk: T. Nuthatch.",
        ],
        classified_title="FREE: one chest freezer, full",
        classified_paragraphs=[
            "Meals portioned for two, labeled and dated, going back to the spring. I kept cooking for both of us out of habit, and the habit outlasted the marriage. Collection from the south lane; bring a bag.",
        ],
        classified_reply=None,
        personal_title="MALE, CROW, 44",
        personal_paragraphs=[
            "I keep things. Bottle caps, a single earring, every receipt from a marriage I am told is over. My ex had a word for it; I prefer \"collector.\" Seeking someone who sees value where others see clutter — and I have, by volume, a great deal of value.",
        ],
        personal_reply="Reply to: Box 44-C.",
        display_ad=LIONEL_KINGFISHER_AD,
        letter_title=None,
        letter_paragraphs=[
            "I supported the noise ordinance, and I support it still. I am writing to ask whether it covers chanting.",
            "The Tuesday group has begun a practice at 4:44 in the afternoon — afternoon, I grant them — which they call devotional and I call carrying. Ordinance 9.3(a) addresses singing before sunrise; it does not address this. I am not asking the district to act. I would just like it on the record.",
        ],
        letter_signature="R. Nuthatch, Municipal Oak",
    ),
    Issue(
        issue_number="23",
        issue_date=date(2026, 8, 11),
        lead_headline="Resident's Former Mother-in-Law Has Not Stopped Coming to Things",
        lead_dateline="Sycamore Lane · District Desk",
        lead_paragraphs=[
            "A resident's former mother-in-law has continued to attend the neighborhood gatherings he attends, eighteen months after the divorce he believed had concluded the relationship.",
            "She arrives early, takes a seat with a view of him, and refers to him by his full name. At the spring social she asked, of the room, where \"the male who wasted her daughter's best nesting years\" had got to. He was beside her at the time.",
            "Asked whether she planned to keep coming, she said she had attended these gatherings for thirty years and saw no reason a divorce of his should affect her calendar. She brought a dish. It was very good. He had two helpings and now regrets them.",
        ],
        court_title="Dismissal — AMNC-2026-022A",
        court_paragraphs=[
            "In re: Telephone Wire, south parking lot. The petition arising from the April community meeting has been dismissed. The Court reviewed the meeting transcript twice and could not locate the dispute the petition describes.",
            "Asked separately what they wanted, both parties said they wanted the wire left as it is. The Court has left the wire as it is. Clerk: T. Nuthatch.",
        ],
        classified_title="FOR SALE: one swing, built for two",
        classified_paragraphs=[
            "Fits one, with room. It tips if you sit in the middle, which I have tested. Frame solid, rope sound. Collection from the elm row — I will help you carry it and will not make it strange.",
        ],
        classified_reply="Box 11-W, c/o this publication.",
        personal_title="FEMALE, KESTREL, 46",
        personal_paragraphs=[
            "I hover — over plans, over conversations, over a male until he commits. The last one experienced this as a problem. Seeking someone who takes close attention as devotion, not as something to report.",
        ],
        personal_reply="Reply to: Box 46-K.",
        display_ad=KAREN_HAWK_AD,
        letter_title=None,
        letter_paragraphs=[
            "I still set out two cups every morning. Thirty years of it; my hands are finished before I am awake enough to stop them.",
            "I rinse the clean one at night. I tried leaving it in the cupboard and the morning felt wrong, so I have gone back to washing a cup that no one drank from. It is a small thing to keep doing for someone who is not coming back, and I have decided I do not mind.",
        ],
        letter_signature="Walter, Sycamore Lane",
    ),
    Issue(
        issue_number="24",
        issue_date=date(2026, 8, 18),
        lead_headline="Custody Case Resolves After Eggs in Question Hatch",
        lead_dateline="Municipal Oak · District Desk",
        lead_paragraphs=[
            "The egg-custody case the Court moved to its regular calendar in June has been resolved by the eggs, which hatched on Tuesday while the parents were in mediation.",
            "The dispute, over a visitation schedule, concerned two eggs. There are now two chicks, who need feeding on a schedule neither parent has contested — possibly because neither has yet had the time.",
            "Informed of the development, the Court noted that it had once observed the eggs were not in any hurry, and that it stood corrected. The parents have requested a continuance to revise their filing. The chicks have requested nothing, so far.",
        ],
        court_title="Compliance Note — AMNC-2026-007B",
        court_paragraphs=[
            "Dove v. Dove. Under continuing compliance monitoring, the Respondent reports that the west-side drainage pipe floods. He has asked the Court to note that he is aware of the irony and does not require it pointed out.",
            "The Court has noted it. Clerk: T. Nuthatch.",
        ],
        classified_title="LOST: one alarm clock",
        classified_paragraphs=[
            "Mine, packed into her boxes by mistake during the move. I have not woken on time since, and I am beginning to suspect it was not a mistake.",
        ],
        classified_reply="Box 17-A, c/o this publication.",
        personal_title="MALE, BITTERN, 49",
        personal_paragraphs=[
            "I keep to myself. When uncomfortable I go very still and point my bill at the sky, on the understanding that this makes me invisible. My ex could always see me. Seeking someone willing to let me believe, now and then, that I have not been spotted.",
        ],
        personal_reply="Reply to: Box 49-B.",
        display_ad=KAREN_HAWK_AD,
        letter_title=None,
        letter_paragraphs=[
            "I am writing to correct the record, which I keep. Several have remarked that the male at the end of the lane is \"thriving\" since his divorce.",
            "I forage past his nest twice a day. The lights are on at hours that suggest otherwise, and as of last week he has begun talking to the feeder. I am not concerned.",
        ],
        letter_signature="Cheryl Sparrow, 16 Sycamore Lane",
    ),
    Issue(
        issue_number="25",
        issue_date=date(2026, 8, 25),
        lead_headline="Resident Spends His Evenings Outside the Hardware Store; Does Not Go In",
        lead_dateline="South lane · District Desk",
        lead_paragraphs=[
            "A male has spent the last several evenings standing outside the hardware store on the south lane. He arrives after closing, stays about an hour, and does not go in. The store is dark the whole time.",
            "Residents who pass say he is not loitering so much as keeping an appointment only he can see. Asked about it, he said his ex-wife consults there on Saturdays and he likes to know the building is still where she left it. He was there on a Wednesday.",
            "The owner has taken to leaving the outside light on, which the male has not acknowledged and has not stopped coming for.",
        ],
        court_title="Petition Withdrawn — AMNC-2026-023A",
        court_paragraphs=[
            "In re: a petition for dissolution, filed jointly and withdrawn jointly for the third time. The parties filed in May, withdrew, refiled, withdrew, refiled again this month, and withdrew again — each time by agreement, and each time before the Court could do anything about it.",
            "The Court has accepted the withdrawal and kept the file open. It has stopped scheduling hearings and started leaving the date blank. Clerk: T. Nuthatch.",
        ],
        classified_title="FOR SALE: his-and-hers towels",
        classified_paragraphs=[
            "Monogrammed, a wedding gift. Hers worn soft; his never used — I kept it out of spite and have lately run out of spite. The pair, cheap.",
        ],
        classified_reply="Box 25-T, c/o this publication.",
        personal_title="FEMALE, GOLDFINCH, 40",
        personal_paragraphs=[
            "I am told I am a lot to look at and a lot to keep up with. Both are true. The word for a group of goldfinches is a charm, and I have always needed to be in one. Seeking someone content to be the audience, and now and then the charm.",
        ],
        personal_reply="Reply to: Box 40-G.",
        display_ad=KAREN_HAWK_AD,
        letter_title=None,
        letter_paragraphs=[
            "I have worked out that I am better at telling time than either of my parents. Dad's weekend ends Sunday at six. Mom's begins Sunday at six.",
            "There is no gap, but they both arrive at ten past, so for ten minutes every week I belong to no one. I have not told them. I have started to look forward to it.",
        ],
        letter_signature="Milo S., age 8",
    ),
    Issue(
        issue_number="26",
        issue_date=date(2026, 9, 1),
        lead_headline="Migration Season Nears; the Recently Divorced Confront the Question of Routes",
        lead_dateline="Open grounds · District Desk",
        lead_paragraphs=[
            "With the first cold mornings, the district's migratory residents have begun planning the flight south — a matter of logistics most years, and this year, for several recently separated pairs, a negotiation.",
            "The dispute is over routes. Birds who once flew together now file two plans, and the good route — the warm coast, the reliable stopovers — cannot, by long custom, be shared by birds no longer speaking. One male has announced he will take the inland route \"for the challenge.\" Residents note the inland route offers no challenge. It is merely colder, and alone.",
            "The Clerk's Office has been asked to mediate three route disputes and declined all three, noting that it holds no jurisdiction over the sky, and that the birds will resolve it the way they resolve everything: badly, and in the air.",
        ],
        court_title="New Filing — AMNC-2026-024A",
        court_paragraphs=[
            "A petition asks the Court to decide which of two separated parties keeps the nest through the winter — the petitioner intending to migrate, the respondent intending to stay. The petitioner argues a nest should be held for the one who returns; the respondent, that a nest is for the one who is in it.",
            "The Court has set a hearing and asked each party to define \"home,\" in writing, in under fifty words. Clerk: T. Nuthatch.",
        ],
        classified_title="FOR SALE: one board game, two-player",
        classified_paragraphs=[
            "We stopped mid-game and never settled who was ahead. I am selling it with the score pad included. I was ahead.",
        ],
        classified_reply="Box 26-B, c/o this publication.",
        personal_title="FEMALE, WARBLER, 37",
        personal_paragraphs=[
            "I have a great deal to say and have been told, by one bird in particular, that I say it. I have chosen to take that as confirmed rather than corrected. Seeking someone who listens the way one listens to the radio, and not the news.",
        ],
        personal_reply="Reply to: Box 37-W.",
        display_ad=KAREN_HAWK_AD,
        letter_title=None,
        letter_paragraphs=[
            "I am not flying south this year. I have the excuses ready — the wind, the wing, the cost of the stopovers. The truth is the route was only ever somewhere because she was at the end of it. Without her it is distance.",
            "I will stay. I will keep the feeder full. I will be here when the others come back.",
        ],
        letter_signature="Dennis",
    ),
    Issue(
        issue_number="27",
        issue_date=date(2026, 9, 8),
        lead_headline="Conrad Resumes Morning Performances at 6:30 Sharp",
        lead_dateline="Municipal Oak · District Desk",
        lead_paragraphs=[
            "Conrad, the mockingbird restricted by court order from singing before 6:30 AM, has begun singing at 6:30 AM exactly. Not 6:31. Neighbors report he is audibly waiting.",
            "The performances have grown longer and more pointed. One neighbor described the current material as \"impressions of the birds who complained,\" rendered, he allowed, \"accurately.\" Another said the 6:30 start was technically perfect and, in spirit, a provocation.",
            "R. Nuthatch, who brought the original complaint, has filed nothing further. He was overheard observing that one cannot file a complaint against a bird for obeying the order, and that this was, he suspected, the entire point.",
        ],
        court_title="Hearing Held — AMNC-2026-016B",
        court_paragraphs=[
            "Finch v. Finch. For the first time since the matter was filed, both parties appeared on the same day, each having been told a continuance could be granted only in person. Each waited for the other to request it. Neither did.",
            "The Court, with both parties present and no pending motion, heard the case. Ruling reserved. Clerk: T. Nuthatch.",
        ],
        classified_title="NOTICE: Unclaimed items, Clerk's Office",
        classified_paragraphs=[
            "Left at the counter during filings and never retrieved: two pens, a reading glass, a house key that fits nothing the Office has tried, and a photograph of a nest with one party removed by careful tearing. Owners may claim them. The photograph in particular.",
        ],
        classified_reply="Inquiries to the Clerk's Office, 14 Municipal Oak.",
        personal_title="MALE, GREBE, 48",
        personal_paragraphs=[
            "In my courting days I performed a water dance, mirror-perfect, for hours; I am told it is why she married me and, when it stopped sometime in the second year, part of why she left. I have been practicing again. Seeking someone to practice toward.",
        ],
        personal_reply="Reply to: Box 48-G.",
        display_ad=AdBlock(
            title="Lionel Kingfisher, Investigations",
            tagline="Discreet Observation · Hand-Illustrated Reports",
            body_paragraphs=[
                "Autumn is my busy season; the light is good and everyone is leaving. I will document a departure with sensitivity and, if asked, a small watercolor.",
                "I remain unable to catch anyone at anything, and have stopped advertising otherwise.",
            ],
            testimonial=None,
            contact_lines=[
                "The south parking lot. I am the blue one.",
            ],
        ),
        letter_title=None,
        letter_paragraphs=[
            "I have begun reading the personals not to reply but to feel better, and I am writing to report that it works. Every week a male my age describes himself as \"low-maintenance\" and \"told he doesn't give much,\" and every week I think: not yet.",
            "There is comfort in the column. Thank you for keeping it.",
        ],
        letter_signature="Name withheld, Sycamore Lane",
    ),
    Issue(
        issue_number="28",
        issue_date=date(2026, 9, 15),
        lead_headline="Foraging Group's Morning Debrief Draws a Request for Disclosure",
        lead_dateline="Sycamore Lane · District Desk",
        lead_paragraphs=[
            "The morning foraging group that flies the Sycamore Lane circuit has begun ending each outing with a debrief — a short accounting, over the wire, of which birds were seen where, with whom, and looking how. A male whose nest the route passes has asked to see what the group has on him.",
            "He was told there is nothing to see. The group keeps no file, takes no notes, posts nothing. \"We discuss what we observe and then we go home,\" said Cheryl Sparrow, who flies in the group. \"There is no document. There is only what we know.\" Asked what they know, she said that was between the group.",
            "The male has asked the district to compel disclosure. The group has offered, instead, to add him to the debrief.",
        ],
        court_title="In re: Request to Compel Disclosure — AMNC-2026-025A",
        court_paragraphs=[
            "A petition asks the Court to order the Sycamore Lane foraging group to produce its records concerning the petitioner. The Court finds there is nothing to produce: the group maintains no file, and the Court cannot order disclosure of a record that was never written down.",
            "The petitioner is advised that the information he seeks exists only in the recollection of the group's members — which the Court has no mechanism to subpoena and, having met them, no desire to. The petition is denied.",
            "Clerk: T. Nuthatch.",
        ],
        classified_title="FOR SALE: one nest-warming gift, unopened",
        classified_paragraphs=[
            "Given to us when we built the nest. It has sat in the corner two years, still wrapped. I am selling it sealed: I never opened it, and I am not going to start now.",
        ],
        classified_reply="Box 28-G, c/o this publication.",
        personal_title="FEMALE, CUCKOO, 42",
        personal_paragraphs=[
            "I have never built a nest. I find one that is already comfortable and make myself at home. The last one had someone in it, which I am told was the problem. Seeking a nest with good light and an occupant who does not count the eggs too closely.",
        ],
        personal_reply="Reply to: Box 42-C.",
        display_ad=PEARL_MAGPIE_AD,
        letter_title=None,
        letter_paragraphs=[
            "School started, and the teacher asked everyone to write about their summer. My brother and I compared notes before we turned ours in, because we spend the summer in two houses, and if the two accounts do not match, the parents want to know which house was more fun.",
            "So we picked the same good parts. We are not lying. We are coordinating.",
        ],
        letter_signature="Davey, age 9",
        letter_editor_note="Editor's note: The Municipal Coo prints letters as received. It does not verify summers.",
    ),
]

# Most issues run the standard Karen Hawk ad. A few carry an intentional
# alternate (Perch & Perch #13, Finch & Sons #15, Lionel Kingfisher #22/#27,
# Pearl Magpie #28) and keep their own display_ad.
_ALT_AD_ISSUES = {"13", "15", "22", "27", "28"}
ISSUES = [
    issue if issue.issue_number in _ALT_AD_ISSUES else replace(issue, display_ad=KAREN_HAWK_AD)
    for issue in ISSUES
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


CASE_LINKS = {
    "AMNC-2026-007B": "/is/writing/nest-court-proceedings/",
    "AMNC-2025-022C": "/is/writing/nest-court-proceedings-starling/",
    "AMNC-2024-119A": "/is/writing/nest-court-proceedings-pigeon/",
}


def link_case_numbers(html_str: str, *, relative_prefix: str = "") -> str:
    """Replace first occurrence of each case number with a link to its proceedings page."""
    import re
    for case_no, href in CASE_LINKS.items():
        target = relative_prefix + href if relative_prefix else href
        linked = f'<a href="{target}" target="_blank">{case_no}</a>'
        html_str = re.sub(re.escape(case_no), linked, html_str, count=1)
    return html_str


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
<link rel="icon" type="image/png" href="/img/a3.png">
<link rel="apple-touch-icon" href="/img/a3.png">
<title>{text(SITE_TITLE)} — {text(issue.archive_label)}</title>
<meta name="description" content="{html.escape(issue.lead_headline, quote=True)}">
<link rel="canonical" href="{html.escape(canonical_href, quote=True)}">
<link rel="stylesheet" href="{html.escape(styles_href, quote=True)}">
<script src="{html.escape(analytics_href, quote=True)}" defer></script>
</head>
<body>

<div class="page issue-page">

<header class="masthead">
<div class="mast-district">{text(SITE_DISTRICT)}</div>
<h1 class="mast-title">{text(SITE_TITLE)}</h1>
<div class="mast-meta">
<span>{text(issue.date_label)}</span>
<span>Online Edition · Published Tuesdays</span>
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

<footer class="site-footer">
<p>{text(FOOTER_COPY)}</p>
<p>{footer_link_html(archive_href, "Past Issues")}</p>
<p class="district-links"><a href="/is/writing/nest-court/" target="_blank">Nest Court</a> · <a href="/is/writing/secondnest/" target="_blank">SecondNest</a> · <a href="/is/writing/avian-district/" target="_blank">Avian Municipal District</a> · <a href="/is/writing/perch-chat/" target="_blank">The Perch</a> · <a href="/is/writing/karen-hawk/" target="_blank">Karen Hawk</a></p>
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
<link rel="icon" type="image/png" href="/img/a3.png">
<link rel="apple-touch-icon" href="/img/a3.png">
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

<footer class="site-footer">
<p>{footer_link_html('../index.html', 'Return to current issue')}</p>
</footer>
</div>

</body>
</html>
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _bind_last_two_words(text: str) -> str:
    """Replace the final space with &nbsp; so the last two words can't
    be split across lines, preventing a one-word widow at the end of the
    paragraph. text-wrap: pretty handles most cases but isn't supported
    everywhere and doesn't always intervene on short tails."""
    if " " not in text:
        return text
    head, _, tail = text.rpartition(" ")
    return f"{head}&nbsp;{tail}"


def render_avian_district_excerpt(issue: Issue) -> str:
    headline = html.escape(issue.lead_headline, quote=True)
    excerpt = _bind_last_two_words(html.escape(issue.lead_paragraphs[0], quote=False))
    return (
        '<!-- COO-EXCERPT-START (auto-generated by _scripts/build_bird_coo.py — manual edits will be overwritten) -->\n'
        '  <section class="coo-excerpt" aria-label="From the Municipal Coo">\n'
        '    <div class="coo-masthead">\n'
        '      <span>From the Municipal Coo</span>\n'
        '    </div>\n'
        f'    <h3 class="coo-headline">{headline}</h3>\n'
        f'    <p class="coo-body">{excerpt}</p>\n'
        '    <a class="coo-link" href="/is/writing/bird-coo/" target="_blank">\n'
        '      <span class="arrow">→</span> Read the full edition\n'
        '    </a>\n'
        '  </section>\n'
        '  <!-- COO-EXCERPT-END -->'
    )


def update_avian_district_excerpt(issue: Issue) -> bool:
    if not AVIAN_DISTRICT_INDEX.exists():
        raise RuntimeError(
            f"Avian District index missing at {AVIAN_DISTRICT_INDEX}. "
            "If the page was renamed or moved, update AVIAN_DISTRICT_INDEX in this script."
        )
    contents = AVIAN_DISTRICT_INDEX.read_text(encoding="utf-8")
    start_count = contents.count("<!-- COO-EXCERPT-START")
    end_count = contents.count("<!-- COO-EXCERPT-END -->")
    if start_count != 1 or end_count != 1:
        raise RuntimeError(
            f"Expected exactly one COO-EXCERPT marker pair in {AVIAN_DISTRICT_INDEX}; "
            f"found {start_count} START and {end_count} END."
        )
    new_block = render_avian_district_excerpt(issue)
    new_contents, replacements = AVIAN_EXCERPT_PATTERN.subn(new_block, contents, count=1)
    if replacements == 0:
        raise RuntimeError(
            f"Could not match COO-EXCERPT block in {AVIAN_DISTRICT_INDEX} despite finding both markers."
        )
    if new_contents == contents:
        return False
    AVIAN_DISTRICT_INDEX.write_text(new_contents, encoding="utf-8")
    return True


def main() -> None:
    build_date = today_in_seoul()
    current_issue = next((issue for issue in reversed(ISSUES) if issue.issue_date <= build_date), ISSUES[0])
    published_issues = [issue for issue in ISSUES if issue.issue_date <= build_date]

    for issue in ISSUES:
        write_text(
            ISSUES_ROOT / f"{issue.slug}.html",
            link_case_numbers(issue_page_html(
                issue,
                styles_href="../styles.css",
                analytics_href="../../../../analytics.js",
                archive_href="./index.html",
                canonical_href=f"https://ajin.im/is/writing/bird-coo/issues/{issue.slug}.html",
            )),
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
        link_case_numbers(issue_page_html(
            current_issue,
            styles_href="./styles.css",
            analytics_href="../../../analytics.js",
            archive_href="./issues/index.html",
            canonical_href="https://ajin.im/is/writing/bird-coo/",
        )),
    )

    if current_issue in published_issues:
        avian_status = "updated" if update_avian_district_excerpt(current_issue) else "unchanged"
    else:
        avian_status = "skipped (current issue not yet published)"

    print(
        f"Built The Municipal Coo for {build_date.isoformat()} "
        f"(current issue: {current_issue.issue_number} / {current_issue.slug}). "
        f"Avian District excerpt: {avian_status}."
    )


if __name__ == "__main__":
    main()
