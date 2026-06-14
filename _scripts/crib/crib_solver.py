#!/usr/bin/env python3
"""Chainability check for the 해독/CRIB first-draft corpus.
A level is 'clean' (logic-forced, no blind guessing) if every new piece can be
reached via a word where it is the ONLY unknown, given the carried+crib key.
"""
CHO=list('ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ')
JUNG=list('ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ')
JONG=['']+list('ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ')

def atoms(w):
    out=[]
    for ch in w:
        c=ord(ch)-0xAC00
        out.append(CHO[c//588]); out.append(JUNG[(c%588)//28])
        jo=JONG[c%28]
        if jo: out.append(jo)
    return out

TRUTH={'ㄴ':'n','ㅏ':'a','ㅁ':'m','ㅜ':'u','ㅅ':'s','ㅗ':'o','ㅣ':'i','ㄱ':'g','ㅂ':'b','ㄷ':'d',
       'ㄹ':'r','ㅎ':'h','ㅔ':'e','ㅈ':'j','ㅓ':'eo','ㅡ':'eu','ㅇ':'ng','ㅊ':'ch','ㅐ':'ae',
       'ㅋ':'k','ㅌ':'t','ㅍ':'p'}

LEVELS=[
 ('band1 · loop',        '나무', False, ['나무','나','소','산','미','미소']),
 ('band2 · no anchor',    None,  False, ['고기','비누','도시','두부','가구']),
 ('band3 · wide bank',    None,  True,  ['사람','소리','하나','하루','게','네']),
 ('band3 · wide bank',    None,  True,  ['바지','자리','거리','머리','그림','드라마']),
 ('band4 · finals',       None,  True,  ['강','공','방','책','차','개','문','밥']),
 ('band4 · finals',       None,  True,  ['코','키','토','타','발','곰','짐','산']),
 ('band5 · thin overlap', None,  True,  ['포도','파','풀','바다','거리','그림']),
]

def piece_set(words):
    s=[]
    for w in words:
        for a in atoms(w):
            if a not in s: s.append(a)
    return s

carried=set()
all_ok=True
for i,(band,crib,wide,words) in enumerate(LEVELS):
    known=set(carried)
    if crib:
        for a in atoms(crib): known.add(a)
    level_pieces=piece_set(words)
    new=[p for p in level_pieces if p not in known]
    # chain: repeatedly crack any piece that is the lone unknown in some word
    progress=True
    cracked=set()
    while progress:
        progress=False
        for w in words:
            unk=list({a for a in atoms(w) if a not in known})
            if len(unk)==1:
                known.add(unk[0]); cracked.add(unk[0]); progress=True
    stuck=[p for p in new if p not in cracked]
    status='CLEAN' if not stuck else 'NEEDS-GUESS: '+''.join(stuck)
    if stuck: all_ok=False
    # verify all TRUTH keys exist
    missing=[a for a in level_pieces if a not in TRUTH]
    miss=' MISSING-TRUTH:'+''.join(missing) if missing else ''
    print(f"L{i+1} {band:24} new={''.join(new):8} -> {status}{miss}")
    for a in level_pieces: carried.add(a)

print('alphabet size:', len(carried), '->', ''.join(sorted(carried, key=lambda x:(CHO+JUNG).index(x) if x in CHO+JUNG else 99)))
print('ALL LEVELS CLEAN' if all_ok else 'SOME LEVELS NEED GUESSING (refine)')
