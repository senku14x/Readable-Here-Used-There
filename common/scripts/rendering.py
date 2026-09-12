"""Prompt construction and token geometry for the three organisms.

Every render tokenizes the complete conversation string and resolves spans by character offsets.
Mechanical gates (§5): decoded source, user-carrier, assistant-carrier and query spans must equal
the intended strings; the copy organism contains two carrier occurrences; no padding.

Conditions are named by their scientific meaning. Exact tails are frozen, byte for byte.
"""
import re

COPY = "copy the following text exactly, word for word"
COPY_NOW = "Now " + COPY

# §2.1 controlled word-copy organism: tail follows `Here is the word "{X}"`
CONTROLLED_TAILS = {
    "maintain":       '. Keep that word in mind while you ' + COPY,
    "mention":        '. That word occurs one time. ' + COPY_NOW,          # spec "Mention/control"
    "ignore":         '. That word is irrelevant here. ' + COPY_NOW,
    "do_not_think":   '. Do not think about that word. ' + COPY_NOW,
    "never_think":    '. Never think about that word. ' + COPY_NOW,
}
CONTROLLED_INTRO = 'Here is the word '
PLAIN_MENTION_TAIL = '. ' + COPY_NOW                        # `{X}. Now copy ...` (unquoted, no intro)
ABSENT_HEAD = 'A single passage of text is given below. ' + COPY_NOW
PULSE_BASE_HEAD = 'Copy the following text exactly, word for word'

# §2.3 target-presentation factorial bodies (quoted/bare × copy/directed wording), each ends `:\n\n{carrier}`
PRESENTATION_BODIES = {
    ("quoted", "copy", "maintain"):    lambda X: f'Here is the word "{X}"' + CONTROLLED_TAILS["maintain"],
    ("quoted", "copy", "mention"):     lambda X: f'Here is the word "{X}"' + CONTROLLED_TAILS["mention"],
    ("quoted", "directed", "maintain"): lambda X: f'Here is the word "{X}". Hold that word in mind as you write. ' + COPY_NOW,
    ("quoted", "directed", "mention"):  lambda X: f'Here is the word "{X}". That word came up in conversation. ' + COPY_NOW,
    ("bare", "copy", "maintain"):      lambda X: f'{X}. Keep that word in mind while you ' + COPY,
    ("bare", "copy", "mention"):       lambda X: f'{X}. That word occurs one time. ' + COPY_NOW,
    ("bare", "directed", "maintain"):  lambda X: f'Hold {X} in mind as you write. ' + COPY_NOW,
    ("bare", "directed", "mention"):   lambda X: f'{X} came up in conversation. ' + COPY_NOW,
}

# §2.4 categories
CATEGORY_TAILS = {"maintain": '. Keep that category in mind while you ' + COPY,
                  "mention": '. That category occurs one time. ' + COPY_NOW}
LIST_TAILS = {"maintain": '. Keep those items in mind while you ' + COPY,
              "mention": '. That list occurs one time. ' + COPY_NOW}
# §2.5 tagged selection / sums
TAGGED_TAILS = {"maintain": '. Keep the word tagged {T} in mind while you ' + COPY,
                "mention": '. Those words occur one time. ' + COPY_NOW}
SUM_TAILS = {"maintain": '. Keep their sum in mind while you ' + COPY,
             "mention": '. That pair occurs one time. ' + COPY_NOW}
# §2.6 ordinal source list
ORDINAL_TAILS = {"maintain": '. Keep the {ORD} word in mind while you ' + COPY,
                 "mention": '. Each word occurs one time. ' + COPY_NOW}


def user_text_controlled(condition, X, carrier):
    """§2.1 user turn for the controlled organism."""
    if condition in CONTROLLED_TAILS:
        return CONTROLLED_INTRO + f'"{X}"' + CONTROLLED_TAILS[condition] + ":\n\n" + carrier
    if condition == "plain_mention":
        return X + PLAIN_MENTION_TAIL + ":\n\n" + carrier
    if condition == "absent":
        return ABSENT_HEAD + ":\n\n" + carrier
    if condition == "pulse_base":
        return PULSE_BASE_HEAD + ":\n\n" + carrier
    raise ValueError(condition)


def user_text_direct(phrasing_text, X, carrier=None, copy_adapted=False):
    """§2.2 direct organism: the user message is the phrasing alone; copy-adapted appends the copy bridge."""
    u = phrasing_text.replace("{X}", X)
    if copy_adapted:
        assert carrier is not None
        u = u + " " + COPY_NOW + ":\n\n" + carrier
    return u


class Rendered:
    """One rendered forward: ids, spans, and the strings each span decodes to."""
    def __init__(self, ids, spans, strings, meta):
        self.ids, self.spans, self.strings, self.meta = ids, spans, strings, meta

    def __len__(self):
        return len(self.ids)

    @property
    def interior(self):
        cs, ce = self.spans["assistant_carrier"]
        return list(range(cs, ce))[2:-2]


