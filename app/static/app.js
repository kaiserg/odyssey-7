let mode = 'rag';
let busy = false;
let adapterAvailable = false;
let responseNumber = 0;
const chat = document.getElementById('chat');
const sources = document.getElementById('sources');
const question = document.getElementById('q');
const modeDescriptions = {
  base: 'No manual excerpts. Watch for uncertainty, invented facts, and unsupported answers.',
  rag: 'Retrieve manual excerpts, then answer with source labels.',
  finetuned: 'Same retrieved excerpts, plus the validated formatting adapter. Better format does not guarantee better facts.'
};
const modeNames = { base: 'BASE', rag: 'RAG', finetuned: 'FINE-TUNED + RAG' };

function updateControls() {
  document.querySelectorAll('button,input').forEach(control => {
    control.disabled = busy || (control.id === 'finetuned-mode' && !adapterAvailable);
  });
  document.getElementById('finetuned-mode').title = adapterAvailable
    ? 'Validated local adapter on the same MLX base model'
    : 'Requires the MLX backend and a validated local adapter. See docs/FINETUNING.md.';
  chat.setAttribute('aria-busy', String(busy));
  document.getElementById('request-status').textContent = busy ? 'TRANSMITTING…' : 'READY';
  document.getElementById('transmit').firstChild.textContent = busy ? 'Working ' : 'Transmit ';
}

function resetEvidence(text) {
  sources.replaceChildren();
  const empty = document.createElement('div');
  empty.className = 'empty-state';
  const paragraph = document.createElement('p');
  paragraph.textContent = text;
  empty.append(paragraph);
  sources.append(empty);
  document.getElementById('source-count').textContent = '0';
  document.getElementById('evidence-question').textContent = 'Sources for the next response.';
  document.querySelectorAll('.message-evidence').forEach(button => button.setAttribute('aria-pressed', 'false'));
}

function sourceLink(source, label) {
  const link = document.createElement('a');
  link.href = source.url;
  link.target = '_blank';
  link.rel = 'noopener';
  link.textContent = label;
  return link;
}

function showSources(items, text, responseMode) {
  sources.replaceChildren();
  document.getElementById('source-count').textContent = String(items.length);
  document.getElementById('evidence-question').textContent = `${modeNames[responseMode]} / ${text}`;
  items.forEach((source, i) => {
    const details = document.createElement('details');
    details.className = 'source';
    const summary = document.createElement('summary');
    summary.textContent = `[${i + 1}] ${source.section}`;
    const excerpt = document.createElement('p');
    excerpt.textContent = source.text;
    const score = document.createElement('div');
    score.className = 'source-score';
    score.textContent = `Similarity ${source.score.toFixed(3)} · not a confidence score`;
    details.append(summary, score, sourceLink(source, `${source.source}:${source.line_start} ↗`), excerpt);
    sources.append(details);
  });
  if (!items.length) {
    const empty = document.createElement('div');
    empty.className = 'empty-state';
    empty.textContent = responseMode === 'base' ? 'Base mode uses no documents.' : 'No excerpts passed the retrieval threshold.';
    sources.append(empty);
  }
}

function msg(who, text, response = null) {
  const article = document.createElement('article');
  article.className = `message ${who === 'YOU' ? 'user' : who === 'SYSTEM ERROR' ? 'error' : 'ai'}`;
  const heading = document.createElement('div');
  heading.className = 'message-heading';
  const avatar = document.createElement('span');
  avatar.className = 'avatar';
  avatar.setAttribute('aria-hidden', 'true');
  avatar.textContent = who === 'YOU' ? '↗' : who === 'SYSTEM ERROR' ? '!' : 'O7';
  const label = document.createElement('b');
  label.textContent = who;
  heading.append(avatar, label);
  if (response) {
    const tag = document.createElement('span');
    tag.className = 'message-tag';
    tag.textContent = modeNames[response.mode];
    heading.append(tag);
  }
  const body = document.createElement('div');
  body.className = 'message-body';
  const paragraph = document.createElement('p');
  paragraph.textContent = text;
  body.append(paragraph);
  article.append(heading, body);
  if (response) {
    const id = ++responseNumber;
    const evidence = document.createElement('button');
    evidence.type = 'button';
    evidence.className = 'message-evidence';
    evidence.textContent = response.sources.length ? `INSPECT ${response.sources.length} SOURCE${response.sources.length === 1 ? '' : 'S'} ↗` : 'INSPECT EVIDENCE ↗';
    evidence.setAttribute('aria-label', `Inspect evidence for response ${id}`);
    evidence.setAttribute('aria-controls', 'sources');
    evidence.setAttribute('aria-pressed', 'true');
    evidence.onclick = () => {
      document.querySelectorAll('.message-evidence').forEach(button => button.setAttribute('aria-pressed', String(button === evidence)));
      showSources(response.sources, response.question, response.mode);
      sources.tabIndex = -1;
      sources.focus();
      sources.scrollIntoView({ block: 'nearest' });
    };
    document.querySelectorAll('.message-evidence').forEach(button => button.setAttribute('aria-pressed', 'false'));
    article.append(evidence);
  }
  chat.append(article);
  chat.scrollTop = chat.scrollHeight;
}

