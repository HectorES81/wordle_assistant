#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wordle Assistant
  1. Opening tandem suggestions  (3-word groups for maximum letter coverage)
  2. Permutation explorer        (all valid 5-slot arrangements of known letters)
"""

import copy
import os
import random
import sys
from itertools import combinations, permutations as _iperm
from typing import Dict, List, Set, Tuple

# ---------------------------------------------------------------------------
# Word list - used only for tandem scoring
# ---------------------------------------------------------------------------
_RAW = """
aback abase abate abbey abbot abhor abide abler abode abort about above
abuse abyss adage adapt adept admit adobe adult after again agate agile
aging aglow agony agora agree ahead aisle alarm album alert algae alibi
alien align alike alive allay alley allot allow alloy aloft alone along
aloof aloud alpha alter amaze amber amble amend amiss amity among ample
angel anger angle angry anime ankle annex antic anvil aorta aphid apple
apply aptly arbor ardor argue arise armor aroma arose array ashen asset
atlas atone attic audio audit augur avail avert avian avoid awake award
aware awful awoke azure babel banal banjo basic basin basis batch bathe
bayou beach beard beast beige belle bench berry bilge binge birth black
blade blame bland blank blast blaze bleak bleed blend bless blimp blind
bliss bloat block blood bloom blown blunt blurb blurt board boast bonus
brace braid brain brake brand brave brawl brawn bread break breed brick
bride brief brine bring brisk broad broke brood brook broth brunt brush
brute budge build built bulge burnt burst buyer byway cabin cable camel
canal candy canny canoe caper cargo carve catch cause cedar cease chain
chair chalk champ chant chaos charm chart chase cheap cheat check cheek
cheer chess chest chill choir choke chord chose chunk civil claim clamp
clank clasp cleft clerk click cliff clink cloak clock clone close clout
clove clown clump clung coach coast cobra comet comic comma coral count
coupe court cover craft crane crash crave crawl creak cream creep crest
crimp crisp croak crone crook cross crowd crown crumb crush crust crypt
cubic cupid curve cycle dairy dance datum daunt dealt debut decoy defer
delta depot depth derby devil digit dirty disco ditch ditty diver dizzy
dodge douse dowel draft drain drape drawl drawn dread dream dress dried
drink drive drone drove drown drunk dryer duchy dully dumpy duvet dwarf
dwell dying eager eagle early earth ebony eerie eight elite elbow elder
ember empty endow enemy enjoy enter epoch equip erode essay etude evade
event every evoke exact exalt excel exert exile exist expel extra fable
facet fairy faith fatal fault feast feral ferry fetal fetch fiber fiend
fifty fight filch final finch first flair flame flask fleck fleet flesh
flock flood floor floss flour flown fluff fluke flume flung flunk flute
focal focus foray forge forth found frame frank fraud freak fresh frill
frisk froth froze fruit fully fungi funky funny gable gauze gecko genie
genre ghost giant girth given gizmo gland glare glass gleam glide glint
gloom gloss glove glyph gnome gouge gourd grace grade graft grain grand
grant grape grasp grate grave graze great greed green greet grief grill
gripe groan groin grope group grout grove growl grown gruel gruff grunt
guild guile guise gulch gusto gypsy habit halve handy hardy haste hatch
haute haven hazel heady heart heave hedge hefty heist helix heron hippo
hoist homer honey honor horde hotel hound human humid humor hurry hyena
hyper icing ideal idiom idiot image imply incur indie inept infer inlay
inner inset inter intro ionic irate ivory jaunt jazzy jelly jewel jiffy
joint joker joust judge juice jumbo kayak kebab kitty knife knack knave
kneel knelt knock knoll koala kudos label lance larva latch latte laugh
layer leach leafy learn lease least leave ledge legal lemon level light
lilac lithe llama lodge logic loopy louse lucid lumpy lunar lunch lusty
lymph lyric magic major maker mango manor maple march match maxim mayor
mealy medal merry messy micro might miner mirth miser model mocha moody
moral motel motif mould moult mound mourn mouse mousy murky mushy myrrh
nadir nasal naval nerve night noble noise notch novel nymph occur offer
often onset optic orbit order other otter ought ounce outdo outer ovary
ovoid owner oxide ozone paint panda panel panic paper party pasta paste
patch pause peach pearl pedal petty phase phone photo piano piece pilot
pinch pitch pixel pixie pizza place plaid plain plane plank plant plaza
plead pleat pluck plumb plume plunk poise poker polar porch pouch power
prank press price pride prime print prior prism probe prone prose prove
prowl prune psalm pudgy pulse punch pupil purge pygmy queen query queue
quick quiet quirk quota quote radar radio rally rapid raise raven reach
realm relay reign remit renal repay revel rigid risky rivet roast rogue
rouge rough round royal rugby ruler rupee saint sauce scalp scant scare
scarf scone scoop score scorn scrub seize sense serum serve setup seven
sever shaft shake shall shame shape share sharp shave sheen sheep sheer
shelf shell shift shine shirt shock shoot shore shout shove shown shred
shrew shrub shrug siege sieve sight sigma silky silly since sinew sixth
sixty skill skimp skull skunk slash slate slave slick slide slime slope
sloth slurp slush smart smear smell smelt smile smock smoke snack snake
snare sneak sniff snore snort snout sober solar solid solve sorry sound
south space spade spare spark speak spear speck spell spend spill spine
spoil spoke spoof spook spool spoon spore sport spout spray spree sprig
spunk squad squat squid stack staff stage stain stair stake stale stall
stamp stand stare stark start stash state steal steam steel steep steer
stern stick stiff still sting stock stomp stone stood stool stoop store
storm story stout stove strap straw stray strip strut study stump stung
stunk stunt style suave sugar suite sunny super surge swamp swear sweep
sweet swift swine swipe swirl sword sworn swung syrup taboo taint talon
tango tapir taunt tawny teach tease tempo tense tepid theft theme thick
thief thigh thing think thorn those three threw thumb tidal tiger tight
timer tipsy titan title toast today token tooth topaz torso total totem
touch tough towel tower toxic trace track trail train trait tramp trash
trawl trend trial tribe trick tripe trite trout trove truce truck truly
trump trunk trust truth tulip tuner tunic turbo tutor tweed twill twist
tying ulcer ultra umbra uncle under unity until upper upset usher utter
vague valid valor value valve vapor vault vaunt vegan vicar video vigor
venom venue verse viola viper visor vista vital vivid vocal vodka vomit
voter vouch vowel waltz watch water weary wedge weigh weird witch wonky
world worry worse worst worth would wound wrath wring wrist wrong yacht
yearn yeast yield young youth zappy zesty zilch zippy
"""

# Embedded fallback — used when CSV files are absent
_EMBEDDED: List[str] = []
_seen_w: Set[str] = set()
for _tok in _RAW.split():
    _tok = _tok.lower()
    if len(_tok) == 5 and _tok.isalpha() and _tok not in _seen_w:
        _EMBEDDED.append(_tok)
        _seen_w.add(_tok)


def _read_csv(path: str) -> List[str]:
    words: List[str] = []
    seen: Set[str] = set()
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                w = line.strip().lower()
                if len(w) == 5 and w.isalpha() and w not in seen:
                    words.append(w)
                    seen.add(w)
    except OSError:
        pass
    return words


_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "words-list")
ANSWER_WORDS: List[str] = _read_csv(os.path.join(_BASE, "word-bank.csv")) or _EMBEDDED
VALID_WORDS:  List[str] = _read_csv(os.path.join(_BASE, "valid-words.csv")) or ANSWER_WORDS

# Session state — persists across permutation runs until "new game"
_session: Dict[str, str] = {"opening": ""}

# ---------------------------------------------------------------------------
# Letter frequency weights (Wordle answer corpus approximation)
# ---------------------------------------------------------------------------
FREQ: Dict[str, int] = {
    'e': 1233, 'a': 979, 'r': 899, 'o': 754, 't': 729, 'l': 719, 'i': 671,
    's': 669, 'n': 575, 'c': 477, 'u': 467, 'y': 425, 'd': 393, 'h': 389,
    'p': 367, 'g': 311, 'm': 309, 'b': 281, 'f': 230, 'k': 210, 'w': 195,
    'v': 153, 'z':  40, 'x':  37, 'j':  27, 'q':  19,
}

# Starting coverage target for probe words; falls back to 4 → 3 → 2 if no words found
PROBE_MATCH_TARGET = 5


def _word_score(word: str, exclude: Set[str] = frozenset()) -> int:
    return sum(FREQ.get(c, 0) for c in set(word) - exclude)


# ---------------------------------------------------------------------------
# Tandem finder - greedy 3-word opening groups
# ---------------------------------------------------------------------------
def find_tandems(n: int = 12, word_pool: List[str] = None) -> List[Tuple[str, str, str]]:
    """Return top-n 3-word tandems by greedy letter-frequency coverage."""
    source = word_pool if word_pool is not None else VALID_WORDS
    # All-unique-letter words give maximum information per guess
    pool = [w for w in source if len(set(w)) == 5]

    # Score every word; take the top quarter as the candidate pool for variety
    all_scored = sorted(pool, key=_word_score, reverse=True)
    top_n = max(150, len(all_scored) // 4)
    candidates = all_scored[:top_n]

    # Shuffle within the candidate pool so each call surfaces different combos
    random.shuffle(candidates)
    top = candidates[:80]

    results: List[Tuple[str, str, str, int]] = []
    for w1 in top[:30]:
        used1 = set(w1)
        c2 = sorted(
            [w for w in pool if set(w).isdisjoint(used1)],
            key=lambda w: _word_score(w, used1), reverse=True
        )
        # Shuffle the top w2 candidates for extra variety
        c2_top = c2[:30]
        random.shuffle(c2_top)
        for w2 in c2_top[:10]:
            used2 = used1 | set(w2)
            c3 = sorted(
                [w for w in pool if set(w).isdisjoint(used2)],
                key=lambda w: _word_score(w, used2), reverse=True
            )
            for w3 in c3[:3]:
                score = (_word_score(w1) +
                         _word_score(w2, used1) +
                         _word_score(w3, used2))
                results.append((w1, w2, w3, score))

    # Sort by score so we keep quality tandems; then shuffle within the top tier
    results.sort(key=lambda x: x[3], reverse=True)
    top_results = results[:max(n * 4, 60)]
    random.shuffle(top_results)

    deduped: List[Tuple[str, str, str]] = []
    seen_sets: Set[frozenset] = set()
    for w1, w2, w3, _ in top_results:
        key = frozenset([w1, w2, w3])
        if key not in seen_sets:
            seen_sets.add(key)
            deduped.append((w1, w2, w3))
        if len(deduped) == n:
            break
    return deduped


# ---------------------------------------------------------------------------
# Permutation explorer
# ---------------------------------------------------------------------------
def generate_arrangements(
    greens: Dict[int, str],        # 0-indexed position -> letter (uppercase)
    yellows: Dict[str, List[int]], # letter (uppercase) -> excluded positions (0-indexed)
) -> List[str]:
    """
    Generate all valid 5-slot patterns.

    Green letters are fixed at their confirmed positions.
    Yellow letters must appear somewhere in the 5 slots, but not at any
    of their excluded positions.
    Remaining slots are shown as '_'.
    """
    base = ['_'] * 5
    for pos, letter in greens.items():
        if 0 <= pos < 5:
            base[pos] = letter

    free = [i for i in range(5) if base[i] == '_']

    # Yellow letters not already placed as green
    green_set = set(greens.values())
    to_place = [l for l in yellows if l not in green_set]

    if len(to_place) > len(free):
        return []

    seen: Set[str] = set()
    results: List[str] = []

    for chosen_pos in combinations(free, len(to_place)):
        for ordered in _iperm(to_place):
            valid = True
            for letter, pos in zip(ordered, chosen_pos):
                if pos in yellows.get(letter, []):
                    valid = False
                    break
            if valid:
                arr = list(base)
                for letter, pos in zip(ordered, chosen_pos):
                    arr[pos] = letter
                s = ''.join(arr)
                if s not in seen:
                    seen.add(s)
                    results.append(s)

    return results


# ---------------------------------------------------------------------------
# Word matcher - filters WORDS using green / yellow / gray constraints
# ---------------------------------------------------------------------------
def find_word_matches(
    greens: Dict[int, str],        # 0-indexed position -> confirmed letter
    yellows: Dict[str, List[int]], # letter -> excluded positions (0-indexed)
    gray: Set[str],                # letters absent from the word
    word_list: List[str] = None,   # defaults to ANSWER_WORDS
) -> List[str]:
    green_letters = set(greens.values())
    matches = []
    for word in (word_list if word_list is not None else ANSWER_WORDS):
        w = word.upper()

        # Gray letters must not appear (unless also confirmed green at a position)
        if any(c in w for c in gray if c not in green_letters):
            continue

        # Green: exact position match
        if not all(0 <= pos < 5 and w[pos] == letter for pos, letter in greens.items()):
            continue

        # Yellow: letter present, but not at its excluded positions
        ok = True
        for letter, bad_pos in yellows.items():
            if letter not in w:
                ok = False
                break
            if any(0 <= p < 5 and w[p] == letter for p in bad_pos):
                ok = False
                break
        if ok:
            matches.append(word)

    matches.sort(key=_word_score, reverse=True)
    return matches


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _hr(char: str = "-", width: int = 52) -> None:
    print(char * width)


def _banner() -> None:
    print()
    _hr("=")
    print("        W O R D L E   A S S I S T A N T")
    _hr("=")
    print(f"  Answers: {len(ANSWER_WORDS)} words  |  Valid guesses: {len(VALID_WORDS)} words")


def _parse_entry(entry: str) -> Tuple[str, List[int]]:
    """
    Parse  LETTER:pos,pos  or just  LETTER.
    Positions are 1-indexed in user input; returns 0-indexed.
    Raises ValueError on bad input.
    """
    entry = entry.strip().upper()
    if ':' in entry:
        letter, rest = entry.split(':', 1)
        letter = letter.strip()
        positions = [int(p.strip()) - 1 for p in rest.split(',') if p.strip().isdigit()]
    else:
        letter = entry.strip()
        positions = []
    if not (len(letter) == 1 and letter.isalpha()):
        raise ValueError("bad letter")
    return letter, positions


# ---------------------------------------------------------------------------
# Constraint helpers
# ---------------------------------------------------------------------------
def _print_summary(greens: Dict[int, str], yellows: Dict[str, List[int]], gray: Set[str]) -> None:
    print()
    print("  ---- Constraints so far ----")
    if greens:
        parts = [f"{l} at pos {p+1}" for p, l in sorted(greens.items())]
        print(f"  GREEN:  {',  '.join(parts)}")
    else:
        print("  GREEN:  (none)")
    if yellows:
        parts = []
        for letter, excl in sorted(yellows.items()):
            tag = f"not@{','.join(str(p+1) for p in sorted(excl))}" if excl else "in word"
            parts.append(f"{letter} ({tag})")
        print(f"  YELLOW: {',  '.join(parts)}")
    else:
        print("  YELLOW: (none)")
    print(f"  GRAY:   {', '.join(sorted(gray)) if gray else '(none)'}")
    print()


def _collect_greens(greens: Dict[int, str]) -> None:
    print("  GREEN letters - confirmed position.")
    print("  Format: LETTER:position  e.g. R:4   (blank line when done)")
    while True:
        entry = input("  green> ").strip()
        if not entry:
            break
        try:
            letter, positions = _parse_entry(entry)
            if not positions:
                print("  ! Green needs a position, e.g.  R:4")
                continue
            greens[positions[0]] = letter
        except (ValueError, IndexError):
            print("  ! Format: LETTER:position  e.g.  R:4")


def _collect_yellows(yellows: Dict[str, List[int]]) -> None:
    print()
    print("  YELLOW letters - in word, wrong position.")
    print("  Format: LETTER:excluded,positions  e.g. L:2,4  or just  L")
    print("  (blank line when done)")
    while True:
        entry = input("  yellow> ").strip()
        if not entry:
            break
        try:
            letter, positions = _parse_entry(entry)
            if letter in yellows:
                yellows[letter] = list(set(yellows[letter] + positions))
            else:
                yellows[letter] = positions
        except (ValueError, IndexError):
            print("  ! Format: LETTER:pos,pos  e.g.  L:2,4  or just  L")


def _collect_gray(gray: Set[str]) -> None:
    print()
    print("  GRAY letters - eliminated (not in the word).")
    print("  Type together e.g. atrins  (blank line to skip)")
    raw = input("  gray> ").strip().upper()
    gray |= {c for c in raw if c.isalpha()}


# ---------------------------------------------------------------------------
# Conflict checking, bulk entry, and constraint editing
# ---------------------------------------------------------------------------
def _check_conflicts(greens: Dict[int, str], yellows: Dict[str, List[int]], gray: Set[str]) -> bool:
    """Warn when a letter is marked both yellow and gray. Returns True if any found."""
    found = False
    for letter in sorted(yellows):
        if letter in gray:
            print(f"  ! Conflict: '{letter}' is both YELLOW and GRAY — "
                  f"gray is eliminating it. Use 'e' to correct.")
            found = True
    return found


def _parse_bulk(line: str, greens: Dict[int, str],
                yellows: Dict[str, List[int]], gray: Set[str]) -> bool:
    """
    Parse 'WORD colors' bulk entry (e.g. TRAIN bybyg).
    Colors: g=green, y=yellow, b=black/gray.
    Duplicate-letter safe: only marks a letter gray when it is absent from every position.
    """
    parts = line.strip().upper().split()
    if len(parts) == 2:
        word, colors = parts[0], parts[1].lower()
    elif len(parts) == 1 and len(parts[0]) >= 6:
        word, colors = parts[0][:5], parts[0][5:].lower()
    else:
        print("  ! Enter word and colors, e.g.  TRAIN bybyg")
        return False

    if len(word) != 5 or not word.isalpha():
        print("  ! Word must be exactly 5 letters.")
        return False
    if len(colors) != 5 or not all(c in 'gyb' for c in colors):
        print("  ! Color string must be 5 chars using g / y / b.")
        return False

    non_gray = {word[i] for i in range(5) if colors[i] in ('g', 'y')}

    for i, (letter, color) in enumerate(zip(word, colors)):
        if color == 'g':
            greens[i] = letter
        elif color == 'y':
            if letter in yellows:
                if i not in yellows[letter]:
                    yellows[letter].append(i)
            else:
                yellows[letter] = [i]
        else:
            if letter not in non_gray:
                gray.add(letter)

    print(f"  Applied: {word} {colors}")
    return True


def _edit_greens(greens: Dict[int, str]) -> None:
    print()
    if greens:
        parts = [f"{l} at pos {p+1}" for p, l in sorted(greens.items())]
        print(f"  Current GREEN: {', '.join(parts)}")
    else:
        print("  Current GREEN: (none)")
    print("  R:4  add/update    -2  remove position    blank to finish")
    while True:
        raw = input("  edit-green> ").strip()
        if not raw:
            break
        if raw.startswith('-'):
            try:
                pos = int(raw[1:].strip()) - 1
                if pos in greens:
                    print(f"  Removed '{greens.pop(pos)}' at position {pos+1}.")
                else:
                    print(f"  No green at position {pos+1}.")
            except ValueError:
                print("  ! Use -2 to remove green at position 2.")
        else:
            try:
                letter, positions = _parse_entry(raw)
                if not positions:
                    print("  ! Green needs a position, e.g.  R:4")
                    continue
                greens[positions[0]] = letter
                print(f"  Set: '{letter}' at pos {positions[0]+1}.")
            except (ValueError, IndexError):
                print("  ! Format: R:4")


def _edit_yellows(yellows: Dict[str, List[int]]) -> None:
    print()
    if yellows:
        parts = []
        for letter, excl in sorted(yellows.items()):
            tag = f"not@{','.join(str(p+1) for p in sorted(excl))}" if excl else "in word"
            parts.append(f"{letter} ({tag})")
        print(f"  Current YELLOW: {', '.join(parts)}")
    else:
        print("  Current YELLOW: (none)")
    print("  +R:1,2  add/merge positions    -R  remove letter    blank to finish")
    while True:
        raw = input("  edit-yellow> ").strip()
        if not raw:
            break
        if raw.startswith('-'):
            letter = raw[1:].strip().upper()
            if len(letter) == 1 and letter.isalpha():
                if letter in yellows:
                    del yellows[letter]
                    print(f"  Removed '{letter}' from yellows.")
                else:
                    print(f"  '{letter}' was not in yellows.")
            else:
                print("  ! Use -R to remove letter R.")
        elif raw.startswith('+'):
            try:
                letter, positions = _parse_entry(raw[1:])
                if letter in yellows:
                    yellows[letter] = list(set(yellows[letter] + positions))
                else:
                    yellows[letter] = positions
                tag = f"not@{','.join(str(p+1) for p in sorted(yellows[letter]))}" if yellows[letter] else "in word"
                print(f"  Updated: {letter} ({tag}).")
            except (ValueError, IndexError):
                print("  ! Format: +R:1,2 or just +R")
        else:
            print("  ! Prefix with + to add or - to remove.")


def _edit_gray(gray: Set[str]) -> None:
    print()
    print(f"  Current GRAY: {', '.join(sorted(gray)) if gray else '(none)'}")
    print("  -RT  remove letters    ABC  add letters    blank to finish")
    while True:
        raw = input("  edit-gray> ").strip().upper()
        if not raw:
            break
        if raw.startswith('-'):
            to_remove = {c for c in raw[1:] if c.isalpha()}
            removed = gray & to_remove
            gray -= to_remove
            if removed:
                print(f"  Removed: {', '.join(sorted(removed))}.")
            else:
                print("  (none of those were in gray).")
        else:
            to_add = {c for c in raw if c.isalpha()}
            gray |= to_add
            print(f"  Added: {', '.join(sorted(to_add))}.")
        print(f"  Gray is now: {', '.join(sorted(gray)) if gray else '(empty)'}.")


def _edit_constraints(greens: Dict[int, str], yellows: Dict[str, List[int]], gray: Set[str]) -> None:
    while True:
        print()
        print("  Edit:  g = greens   y = yellows   x = gray   done = finish")
        choice = input("  edit> ").strip().lower()
        if choice in ('done', 'd', ''):
            break
        elif choice == 'g':
            _edit_greens(greens)
        elif choice == 'y':
            _edit_yellows(yellows)
        elif choice in ('x', 'gray'):
            _edit_gray(gray)
        else:
            print("  Enter g, y, x, or done.")
        _check_conflicts(greens, yellows, gray)


def _show_eliminated(greens: Dict[int, str], yellows: Dict[str, List[int]], gray: Set[str]) -> None:
    """Show answer-bank words that fit the letter pattern but are ruled out by constraints."""
    if not greens and not yellows:
        print("  Add green or yellow constraints first.")
        return
    green_letters = set(greens.values())
    eliminated = []
    for word in ANSWER_WORDS:
        w = word.upper()
        if not all(0 <= pos < 5 and w[pos] == letter for pos, letter in greens.items()):
            continue
        if not all(letter in w for letter in yellows):
            continue
        reasons = []
        for c in sorted(gray):
            if c in w and c not in green_letters:
                reasons.append(f"{c} is gray")
        for letter, bad_pos in sorted(yellows.items()):
            for p in sorted(bad_pos):
                if 0 <= p < 5 and w[p] == letter:
                    reasons.append(f"{letter} at pos {p+1} (yellow excluded)")
                    break
        if reasons:
            eliminated.append((word, ', '.join(reasons)))
    _hr()
    if eliminated:
        print(f"  Eliminated candidates (answer bank): {len(eliminated)}")
        _hr()
        for word, reason in eliminated[:30]:
            print(f"  {word.upper():<8} — {reason}")
        if len(eliminated) > 30:
            print(f"  ... and {len(eliminated) - 30} more.")
    else:
        print("  No eliminated candidates found in the answer bank.")
    _hr()


def _show_arrangements(arrangements: List[str]) -> None:
    if not arrangements:
        return
    # Sort: uppercase A-Z first, then _ (ord('_')=95 > ord('Z')=90)
    sorted_arr = sorted(arrangements)
    # Group by first character so each new lead letter starts a fresh row
    groups: List[List[str]] = []
    cur_key = ''
    cur: List[str] = []
    for arr in sorted_arr:
        if arr[0] != cur_key:
            if cur:
                groups.append(cur)
            cur = [arr]
            cur_key = arr[0]
        else:
            cur.append(arr)
    if cur:
        groups.append(cur)
    cols = 4
    print("  Pos 1 2 3 4 5")
    print("  -----------")
    for i, group in enumerate(groups):
        if i > 0:
            print()
        for start in range(0, len(group), cols):
            row = group[start:start + cols]
            print("  " + "  ".join(f"{' '.join(arr):<9}" for arr in row))


def _show_word_matches(greens: Dict[int, str], yellows: Dict[str, List[int]], gray: Set[str]) -> None:
    matches = find_word_matches(greens, yellows, gray)
    _hr()
    if matches:
        print(f"  Answer bank matches: {len(matches)}")
        _hr()
        cols_w = 6
        for start in range(0, len(matches), cols_w):
            row = matches[start : start + cols_w]
            print("  " + "  ".join(f"{w.upper():<7}" for w in row))
    else:
        print("  None in answer bank - checking full valid-word list...")
        _hr()
        extended = find_word_matches(greens, yellows, gray, word_list=VALID_WORDS)
        print(f"  Valid-word matches: {len(extended)}")
        _hr()
        if extended:
            cols_w = 6
            for start in range(0, len(extended), cols_w):
                row = extended[start : start + cols_w]
                print("  " + "  ".join(f"{w.upper():<7}" for w in row))
        else:
            print("  No matches in either list - check your constraints.")
    _hr()


# ---------------------------------------------------------------------------
# Letters-in-play helper
# ---------------------------------------------------------------------------
def _letters_in_play(matches: List[str], greens: Dict[int, str],
                     yellows: Dict[str, List[int]]) -> str:
    """Letters still undiscovered: appear in remaining answers but are not yet confirmed (not green, not yellow)."""
    locked_positions = set(greens.keys())
    known_letters = set(greens.values()) | set(yellows.keys())
    letters: Set[str] = set()
    for word in matches:
        for i, ch in enumerate(word.upper()):
            if i not in locked_positions and ch not in known_letters:
                letters.add(ch)
    return ' '.join(sorted(letters))


# ---------------------------------------------------------------------------
# Probe-word finder
# ---------------------------------------------------------------------------
def _find_probe_words(unknown_letters: Set[str], answer_pool_set: Set[str]) -> Tuple[List[str], int]:
    """
    Find up to 5 words from VALID_WORDS (excluding answer_pool_set) that cover
    the most letters from unknown_letters.  Tries PROBE_MATCH_TARGET down to 2.
    Candidates are shuffled so repeated calls surface different words.
    Returns (words, actual_target).
    """
    if not unknown_letters:
        return [], 0
    candidates = [w for w in VALID_WORDS if w not in answer_pool_set]
    random.shuffle(candidates)
    target = PROBE_MATCH_TARGET
    while target >= 2:
        qualifying = [w for w in candidates
                      if len(unknown_letters & set(w.upper())) >= target]
        if qualifying:
            return qualifying[:5], target
        target -= 1
    return [], 0


# ---------------------------------------------------------------------------
# Menu handlers
# ---------------------------------------------------------------------------
def show_tandems(ask_pool: bool = True) -> None:
    print()
    if ask_pool:
        print("  Use common words only (answer bank), or the full valid-guess list?")
        print(f"  c = common ({len(ANSWER_WORDS)} words)   f = full ({len(VALID_WORDS)} words)  [default: common]")
        choice = input("  Pool: ").strip().lower()
        pool = VALID_WORDS if choice == 'f' else ANSWER_WORDS
    else:
        pool = ANSWER_WORDS
    print("\n  Computing top opening tandems...")
    tandems = find_tandems(12, word_pool=pool)
    print()
    _hr()
    print(f"  {'#':>3}  {'Word 1':<9} {'Word 2':<9} {'Word 3':<9} Letters")
    _hr()
    for i, (w1, w2, w3) in enumerate(tandems, 1):
        cov = len(set(w1) | set(w2) | set(w3))
        print(f"  {i:>3}. {w1.upper():<9} {w2.upper():<9} {w3.upper():<9} {cov} unique")
    _hr()
    print("  Tip: any row eliminates up to 15 letters in 3 guesses.\n")
    sel = input("  Select a row to use as your opening (or press Enter to skip): ").strip()
    if sel.isdigit():
        idx = int(sel) - 1
        if 0 <= idx < len(tandems):
            w1, w2, w3 = tandems[idx]
            _session["opening"] = f"{w1.upper()} \xb7 {w2.upper()} \xb7 {w3.upper()}"
            print(f"  Saved: {_session['opening']}")


def run_permutations() -> bool:
    print()
    print("  Positions are numbered 1-5 (left to right).")
    print("  Blanks ( _ ) in output = position not yet known.")
    print()

    greens:  Dict[int, str]       = {}
    yellows: Dict[str, List[int]] = {}
    gray:    Set[str]             = set()
    guess_count = 0
    history: List = []

    # ---- first guess ----
    print("  Enter your first guess result:")
    print("  Bulk: WORD colors  (g=green, y=yellow, b=black)  e.g. TRAIN bybyg")
    print("  Press Enter to use manual green / yellow / gray input instead.")
    history.append(copy.deepcopy((greens, yellows, gray, guess_count)))
    while True:
        raw = input("  bulk> ").strip()
        if not raw:
            _collect_greens(greens)
            _collect_yellows(yellows)
            _collect_gray(gray)
            break
        if raw.lower() in ('q', 'quit'):
            return False
        if _parse_bulk(raw, greens, yellows, gray):
            break
    guess_count += 1
    _check_conflicts(greens, yellows, gray)

    while True:
        if not greens and not yellows and not gray:
            print("  Nothing entered.")
            return False

        arrangements = generate_arrangements(greens, yellows)
        n = len(arrangements)

        # ---- header ----
        print()
        _hr()
        summary_parts = []
        for pos, letter in sorted(greens.items()):
            summary_parts.append(f"{letter}(green@{pos+1})")
        for letter, excl in sorted(yellows.items()):
            tag = f"not@{','.join(str(p+1) for p in sorted(excl))}" if excl else "yellow"
            summary_parts.append(f"{letter}({tag})")
        if gray:
            summary_parts.append(f"gray:{','.join(sorted(gray))}")
        print(f"  Constraints: {', '.join(summary_parts)}")
        print(f"  Arrangements: {n}  (_ = unknown position)")
        _hr()

        # ---- permutation grid ----
        if not arrangements:
            print("  No valid arrangements - check your constraints.")
        else:
            _show_arrangements(arrangements)

        # ---- answer count + letters in play ----
        answer_matches = find_word_matches(greens, yellows, gray)
        answer_count = len(answer_matches)
        print()
        if answer_count:
            print(f"  {answer_count} word(s) in the answer bank fit these constraints.")
            lip = _letters_in_play(answer_matches, greens, yellows)
            if lip:
                print(f"  Letters still in play: {lip}")
                unknown_set = set(lip.split())
                probes, ptarget = _find_probe_words(unknown_set, set(answer_matches))
                if probes:
                    print(f"  Probe words ({ptarget}/{len(unknown_set)} unknowns): {'  '.join(w.upper() for w in probes)}")
        else:
            valid_matches = find_word_matches(greens, yellows, gray, word_list=VALID_WORDS)
            valid_count = len(valid_matches)
            print(f"  0 answer-bank matches  ({valid_count} in full valid-word list).")
            lip = _letters_in_play(valid_matches, greens, yellows)
            if lip:
                print(f"  Letters still in play: {lip}")
                unknown_set = set(lip.split())
                probes, ptarget = _find_probe_words(unknown_set, set(valid_matches))
                if probes:
                    print(f"  Probe words ({ptarget}/{len(unknown_set)} unknowns): {'  '.join(w.upper() for w in probes)}")

        # ---- opening reminder (hide once 15 letters known) ----
        constraint_size = len(greens) + len(yellows) + len(gray)
        if _session["opening"] and constraint_size < 15:
            print(f"  Opening: {_session['opening']}")

        # ---- action menu ----
        show_x = guess_count >= 2 or constraint_size >= 10
        while True:
            print()
            print("  [Enter]  Enter next guess      s  Show word matches")
            print("  m  Add more clues              p  Print constraint summary")
            if show_x:
                print("  e  Edit constraints            x  Show eliminated candidates")
            else:
                print("  e  Edit constraints")
            print("  n  New game    u  Undo last guess    q  Done")
            action = input("  > ").strip().lower()

            if action in ('b', ''):
                print()
                print("  Enter word and colors on one line  (blank to cancel):")
                print("  Colors: g = green, y = yellow, b = black/gray")
                print("  Example: TRAIN bybyg")
                applied = False
                while True:
                    raw = input("  bulk> ").strip()
                    if not raw:
                        break
                    history.append(copy.deepcopy((greens, yellows, gray, guess_count)))
                    if _parse_bulk(raw, greens, yellows, gray):
                        _check_conflicts(greens, yellows, gray)
                        guess_count += 1
                        applied = True
                        break
                    else:
                        history.pop()
                if applied:
                    break

            elif action == 's':
                print()
                _show_word_matches(greens, yellows, gray)

            elif action == 'm':
                history.append(copy.deepcopy((greens, yellows, gray, guess_count)))
                _print_summary(greens, yellows, gray)
                _collect_greens(greens)
                _collect_yellows(yellows)
                _collect_gray(gray)
                _check_conflicts(greens, yellows, gray)
                guess_count += 1
                break

            elif action == 'p':
                _print_summary(greens, yellows, gray)

            elif action == 'e':
                history.append(copy.deepcopy((greens, yellows, gray, guess_count)))
                _edit_constraints(greens, yellows, gray)
                break

            elif action == 'x' and show_x:
                print()
                _show_eliminated(greens, yellows, gray)

            elif action == 'u':
                if not history:
                    print("  Nothing to undo.")
                else:
                    snap_g, snap_y, snap_gray, snap_count = history.pop()
                    greens.clear();  greens.update(snap_g)
                    yellows.clear(); yellows.update(snap_y)
                    gray.clear();    gray.update(snap_gray)
                    guess_count = snap_count
                    break

            elif action == 'n':
                _session["opening"] = ""
                show_tandems(ask_pool=False)
                return True

            elif action in ('q', 'quit'):
                print()
                return False

            else:
                print("  Enter s, m, p, e, x, n, u, or q.")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def main() -> None:
    _banner()
    show_tandems(ask_pool=False)
    while run_permutations():
        pass
    try:
        while True:
            print()
            print("  1  New tandem suggestions")
            print("  2  Permutation explorer")
            print("  n  New game")
            print("  q  Quit")
            print()
            choice = input("  Choice: ").strip().lower()
            if choice == '1':
                show_tandems()
            elif choice == '2':
                while run_permutations():
                    pass
            elif choice == 'n':
                _session["opening"] = ""
                show_tandems(ask_pool=False)
                while run_permutations():
                    pass
            elif choice in ('q', 'quit', 'exit'):
                print("\n  Good luck!\n")
                break
            else:
                print("  Enter 1, 2, n, or q.")
    except (KeyboardInterrupt, EOFError):
        print("\n\n  Good luck!\n")


if __name__ == "__main__":
    main()
