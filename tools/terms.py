"""Definitions are authored once in the glossary; only complete entries are interactive."""
import json
import re
from pathlib import Path


def normalize(text):
    return ' '.join(text.casefold().split()).strip('.,:;!? ')


def load(path):
    entries, aliases = {}, {}
    for line in Path(path).read_text().splitlines():
        if not line.startswith('|'): continue
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if len(cells) != 5 or not cells[3] or cells[0] == 'Term' or '/' in cells[0] or re.fullmatch(r'[-:]+', cells[0]): continue
        name, definition, _, example, alternate = cells
        key = re.sub(r'[^a-z0-9]+', '-', normalize(name)).strip('-')
        entries[key] = dict(name=name, definition=definition, example=example)
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


def data():
    return json.dumps(ENTRIES, ensure_ascii=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
