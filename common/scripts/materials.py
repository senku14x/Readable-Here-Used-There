"""Frozen materials: phrasing bank and direct carriers, controlled carriers and word banks, category bank, codebook and sum materials, plain-sentence templates.

Nothing here is derived from model outcomes. Eligibility (single-token, overlap) is checked
mechanically by `rendering.py` against the actual tokenizer and rendered contexts.
"""

# ---------------------------------------------------------------- Appendix B1: carriers (controlled organism)
CARRIERS = {
    "C0": "The committee reviewed the annual budget and approved funding for several new community programs before the long meeting finally adjourned.",
    "C1": "After a brief announcement the passengers boarded quietly and the doors slid shut, and soon the whole platform stood empty and silent.",
    "C2": "Dust settled slowly over the village square while two birds watched from the old doorway",
    "C3": "Several boxes of files were moved to the archive room, and the clerk updated every label, checked the totals twice, and locked the cabinet before leaving for the night.",
}
FIT_CARRIERS = ["C0", "C1"]
EVAL_CARRIERS = ["C2", "C3"]

# ---------------------------------------------------------------- Appendix A: direct carriers
DIRECT_CARRIERS = {
    "D0": "The old painting hung crookedly on the wall.",
    "D3": "I forgot my umbrella at work yesterday afternoon.",
    "D5": "She carefully placed the letter back inside the wooden drawer.",
    "D8": "The garden behind the house grew wild after years of neglect.",
    "D11": "She quietly closed the door and walked down the long empty hallway alone.",
    "D14": "Nobody expected the meeting to run so late into the evening that day.",
    "D16": "The library stayed open later than usual because of the upcoming holiday.",
    "D19": "He spent the entire weekend reorganizing the cluttered garage by himself.",
}
DIRECT_FIT_CARRIERS = ["D0", "D3", "D5", "D8"]
DIRECT_EVAL_CARRIERS = ["D11", "D14", "D16", "D19"]

# ---------------------------------------------------------------- Appendix B1: word banks
FIT_WORDS = ["anchor", "apple", "arrow", "badge", "basket", "bread", "brick", "bridge",
             "bucket", "button", "camel", "camera", "church", "cloud", "coffee", "compass"]
CALIBRATION_WORDS = ["orange", "guitar", "tiger", "mountain", "diamond", "thunder", "castle", "rocket"]
DECOYS = ["dragon", "drawer", "forest", "fork", "hammer", "horse", "knife", "lion"]
EVAL_BANK_1 = [("cat", "dress"), ("snake", "turtle"), ("airport", "fish"), ("library", "toy"),
               ("dish", "moon"), ("fort", "heart"), ("bubble", "rug"), ("bear", "coal")]
EVAL_BANK_2 = [("card", "lake"), ("glass", "silver"), ("river", "shield"), ("monkey", "queen"),
               ("king", "paper"), ("gold", "train"), ("cup", "engine"), ("letter", "sword")]

# ---------------------------------------------------------------- Appendix A: direct phrasing bank
DIRECT_PHRASINGS = {
    # family, id, text
    "think": ("focus", "Think about {X} while you write."),
    "concentrate": ("focus", "Concentrate on {X} while you write the sentence."),
    "focus": ("focus", "Try to focus on {X} while you write the sentence."),
    "hold": ("focus", "Hold {X} in mind as you write."),
    "keep": ("focus", "Keep {X} in your thoughts."),
    "irrelevant-ignore": ("dismiss", "{X} is irrelevant — ignore it."),
    "irrelevant": ("dismiss", "{X} is irrelevant."),
    "ignore": ("dismiss", "Ignore {X}."),
    "parenthetical": ("dismiss", "(Ignore: {X}.)"),
    "distraction": ("dismiss", "{X} is a distraction — push it out of your mind."),
    "unrelated": ("dismiss", "{X} is unrelated to this task."),
    "dont": ("suppress", "Don't think about {X}."),
    "avoid": ("suppress", "Avoid thinking about {X}."),
    "clear": ("suppress", "Clear your mind of {X}."),
    "try-hard": ("suppress", "Try very hard not to think about {X} while you write."),
    "forbidden": ("suppress", "You are forbidden from thinking about {X}."),
    "whatever": ("suppress", "Whatever you do, do not think about {X}."),
    "worry": ("suppress", "Don't worry about {X}."),
    "bare": ("mention", "{X}."),
    "parentheses": ("mention", "({X})"),
    "conversation": ("mention", "{X} came up in conversation."),
    "appears": ("mention", "{X} appears in this prompt."),
    "reference": ("mention", "This prompt contains a reference to {X}."),
    "phrase": ("mention", "There is a phrase, {X}, included here."),
}
DIRECT_PRIMARY_PAIR = ("hold", "conversation")
DIRECT_FIT_FOCUS = ["think", "concentrate", "focus"]
DIRECT_FIT_MENTION = ["bare", "parentheses", "conversation"]
DIRECT_EVAL_FOCUS = ["hold", "keep"]
DIRECT_EVAL_MENTION = ["appears", "reference", "phrase"]

