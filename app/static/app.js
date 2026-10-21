let mode = 'rag';
const chat = document.getElementById('chat');
const sources = document.getElementById('sources');
const question = document.getElementById('q');

function msg(who, text) {
  const article = document.createElement('article');
  const label = document.createElement('b');
  const body = document.createElement('p');
  article.className = who === 'YOU' ? 'user' : 'ai';
  label.textContent = who;
  body.textContent = text;
  article.append(label, body);
  chat.append(article);
  chat.scrollTop = chat.scrollHeight;
}

function sourceLink(source, label) {
  const link = document.createElement('a');
  link.href = source.url;
  link.target = '_blank';
  link.rel = 'noopener';
  link.textContent = label;
  return link;
}

function showSources(items) {
  sources.replaceChildren();
  items.forEach((source, i) => {
    const details = document.createElement('details');
    details.className = 'source';
    const summary = document.createElement('summary');
    summary.textContent = `[${i + 1}] ${source.section} · ${source.score.toFixed(3)}`;
    const excerpt = document.createElement('p');
    excerpt.textContent = source.text;
    details.append(summary, sourceLink(source, `${source.source}:${source.line_start}`), excerpt);
    sources.append(details);
  });
  if (!items.length) sources.textContent = mode === 'base' ? 'No documents in base mode' : 'No matching documents';
}

document.querySelectorAll('[data-mode]').forEach(button => {
  button.onclick = () => {
    mode = button.dataset.mode;
    document.querySelectorAll('[data-mode]').forEach(x => x.classList.toggle('active', x === button));
    sources.textContent = mode === 'base' ? 'No documents in base mode' : 'Awaiting query';
  };
});
document.querySelectorAll('.sample').forEach(button => {
  button.onclick = () => { question.value = button.textContent; question.focus(); };
});

document.getElementById('form').onsubmit = async event => {
  event.preventDefault();
  const text = question.value.trim();
  if (!text) return;
  const requestMode = mode;
  const controls = [...document.querySelectorAll('button,input')];
  const previous = controls.map(x => x.disabled);
  controls.forEach(x => { x.disabled = true; });
  msg('YOU', text);
  question.value = '';
  sources.textContent = 'Retrieving / generating…';
  chat.setAttribute('aria-busy', 'true');
  try {
    const response = await fetch('/api/ask', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: text, mode: requestMode })
    });
    const data = await response.json();
    if (!response.ok) throw Error(typeof data.detail === 'string' ? data.detail : 'Invalid request');
    msg('ODYSSEY-7 AI', data.answer);
    showSources(data.sources);
  } catch (error) {
    sources.textContent = 'Request failed';
    msg('SYSTEM ERROR', error.message);
  } finally {
    controls.forEach((x, i) => { x.disabled = x.id === 'finetuned-mode' ? x.dataset.available !== 'true' : previous[i]; });
    chat.setAttribute('aria-busy', 'false');
    question.focus();
  }
};

fetch('/api/docs').then(r => {
  if (!r.ok) throw Error('Manual catalog unavailable');
  return r.json();
}).then(items => {
  for (const item of items) {
    const row = document.createElement('div');
    row.className = 'doc';
    row.append(sourceLink(item, `▣ ${item.section}`));
    document.getElementById('docs').append(row);
  }
}).catch(error => { document.getElementById('docs').textContent = error.message; });
fetch('/api/config').then(r => r.json()).then(config => {
  document.getElementById('retrieval-status').textContent = `● ${config.retriever.toUpperCase()} / ${config.chat_backend.toUpperCase()} / ${config.chat_model}`;
  const fineTuned = document.getElementById('finetuned-mode');
  fineTuned.dataset.available = String(config.fine_tuned_available);
  fineTuned.disabled = chat.getAttribute('aria-busy') === 'true' || !config.fine_tuned_available;
  fineTuned.textContent = config.fine_tuned_available ? 'FINE-TUNED + RAG' : 'FINE-TUNED + RAG · UNAVAILABLE';
}).catch(() => { document.getElementById('retrieval-status').textContent = '● RETRIEVAL STATUS UNKNOWN'; });
