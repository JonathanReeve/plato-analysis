# -*- coding: UTF-8 -*-
"""Language specific functions."""

from __future__ import unicode_literals
import re
import collections

VOWELS = 'aoeuiäàâáåãëéèêóòöôõðùúüìíïî'  # y is special case; true for en.

specialSyllables_en = """\
tottered 2
chummed 1
peeped 1
moustaches 2
shamefully 3
messieurs 2
satiated 4
sailmaker 4
sheered 1
disinterred 3
propitiatory 6
bepatched 2
particularized 5
caressed 2
trespassed 2
sepulchre 3
flapped 1
hemispheres 3
pencilled 2
motioned 2
poleman 2
slandered 2
sombre 2
etc 4
sidespring 2
mimes 1
effaces 2
mr 2
mrs 2
ms 1
dr 2
st 1
sr 2
jr 2
truckle 2
foamed 1
fringed 2
clattered 2
capered 2
mangroves 2
suavely 2
reclined 2
brutes 1
effaced 2
quivered 2
h'm 1
veriest 3
sententiously 4
deafened 2
manoeuvred 3
unstained 2
gaped 1
stammered 2
shivered 2
discoloured 3
gravesend 2
60 2
lb 1
unexpressed 3
greyish 2
unostentatious 5
"""

fallback_cache = {}
_fallback_subsyl = ["cial", "tia", "cius", "cious", "gui", "ion", "iou",
		"sia$", ".ely$"]
_fallback_addsyl = ["ia", "riet", "dien", "iu", "io", "ii",
		"[aeiouy]bl$", "mbl$",
		"[aeiou]{3}",
		"^mc", "ism$",
		"(.)(?!\\1)([aeiouy])\\2l$",
		"[^l]llien",
		"^coad.", "^coag.", "^coal.", "^coax.",
		"(.)(?!\\1)[gq]ua(.)(?!\\2)[aeiou]",
		"dnt$"]
fallback_subsyl = [re.compile(a) for a in _fallback_subsyl]
fallback_addsyl = [re.compile(a) for a in _fallback_addsyl]


def _normalize_word(word):
	return word.strip().lower()

# Read syllable overrides and populate cache with them
for line in specialSyllables_en.splitlines():
	line = line.strip()
	if line:
		toks = line.split()
		assert len(toks) == 2
		fallback_cache[_normalize_word(toks[0])] = int(toks[1])


def countsyllables_en(word):
	"""Fallback syllable counter.

	This is based on the algorithm in Greg Fast's perl module
	Lingua::EN::Syllable."""
	if not word:
		return 0

	# Check for a cached syllable count
	if word in fallback_cache:
		return fallback_cache[word]

	# Remove final silent 'e'
	if word[-1] == "e":
		word = word[:-1]

	# Count vowel groups
	result = 0
	prev_was_vowel = False
	for char in word:
		is_vowel = char in VOWELS or char == 'y'
		if is_vowel and not prev_was_vowel:
			result += 1
		prev_was_vowel = is_vowel

	# Add & subtract syllables
	for r in fallback_addsyl:
		if r.search(word):
			result += 1
	for r in fallback_subsyl:
		if r.search(word):
			result -= 1

	# Cache the syllable count
	fallback_cache[word] = result

	return result


def countsyllables_nlde(word):
	"""Count syllables for Dutch / German words by counting vowel-consonant or
	consonant-vowel pairs, depending on the first character being a vowel or
	not. If it is, a trailing e will be handled with a special rule."""
	result = 0
	prev_was_vowel = word[0] in VOWELS
	for char in word[1:]:
		is_vowel = char in VOWELS
		if prev_was_vowel and not is_vowel:
			result += 1
		prev_was_vowel = is_vowel

	if (len(word) > 1 and word[0] in VOWELS
			and word.endswith('e') and not word[-2] in VOWELS):
		result += 1
	return result or 1


