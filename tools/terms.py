"""Load four-layer definitions from the canonical authored glossary table."""
import json
import re
from pathlib import Path

FIELDS = ('definition', 'plain', 'analogy', 'example')


def normalize(text):
    return ' '.join(text.casefold().split()).strip('.,:;!? ')


def key_for(name):
    return re.sub(r'[^a-z0-9]+', '-', normalize(name)).strip('-')


def load(path):
    entries, aliases = {}, {}
    for line in Path(path).read_text().splitlines():
        if not line.startswith('|'): continue
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if cells[0] == 'Term' or re.fullmatch(r'[-:]+', cells[0]): continue
        if len(cells) != 8: raise ValueError('Expected eight glossary columns: '+cells[0])
        name, definition, plain, analogy, example, lesson, alternate, sources = cells
        if not all([definition, plain, analogy, example, lesson, sources]): raise ValueError('Incomplete layers: '+name)
        if 'Limit:' not in analogy: raise ValueError('Missing analogy limit: '+name)
        key = key_for(name)
        if key in entries: raise ValueError('Duplicate term: '+name)
        entries[key] = dict(name=name, definition=definition, plain=plain, analogy=analogy, example=example)
        # Slash groups distinguish concepts; their constituents are not interchangeable aliases.
        for alias in [name] + alternate.split(';'):
            if not alias.strip(): continue
            normalized = normalize(alias)
            if normalized in aliases: raise ValueError('Duplicate term alias: '+alias)
            aliases[normalized] = key
    return entries, aliases


ENTRIES, ALIASES = load(Path(__file__).resolve().parents[1] / 'course/glossary.md')


def resolve(text, context=None):
    key = ALIASES.get(normalize(text))
    if key == 'example' and context != '01-foundations': return None
    return key


def data(keys=None):
    selected = ENTRIES if keys is None else {key: ENTRIES[key] for key in sorted(set(keys)) if key in ENTRIES}
    return json.dumps(selected, ensure_ascii=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