# ---------------------------------------------------------------- Appendix B2: category bank
CATEGORIES = {
    "birds": (["sparrow", "robin", "eagle"], ["owl", "duck", "goose", "raven", "pigeon", "swan"]),
    "fish": (["salmon", "tuna", "trout"], ["cod", "carp", "bass", "herring", "perch", "sardine"]),
    "insects": (["ant", "bee", "wasp"], ["beetle", "moth", "fly", "mosquito", "cricket", "butterfly"]),
    "reptiles": (["lizard", "cobra", "python"], ["turtle", "snake", "crocodile", "gecko", "iguana", "alligator"]),
    "citrus fruits": (["lemon", "lime", "grapefruit"], ["orange", "mandarin", "tangerine", "pomelo", "citron", "kumquat"]),
    "nuts": (["almond", "walnut", "cashew"], ["pecan", "hazelnut", "pistachio", "macadamia", "chestnut", "peanut"]),
    "flowers": (["rose", "tulip", "daisy"], ["lily", "orchid", "violet", "iris", "poppy", "lotus"]),
    "trees": (["oak", "pine", "birch"], ["maple", "elm", "cedar", "willow", "beech", "spruce"]),
    "tools": (["wrench", "chisel", "screwdriver"], ["hammer", "saw", "drill", "pliers", "axe", "shovel"]),
    "mammals": (["elephant", "giraffe", "zebra"], ["horse", "rabbit", "mouse", "camel", "cow", "sheep"]),
    "musical instruments": (["piano", "flute", "violin"], ["guitar", "trumpet", "drum", "harp", "cello", "clarinet"]),
    "vegetables": (["carrot", "potato", "onion"], ["cabbage", "spinach", "broccoli", "celery", "leek", "turnip"]),
    "vehicles": (["truck", "bus", "tractor"], ["car", "bicycle", "motorcycle", "scooter", "van", "train"]),
    "gemstones": (["ruby", "jade", "pearl"], ["diamond", "emerald", "sapphire", "opal", "amethyst", "topaz"]),
    "furniture": (["sofa", "chair", "table"], ["desk", "bed", "cabinet", "stool", "dresser", "bench"]),
    "ocean creatures": (["whale", "dolphin", "squid"], ["octopus", "crab", "lobster", "shrimp", "jellyfish", "starfish"]),
}
CATEGORY_ORDER = list(CATEGORIES)
CATEGORY_PAIRS = [(CATEGORY_ORDER[i], CATEGORY_ORDER[i + 1]) for i in range(0, 16, 2)]

# ---------------------------------------------------------------- Appendix B3: codebook and sums
CODE_LETTERS = ["B", "D", "F", "H", "K", "M", "Q", "V"]
SUMS = [("seven", ("two", "five"), ("three", "four")), ("eight", ("two", "six"), ("three", "five")),
        ("nine", ("two", "seven"), ("four", "five")), ("ten", ("two", "eight"), ("three", "seven")),
        ("eleven", ("three", "eight"), ("four", "seven")), ("twelve", ("four", "eight"), ("five", "seven")),
        ("thirteen", ("five", "eight"), ("six", "seven")), ("fourteen", ("six", "eight"), ("five", "nine"))]

# ---------------------------------------------------------------- Appendix C: plain-sentence contexts
PLAIN_TEMPLATES = [
    "I saw a {m} yesterday.", "The {m} was the first thing she mentioned.", "Nobody expected the {m} to be there.",
    "He wrote a short note about the {m}.", "A picture of a {m} hung on the wall.", "They talked about the {m} for an hour.",
    "The {m} appeared in the last chapter.", "My neighbor keeps asking about the {m}.", "There was a {m} in the old photograph.",
    "The story began with a {m}.", "She drew a {m} in her notebook.", "The word {m} was printed on the label.",
]
PLAIN_FIT = PLAIN_TEMPLATES[:8]
PLAIN_VAL = PLAIN_TEMPLATES[8:]
LETTER_TEMPLATES = ["The code letter is {m}.", "The label reads {m}.", "The symbol on the card is {m}.",
                    "She selected the letter {m}.", "The assigned marker is {m}.", "He wrote {m} in the answer box."]
LETTER_FIT = LETTER_TEMPLATES[:4]
LETTER_VAL = LETTER_TEMPLATES[4:]

# H1.8 computed_sums: numeric-word contexts for the RESID sum axis (registered before running; fit 1-4, validate 5-6)
NUMBER_TEMPLATES = ["The answer was {m}.", "She counted to {m}.", "The total came to {m}.",
                    "He wrote {m} on the board.", "The final number is {m}.", "They stopped at {m}."]
NUMBER_FIT = NUMBER_TEMPLATES[:4]
NUMBER_VAL = NUMBER_TEMPLATES[4:]
