# Definition dialogs — review evidence

Coverage: all seven currently bold technical terms in lesson 01: feature, target,
example, parameters, Training, Inference and hyperparameter. Labels such as Basic,
Senior and learning-path names remain emphasis. Ordinary unbolded words are not
linked automatically.

The glossary is the canonical source for each meaning, short example and explicit
alias. Three combined rows were split into distinct concepts; Example was added.
For example, a feature is an available input measurement (package weight), whereas
a target is the predicted outcome (delivery duration). Training fits parameters;
inference applies a fitted model. Example is linked only in the foundations context
to avoid interpreting ordinary prose as dataset vocabulary.

Links keep their glossary destinations without JavaScript or native dialog support.
With support, Enter/click/tap opens a native modal dialog. Native modal behavior
provides keyboard focus containment and Escape cancellation. Close and backdrop
click dismiss it and restore focus without scrolling; modified clicks remain normal
links. Browser history changes close the dialog without adding history entries or
writing progress, ratings or notes. Definitions use textContent and do not contain
exercise solutions. Code spans and existing Markdown links are protected.

Validation: generated HTML and local anchors; Python registry/parser coverage;
DOM-double dialog lifecycle, focus and dismissal tests; all existing practice and
reader tests; offline labs. CSS bounds the centered dialog to the viewport with
scrolling and a 48px close control. These structural assertions are not rendered
viewport-edge testing. No browser surface is connected; real touch, keyboard,
mobile layout, native focus trapping and screen-reader QA remain manual review
items. No screenshots or visual pass are claimed. Draft PR only: no merge or Pages
deployment is authorized for this change.

Run:

```
python3 tools/check.py
python3 -m unittest discover -s tools -p 'test_*.py'
node tools/test_terms.js
node tools/test_practice.js
node tools/test_reader.js
```
