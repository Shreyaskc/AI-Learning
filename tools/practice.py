"""Derive practice cards from existing lesson questions without a second content copy."""
import hashlib
import html
import json
import re

QUESTION = re.compile(r'^\d+\.\s+(.+?)\s+(?:Example solution|Solution|Answer):\s*(.+)$', re.IGNORECASE)


EXPLANATIONS = {'01-foundations': ['From rules to learned functions', 'The first contract: what information exists when?', 'The first contract: what information exists when?'], '02-math': ['Vectors are ordered measurements', 'Vectors are ordered measurements', 'Change, gradients and the chain rule', 'Vectors are ordered measurements'], '03-probability': ['Expectations and variation', 'Expectations and variation', 'Information and loss'], '04-optimization': ['An objective connects data to parameters', 'Generalization and regularization', 'Lab and reasoning'], '05-classical-ml': ['Linear and probabilistic models', 'Trees and ensembles', 'Practical extension: train and compare four families'], '06-evaluation': ['LLM systems need layered evaluation', 'Quantify what the sample can support', 'LLM systems need layered evaluation'], '07-neural-networks': ['Composition creates features', 'Architectural biases', 'Composition creates features'], '08-transformers': ['One attention head, with shapes', 'A block and the language-model head', 'A block and the language-model head', 'Representative implementation: IDs to a complete tiny block', 'One attention head, with shapes', 'A block and the language-model head', 'Costs and misconceptions'], '09-llm-training': ['Capabilities, reasoning and limits', 'Preferences and reinforcement learning', 'Pretraining learns a predictive distribution'], '10-retrieval-rag': ['A worked retrieval evaluation', 'Add generation with measured boundaries', 'Find evidence before writing an answer'], '11-agents-memory': ['Start with a deterministic workflow', 'Persist memory with provenance and deletion', 'Start with a deterministic workflow'], '12-multimodal': ['Representations across modalities', 'Vision-language and speech systems', 'Three generative families'], '13-data-platforms': ['Two clocks matter', 'Offline and online paths', 'Reusable embeddings and knowledge products'], '14-compute-serving': ['Prefill and decode', 'Training memory and parallelism', 'Practical extension: measure a bounded local service'], '15-operations': ['Release and rollback', 'Monitor symptoms and outcomes', 'Release and rollback'], '16-security-responsibility': ['Work through a cross-tenant attack', 'Fairness and human oversight', 'Fairness and human oversight'], '17-research-experiments': ['Read a paper in four passes', 'Ask a question that can lose', 'Read a paper in four passes'], '18-domain-electives': ['Forecasting respects the clock', 'Recommendations are a two-stage decision system', 'Anomaly and risk-like decisions']}
DIAGNOSTIC_LINKS = [('01-foundations', 'The first contract: what information exists when?'), ('02-math', 'Vectors are ordered measurements'), ('03-probability', 'Probability is a model of uncertainty'), ('02-math', 'Change, gradients and the chain rule'), ('01-foundations', 'A worked baseline'), ('08-transformers', 'One attention head, with shapes'), ('10-retrieval-rag', 'Add generation with measured boundaries'), ('11-agents-memory', 'Practical extension: crash a worker after a committed effect'), ('13-data-platforms', 'Two clocks matter'), ('14-compute-serving', 'Serving techniques and their limits')]

def questions(lessons):
    bank=[]
    for path in lessons:
        lines=path.read_text().splitlines();title=lines[0].removeprefix('# ')
        heading='';explanation_heading='';question_index=0
        for line in lines:
            if line.startswith('## '):
                heading=line[3:]
                if not any(word in heading.lower() for word in ('practice','exercise','diagnostic','interview')):
                    explanation_heading=heading
            match=QUESTION.match(line)
            if not match:continue
            prompt,solution=match.groups()
            identity=hashlib.sha256((path.stem+'\n'+prompt).encode()).hexdigest()[:12]
            sentences=re.split(r'(?<=[.!?])\s+(?=[A-Z])',solution,maxsplit=1)
            lesson_stem=path.stem
            if path.stem=='00-start':lesson_stem,explanation_heading=DIAGNOSTIC_LINKS[question_index]
            elif path.stem in EXPLANATIONS:explanation_heading=EXPLANATIONS[path.stem][question_index]
            question_index+=1
            slug=re.sub(r'[^a-z0-9]+','-',explanation_heading.lower()).strip('-')
            bank.append({'id':path.stem+'-'+identity,'topic':path.stem,'topicTitle':title,
                         'question':prompt,'answer':sentences[0],
                         'explanation':sentences[1] if len(sentences)>1 else '',
                         'solution':solution,'lesson':'course/'+lesson_stem+'.html'+('#'+slug if slug else ''),
                         'sourceHeading':heading})
    if len({q['id'] for q in bank})!=len(bank):raise ValueError('duplicate practice question IDs')
    return bank