document.querySelectorAll('[data-mode]').forEach(button => {
  button.onclick = () => {
    mode = button.dataset.mode;
    document.querySelectorAll('[data-mode]').forEach(control => {
      control.classList.toggle('active', control === button);
      control.setAttribute('aria-pressed', String(control === button));
    });
    document.getElementById('mode-description').textContent = modeDescriptions[mode];
    resetEvidence(mode === 'base' ? 'Base mode uses no documents.' : 'Awaiting your next transmission.');
  };
});
document.querySelectorAll('.sample').forEach(button => {
  button.onclick = () => { question.value = button.dataset.question; question.focus(); };
});

document.getElementById('form').onsubmit = async event => {
  event.preventDefault();
  if (busy) return;
  const text = question.value.trim();
  if (!text) return;
  const requestMode = mode;
  busy = true;
  updateControls();
  msg('YOU', text);
  question.value = '';
  resetEvidence(requestMode === 'base' ? 'Generating without manual excerpts…' : 'Retrieving excerpts and generating…');
  try {
    const response = await fetch('/api/ask', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: text, mode: requestMode })
    });
    const data = await response.json();
    if (!response.ok) throw Error(typeof data.detail === 'string' ? data.detail : 'Invalid request');
    msg('ODYSSEY-7 AI', data.answer, { sources: data.sources, question: text, mode: requestMode });
    showSources(data.sources, text, requestMode);
  } catch (error) {
    resetEvidence('Request failed. No evidence is attached to this response.');
    msg('SYSTEM ERROR', error.message);
  } finally {
    busy = false;
    updateControls();
    question.focus();
  }
};

fetch('/api/docs').then(response => {
  if (!response.ok) throw Error('Manual catalog unavailable');
  return response.json();
}).then(items => {
  const catalog = document.getElementById('docs');
  catalog.replaceChildren();
  const groups = new Map();
  for (const item of items) {
    if (!groups.has(item.source)) groups.set(item.source, []);
    groups.get(item.source).push(item);
  }
  for (const [source, sections] of groups) {
    const group = document.createElement('div');
    group.className = 'manual-group';
    const heading = document.createElement('h3');
    heading.textContent = source.replace(/\.md$/, '').replaceAll('-', ' ');
    group.append(heading);
    for (const item of sections) {
      const row = document.createElement('div');
      row.className = 'doc';
      const match = item.section.match(/^(.*?)\s([A-Z]+-\d+)$/);
      const code = document.createElement('span');
      code.className = 'doc-code';
      code.textContent = match ? match[2] : '§';
      row.append(code, sourceLink(item, match ? match[1] : item.section));
      group.append(row);
    }
    catalog.append(group);
  }
  document.getElementById('doc-count').textContent = String(items.length).padStart(2, '0');
  document.getElementById('archive-status').textContent = `${groups.size} manuals / ${items.length} sections`;
  document.getElementById('archive-summary').textContent = `${groups.size} MANUALS / LOCAL MARKDOWN`;
}).catch(error => {
  document.getElementById('docs').textContent = error.message;
  document.getElementById('archive-status').textContent = 'Unavailable';
});
fetch('/api/config').then(response => {
  if (!response.ok) throw Error('Configuration unavailable');
  return response.json();
}).then(config => {
  document.getElementById('retrieval-status').textContent = config.retriever === 'vector' ? 'VECTORS / FAISS' : config.retriever.toUpperCase();
  document.getElementById('backend-status').textContent = config.chat_backend.toUpperCase();
  document.getElementById('model-status').textContent = config.chat_model;
  document.getElementById('adapter-status').textContent = config.fine_tuned_available ? 'VALIDATED' : 'NOT CONFIGURED';
  adapterAvailable = config.fine_tuned_available;
  updateControls();
}).catch(() => {
  for (const id of ['retrieval-status', 'backend-status', 'model-status', 'adapter-status']) document.getElementById(id).textContent = 'Unavailable';
});