conjuction_en = r'and|but|or|yet|nor'
preposition_en = (
		'board|about|above|according to|across from'
		'|after|against|alongside|alongside of|along with'
		'|amid|among|apart from|around|aside from|at|away from'
		'|back of|because of|before|behind|below|beneath|beside'
		'|besides|between|beyond|but|by means of'
		'|concerning|considering|despite|down|down from|during'
		'|except|except for|excepting for|from among'
		'|from between|from under|in addition to|in behalf of'
		'|in front of|in place of|in regard to|inside of|inside'
		'|in spite of|instead of|into|like|near to|off'
		'|on account of|on behalf of|onto|on top of|on|opposite'
		'|out of|out|outside|outside of|over to|over|owing to'
		'|past|prior to|regarding|round about|round'
		'|since|subsequent to|together|with|throughout|through'
		'|till|toward|under|underneath|until|unto|up'
		'|up to|upon|with|within|without|across|along'
		'|by|of|in|to|near|of|from')
pronoun_en = (
		'i|me|we|us|you|he|him|she|her|it|they'
		'|them|thou|thee|ye|myself|yourself|himself'
		'|herself|itself|ourselves|yourselves|themselves'
		'|oneself|my|mine|his|hers|yours|ours|theirs|its'
		'|our|that|their|these|this|those|your')
words_en = collections.OrderedDict([
	('tobeverb', re.compile(
		r'\b(be|being|was|were|been|are|is)\b', re.IGNORECASE)),
	('auxverb', re.compile(
		r"\b(will|shall|cannot|may|need to|would|should"
		r"|could|might|must|ought|ought to|can't|can)\b", re.IGNORECASE)),
	('conjunction', re.compile(
		'\\b(%s)\\b' % conjuction_en, re.IGNORECASE)),
	('pronoun', re.compile(
		'\\b(%s)\\b' % pronoun_en, re.IGNORECASE)),
	('preposition', re.compile(
		'\\b(%s)\\b' % preposition_en, re.IGNORECASE)),
    # a bit limited, but this is exactly what the original style(1) did:
	('nominalization', re.compile(
		r'\b\w{3,}(tion|ment|ence|ance)\b', re.IGNORECASE | re.UNICODE)),
	])

beginnings_en = collections.OrderedDict([
	('pronoun', re.compile(
		'(^|\\n)(%s)\\b' % pronoun_en, re.IGNORECASE)),
	('interrogative', re.compile(
		r'(^|\n)(why|who|what|whom|when|where|how)\b', re.IGNORECASE)),
	('article', re.compile(
		r'(^|\n)(the|a|an)\b', re.IGNORECASE)),
	('subordination', re.compile(
		r"(^|\n)(after|because|lest|till|'til|although"
		r"|before|now that|unless|as|even if|provided that|provided"
		r"|until|as if|even though|since|as long as|so that"
		r"|whenever|as much as|if|than|as soon as|inasmuch"
		r"|in order that|though|while)\b", re.IGNORECASE)),
	('conjunction', re.compile(
		'(^|\\n)(%s)\\b' % conjuction_en, re.IGNORECASE)),
	('preposition', re.compile(
		'(^|\\n)(%s)\\b' % preposition_en, re.IGNORECASE)),
	])

conjuction_nl = 'en|maar|of|want|dus|noch'
preposition_nl = (
		"à|aan|ad|achter|behalve|beneden|betreffende|bij"
		"|binnen|blijkens|boven|buiten|circa|conform|contra"
		"|cum|dankzij|door|gedurende|gezien|hangende|in"
		"|ingevolge|inzake|jegens|krachtens|langs|met|middels"
		"|mits|na|naar|naast|nabij|namens|niettegenstaande"
		"|nopens|om|omstreeks|omtrent|ondanks|onder|ongeacht"
		"|onverminderd|op|over|overeenkomstig|per|plus|richting"
		"|qua|rond|rondom|sedert|staande|te|tegen|tegenover"
		"|ten|ter|tijdens|tot|tussen|uit|uitgezonderd|van"
		"|vanaf|vanuit|vanwege|versus|via|volgens|voor"
		"|voorbij|wegens|zonder")