def page(bank,inline):
    topics=list(dict.fromkeys((q['topic'],q['topicTitle']) for q in bank))
    options=''.join(f'<option value="{topic}">{html.escape(title)}</option>' for topic,title in topics)
    data=json.dumps(bank,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    fallback=''.join(f'<li><p>{inline(q["question"])}</p><details><summary>Show answer and reasoning</summary><p>{inline(q["solution"])}</p><a href="{q["lesson"]}">Read the lesson explanation</a></details></li>' for q in bank)
    return f'''<section id="practice-app" aria-labelledby="practice-title">
<div class="eyebrow">RECALL → COMPARE → REVIEW</div><h1 id="practice-title">Practice Q&amp;A</h1>
<p class="practice-intro">One question at a time. Think it through or jot down an attempt, then compare with the answer. Your self-check is for review, not a grade.</p>
<div id="practice-interactive" hidden>
<div id="practice-filters" class="practice-filters"><div><label for="practice-topic">Topic</label><select id="practice-topic"><option value="all">All topics</option>{options}</select></div><div><label for="practice-search">Find a question</label><input id="practice-search" type="search" placeholder="Try leakage, gradients or memory" autocomplete="off"></div><button id="practice-clear" type="button" class="quiet">Clear filters</button></div>
<p id="practice-results" class="small" role="status" aria-live="polite"></p>
<div class="practice-status"><p id="practice-count" role="status" aria-live="polite"></p><button id="practice-reset" type="button" class="quiet">Reset self-checks</button></div>
<div id="practice-reset-confirm" class="reset-confirm" hidden><p>Reset all Q&amp;A self-checks and your resume position? Lesson study checkboxes are kept.</p><button id="practice-reset-yes" type="button">Reset Q&amp;A progress</button><button id="practice-reset-no" type="button" class="quiet">Cancel</button></div>
<p id="practice-storage" class="storage-note" role="status" hidden></p>
<div id="practice-empty" class="practice-empty" hidden><h2>No matching questions</h2><p>Try a different search or clear the filters.</p><button id="practice-empty-clear" type="button">Show all questions</button></div>
<article id="practice-card" class="practice-card" hidden aria-labelledby="practice-question">
<div class="practice-card-meta"><span id="practice-topic-name"></span><span id="practice-position"></span></div>
<h2 id="practice-question" tabindex="-1"></h2>
<a id="practice-read-before" class="practice-return" href="course/00-start.html">Read this lesson first →</a>
<label for="practice-attempt">Your attempt <span>(optional — thinking aloud works too)</span></label><textarea id="practice-attempt" rows="4" placeholder="Explain the idea in your own words…" aria-describedby="practice-notes-help"></textarea>
<p id="practice-notes-help" class="small">Notes stay in this page session. They are not saved or automatically graded.</p>
<button id="practice-reveal" type="button" class="primary" aria-expanded="false" aria-controls="practice-answer">Show answer</button>
<section id="practice-answer" class="practice-answer" hidden aria-labelledby="practice-answer-title"><h3 id="practice-answer-title" tabindex="-1">Answer to compare</h3><div id="practice-answer-text"></div><h3>Why / reasoning</h3><div id="practice-explanation"></div><a id="practice-lesson" href="course/00-start.html">Read the lesson explanation →</a>
<fieldset class="practice-self-check"><legend>How did your reasoning compare?</legend><button id="practice-got-it" type="button" aria-pressed="false">Got it</button><button id="practice-partly" type="button" aria-pressed="false">Partly</button><button id="practice-need-practice" type="button" aria-pressed="false">Need practice</button><p id="practice-rating" role="status"></p></fieldset></section>
<nav class="practice-nav" aria-label="Question navigation"><button id="practice-previous" type="button">← Previous</button><span id="practice-nav-status"></span><button id="practice-next" type="button">Next question →</button></nav><p id="practice-end" class="small" hidden>Last question in these results. Change topic or filters to keep practicing.</p>
</article></div><noscript><p>JavaScript is off. You can still practice below; open each answer after attempting the question.</p><ol>{fallback}</ol></noscript>
<script type="application/json" id="practice-data">{data}</script><script src="practice.js" defer></script></section>'''