def render_conversation(tok, user_text, assistant_text, extra_turns=None):
    """Chat-template the user turn, append the teacher-forced assistant text, optionally more turns.

    extra_turns: list of (user_text, assistant_prefix) appended after the first assistant turn; the
    final assistant prefix is left open (the answer position is the last token).
    Returns (full_string, ids, offsets, user_start_char, carrier_start_tok).
    """
    rendered = tok.apply_chat_template([{"role": "user", "content": user_text}], tokenize=False,
                                       add_generation_prompt=True, enable_thinking=False)
    full = rendered + assistant_text
    if extra_turns:
        probe = tok.apply_chat_template([{"role": "user", "content": "a"}], tokenize=False,
                                        add_generation_prompt=True, enable_thinking=False)
        gen_suffix = probe[probe.rindex("<|im_start|>assistant\n") + len("<|im_start|>assistant\n"):]
        for q, apre in extra_turns:
            full = full + "<|im_end|>\n<|im_start|>user\n" + q + "<|im_end|>\n<|im_start|>assistant\n" + gen_suffix + apre
    enc = tok(full, add_special_tokens=False, return_offsets_mapping=True)
    ids, offs = enc.input_ids, enc.offset_mapping
    pre = tok(rendered, add_special_tokens=False).input_ids
    k = 0
    while k < len(pre) and pre[k] == ids[k]:
        k += 1
    return full, ids, offs, rendered, k


def _tok_at(offs, c):
    for i, (a, b) in enumerate(offs):
        if a <= c < b:
            return i
    raise ValueError(f"character offset {c} not covered by any token")


def _span_of_substring(offs, full, sub, start):
    c0 = full.index(sub, start)
    return _tok_at(offs, c0), _tok_at(offs, c0 + len(sub) - 1), c0


def render(tok, user_text, carrier, sources=(), assistant_text=None, extra_turns=None, name="", carrier_in_user=True):
    """Render a copy-organism conversation and resolve spans with mechanical gates.

    sources: list of (label, exact_string, quoted:bool) to locate in the user text, in order.
    Gates: each located span decodes to the intended string (after stripping the surrounding quote
    tokens for quoted sources), the assistant carrier decodes to the carrier, and the user carrier
    occurrence is recorded.
    """
    assistant_text = carrier if assistant_text is None else assistant_text
    full, ids, offs, rendered, cs = render_conversation(tok, user_text, assistant_text, extra_turns)
    ubase = full.index(user_text)
    spans, strings = {}, {}
    pos = ubase
    for (label, s, quoted) in sources:
        needle = f'"{s}"' if quoted else s
        c0 = full.index(needle, pos)
        t_open = _tok_at(offs, c0) if quoted else None
        t_first = _tok_at(offs, c0 + (1 if quoted else 0))
        t_last = _tok_at(offs, c0 + len(needle) - (2 if quoted else 1))
        t_close = _tok_at(offs, c0 + len(needle) - 1) if quoted else t_last
        spans[label] = {"open": t_open, "first": t_first, "last": t_last, "close": t_close,
                        "content": list(range(t_first, t_last + 1)),
                        "full": list(range(t_open if quoted else t_first, t_close + 1))}
        strings[label] = tok.decode(ids[t_first:t_last + 1])
        pos = c0 + len(needle)
    # user carrier occurrence (the copy organism has two carrier occurrences; the direct organism has one)
    if carrier_in_user:
        uc0 = full.index(carrier, ubase)
        assert uc0 < ubase + len(user_text), "carrier not found inside the user turn"
        spans["user_carrier"] = (_tok_at(offs, uc0), _tok_at(offs, uc0 + len(carrier) - 1) + 1)
    else:
        assert carrier not in user_text, "carrier unexpectedly present in the user turn"
        spans["user_carrier"] = None
    # assistant carrier: from the LCP boundary; must end exactly where the assistant text ends
    a_end_char = len(rendered) + len(assistant_text)
    ce = _tok_at(offs, a_end_char - 1) + 1
    spans["assistant_carrier"] = (cs, ce)
    strings["assistant_carrier"] = tok.decode(ids[cs:ce])
    strings["user_carrier"] = tok.decode(ids[spans["user_carrier"][0]:spans["user_carrier"][1]]) if carrier_in_user else None
    if extra_turns:
        spans["answer"] = len(ids) - 1
        qc0 = full.index(extra_turns[-1][0], a_end_char)
        spans["query"] = (_tok_at(offs, qc0), len(ids) - 1)
        strings["query"] = tok.decode(ids[spans["query"][0]:spans["query"][1]])
    gates = {}
    for (label, s, quoted) in sources:
        gates[f"span_{label}"] = strings[label].strip() == s
    gates["assistant_carrier"] = strings["assistant_carrier"] == assistant_text
    gates["user_carrier"] = (strings["user_carrier"].strip() == carrier.strip()) if carrier_in_user else True
    gates["no_padding"] = tok.pad_token_id is None or tok.pad_token_id not in ids
    r = Rendered(ids, spans, strings, {"name": name, "full": full, "gates": gates, "user_text": user_text,
                                        "carrier_start": cs, "carrier_end": ce, "n_tokens": len(ids)})
    if not all(gates.values()):
        raise AssertionError(f"rendering gate failed for {name}: {gates} strings={strings}")
    return r


def single_token_id(tok, word, leading_space=True):
    """Return the token id if `word` (with a leading space by default) is a single token, else None."""
    ids = tok((" " if leading_space else "") + word, add_special_tokens=False).input_ids
    return ids[0] if len(ids) == 1 else None


def word_in_text(word, text):
    return re.search(rf"\b{re.escape(word)}s?\b", text, re.I) is not None