pronoun_nl = (
		# persoonlijk voornaamwoord
		"ik|jij|je|u|hij|hem|zij|ze|haar|het"
		"|wij|we|ons|jullie|hen|hun"
		# wederkerend voornaamwoord
		"mij|me|mijzelf|mezelf|je|jezelf|uzelf"
		"|zich|zichzelf|haarzelf|onszelf"
		"|elkaar|elkaars|elkander|elkanders|mekaar|mekaars"
		# pers. vnw: archaisch
		"gij|ge"
		"|mijnen|deinen|zijnen|haren|onzen|uwen|hunnen|haren"
		"|mijner|deiner|zijner|harer|onzer|uwer|hunner|harer"
		"|mijnes|deines|zijnes|hares|onzes|uwes|hunnes|hares")
words_nl = collections.OrderedDict([
	('tobeverb', re.compile(
		r'\b(ben|bent|is|zijn|was|waren)\b', re.IGNORECASE)),
	('auxverb', re.compile(
		"\\b("
		# NB: past perfect forms of these verbs
		# ('gehad', 'geweest', 'geworden') are not auxiliary.
		# with past perfect verb
		"heb|hebt|heeft|hebben|had|hadden"
		"|word|wordt|worden|werd|werden"
		# "|ben|bent|is|zijn|was|waren"
		# with infinitive
		"|zal|zult|zullen|zou|zouden"
		"|kan|kan|kunt|kunnen|kon|konden"
		"|wil|wilt|willen|wilde|wilden|wou|wouden"
		"|moet|moeten|moest|moesten"
		# "|mag|mogen|mocht|mochten"
		# "|hoef|hoeft|hoeven|hoefde|hoefden"
		# "|doe|doet|doen|deed|deden"
		")\\b", re.IGNORECASE)),
	('conjunction', re.compile(
		'\\b(%s)\\b' % conjuction_nl, re.IGNORECASE)),
	('pronoun', re.compile(
		'\\b(%s)\\b' % pronoun_nl, re.IGNORECASE)),
	('preposition', re.compile(
		'\\b(%s)\\b' % preposition_nl, re.IGNORECASE)),
    # a bit limited, but this is exactly what the original style(1) did:
	('nominalization', re.compile(
		r'\b.{3,}(tie|heid|ing|end|ende)\b', re.IGNORECASE)),
	])
beginnings_nl = collections.OrderedDict([
	('pronoun', re.compile(
		'(^|\\n)(%s)\\b' % pronoun_nl, re.IGNORECASE)),
	('interrogative', re.compile(
		r'(^|\n)(wie|wat|waar|waarom|wanneer|hoe|welk|welke)\b',
		re.IGNORECASE)),
	('article', re.compile(
		r"(^|\n)(de|het|een|'t)\b", re.IGNORECASE)),
	('subordination', re.compile(
		"(^|\\n)("
		# onderschikkende voegwoorden
		"aangezien|als|alsof|behalve|daar|daarom|dat"
		"|derhalve|doch|doordat|hoewel|indien|mits|nadat"
		"|noch|ofschoon|omdat|ondanks|opdat|sedert|sinds"
		"|tenzij|terwijl|toen|totdat|voordat|wanneer"
		"|zoals|zodat|zodra|zonder dat"
		# infitief constructies
		"|om te)\\b", re.IGNORECASE)),
	('conjunction', re.compile(
		'(^|\\n)(%s)\\b' % conjuction_nl, re.IGNORECASE)),
	('preposition', re.compile(
		'(^|\\n)(%s)\\b' % preposition_nl, re.IGNORECASE)),
	])

conjuction_de = ('und|oder|aber|sondern|doch|nur|bloß|denn'
		'weder|noch|sowie')
preposition_de = (
	'aus|außer|bei|mit|nach|seit|von|zu'
	'|bis|durch|für|gegen|ohne|um|an|auf'
	'|hinter|in|neben|über|unter|vor|zwischen'
	'|anstatt|statt|trotz|während|wegen')
pronoun_de = (
	'ich|du|er|sie|es|wir|ihr'  # sie           # Nominativ
	'|mich|dich|ihn|uns|euch'  # sie             # Akkusativ
	'|mir|dir|ihm|ihnen'  # uns euch ihr         # Dativ
	'|mein|dein|sein|unser|euer'  # ihr          # Genitiv
	'|meiner|deiner|seiner|unserer|eurer|ihrer'  # Genitiv
	'|meine|deine|seine|unsere|eure|ihre'        # Genitiv
	'|meines|deines|seines|unseres|eures|ihres'  # Genitiv
	'|meinem|deinem|seinem|unserem|eurem|ihrem'  # Genitiv
	'|meinen|deinen|seinen|unseren|euren|ihren'  # Genitiv
		)
words_de = collections.OrderedDict([
	('tobeverb', re.compile("\\b("
		"sein|bin|bist|ist|sind|seid|war|warst|wart"
		"|waren|gewesen|wäre|wärst|wär|wären|wärt|wäret"
		")\\b", re.IGNORECASE)),
	('auxverb', re.compile("\\b("
		"haben|habe|hast|hat|habt|gehabt|hätte|hättest"
		"|hätten|hättet"
		"|werden|werde|wirst|wird|werdet|geworden|würde"
		"|würdest|würden|würdet"
		"|können|kann|kannst|könnt|konnte|konntest|konnten"
		"|konntet|gekonnt|könnte|könntest|könnten|könntet"
		"|müssen|muss|muß|musst|müsst|musste|musstest|mussten"
		"|gemusst|müsste|müsstest|müssten|müsstet"
		"|sollen|soll|sollst|sollt|sollte|solltest|solltet"
		"|sollten|gesollt"
		")\\b", re.IGNORECASE)),
	('conjunction', re.compile(
		'\\b(%s)\\b' % conjuction_de, re.IGNORECASE)),
	('pronoun', re.compile(
		'\\b(%s)\\b' % pronoun_de, re.IGNORECASE)),
	('preposition', re.compile(
		'\\b(%s)\\b' % preposition_de, re.IGNORECASE)),
	('nominalization', re.compile(
		r'\b.{3,}(ung|heit|keit|nis|tum)\b', re.IGNORECASE)),
	])
beginnings_de = collections.OrderedDict([
	('pronoun', re.compile(
		'(^|\\n)(%s)\\b' % pronoun_de, re.IGNORECASE)),
	('interrogative', re.compile(
		r'(^|\n)(wer|was|wem|wen|wessen|wo|wie|warum|weshalb|wann'
		r'|wieso|weswegen)\b', re.IGNORECASE)),
	('article', re.compile(
		r"(^|\n)(der|die|das|des|dem|den|ein|eine|einer|eines|einem|einen)\b",
		re.IGNORECASE)),
	('subordination', re.compile("(^|\\n)("
		# bei Nebensätzen
		"als|als dass|als daß|als ob|anstatt dass|anstatt daß"
		"|ausser dass|ausser daß|ausser wenn|bevor|bis|da|damit"
		"|dass|daß|ehe|falls|indem|je|nachdem|ob|obgleich"
		"|obschon|obwohl|ohne dass|ohne daß|seit|so daß|sodass"
		"|sobald|sofern|solange|so oft|statt dass|statt daß"
		"|während|weil|wenn|wenn auch|wenngleich|wie|wie wenn"
		"|wiewohl|wobei|wohingegen|zumal"
		# bei Infinitivgruppen
		"|als zu|anstatt zu|ausser zu|ohne zu|statt zu|um zu"
		")\\b", re.IGNORECASE)),
	('conjunction', re.compile(
		'(^|\\n)(%s)\\b' % conjuction_de, re.IGNORECASE)),
	('preposition', re.compile(
		'(^|\\n)(%s)\\b' % preposition_de, re.IGNORECASE)),
	])

LANGDATA = dict(
		en=dict(
			syllables=countsyllables_en,
			words=words_en,
			beginnings=beginnings_en),
		nl=dict(
			syllables=countsyllables_nlde,
			words=words_nl,
			beginnings=beginnings_nl),
		de=dict(
			syllables=countsyllables_nlde,
			words=words_de,
			beginnings=beginnings_de),
		)
