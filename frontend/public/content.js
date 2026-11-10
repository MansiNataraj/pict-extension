// PITC select-to-translate with CRT questions.
// Flow: select text -> choose target language -> PITC asks CRT context questions
// -> answers are applied to the translation -> result + register variants.
(() => {
  if (window.top !== window) return; // top frame only

  const DEBUG = true; // logs appear in the page's DevTools console, prefixed [PITC]
  const log = (...a) => { if (DEBUG) console.log('[PITC]', ...a); };
  const warn = (...a) => console.warn('[PITC]', ...a);

  const LANGS = { en: 'English', hi: 'Hindi', ta: 'Tamil', kn: 'Kannada', ar: 'Arabic' };
  const MAX_CHARS = 1500;

  function detectLang(text) {
    if (/[ऀ-ॿ]/.test(text)) return 'hi';
    if (/[஀-௿]/.test(text)) return 'ta';
    if (/[ಀ-೿]/.test(text)) return 'kn';
    if (/[؀-ۿ]/.test(text)) return 'ar';
    return 'en';
  }

  // ---------- backend calls (go through the service worker) ----------
  function callApi(path, payload) {
    return new Promise((resolve) => {
      const t0 = performance.now();
      log('request', path, payload);
      try {
        chrome.runtime.sendMessage({ type: 'PITC_API', path, payload }, (r) => {
          const ms = Math.round(performance.now() - t0);
          if (chrome.runtime.lastError || !r) {
            warn('no response from service worker', path, chrome.runtime.lastError && chrome.runtime.lastError.message);
            resolve({ ok: false, error: 'Extension was reloaded. Refresh this page and try again.' });
          } else {
            log('response', path, r.ok ? 'ok' : 'FAILED', ms + ' ms', r.ok ? r.data : r.error);
            resolve(r);
          }
        });
      } catch (err) {
        warn('sendMessage threw', err);
        resolve({ ok: false, error: 'Extension was reloaded. Refresh this page and try again.' });
      }
    });
  }

  // ---------- UI shell (closed shadow DOM so page CSS cannot interfere) ----------
  const host = document.createElement('div');
  host.style.cssText = 'all:initial;position:absolute;z-index:2147483647;top:0;left:0;';
  const root = host.attachShadow({ mode: 'closed' });
  root.innerHTML = `
    <style>
      *{box-sizing:border-box;font-family:system-ui,sans-serif}
      .box{position:absolute;background:#fff;color:#111;border:1px solid #d0d5dd;border-radius:10px;
        box-shadow:0 6px 24px rgba(0,0,0,.2);padding:10px 12px;font-size:13px;width:340px;display:none}
      button,select{font-size:12px;border-radius:6px;border:1px solid #c5cad3;padding:4px 8px;background:#f6f7f9;cursor:pointer}
      button.primary{background:#4f46e5;color:#fff;border-color:#4f46e5}
      .row{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
      .grow{flex:1}
      .src{color:#555;margin:6px 0;max-height:56px;overflow:auto;font-size:12px;border-left:3px solid #e4e7ec;padding-left:6px}
      .q{margin-top:8px}
      .qt{font-weight:600;font-size:12px}
      .tag{display:inline-block;background:#eef2ff;color:#4338ca;border-radius:4px;padding:0 5px;margin-right:4px;font-size:10px}
      label.opt{display:flex;gap:6px;align-items:center;margin:3px 0;font-size:12px;cursor:pointer}
      .out{margin-top:8px;font-size:15px;white-space:pre-wrap}
      .note{margin-top:4px;font-size:11px;color:#555}
      .err{color:#b42318;margin-top:6px;font-size:12px}
      .card{border:1px solid #e4e7ec;border-radius:8px;padding:6px 8px;margin-top:6px}
      .card .h{font-size:11px;font-weight:600;color:#4f46e5}
      .sp{height:8px}
    </style>
    <div class="box" id="box"></div>`;
  const box = root.getElementById('box');

  let current = '';       // selected text
  let anchorRect = null;  // where to place the box
  let runId = 0;          // invalidates stale async results
  const state = { target: 'hi', questions: [], answers: {} };

  const el = (tag, props = {}, ...kids) => {
    const n = document.createElement(tag);
    Object.assign(n, props);
    kids.forEach((k) => n.append(k));
    return n;
  };

  function setBox(...nodes) { box.replaceChildren(...nodes); place(); }
  function place() {
    if (!anchorRect) return;
    box.style.display = 'block';
    const left = Math.min(Math.max(8, anchorRect.left + window.scrollX), window.scrollX + document.documentElement.clientWidth - 356);
    box.style.left = left + 'px';
    box.style.top = anchorRect.bottom + window.scrollY + 8 + 'px';
  }
  function hide() { runId++; box.style.display = 'none'; }

  const closeBtn = () => el('button', { textContent: '✕', title: 'Close', onclick: hide });
  const srcBlock = () => el('div', { className: 'src', textContent: current });
  const errorBlock = (msg, retry) => {
    const wrap = el('div', {}, el('div', { className: 'err', textContent: msg }));
    if (retry) wrap.append(el('div', { className: 'sp' }), el('button', { textContent: 'Try again', onclick: retry }));
    return wrap;
  };

  // ---------- step 1: ask ----------
  function stepPrompt() {
    runId++;
    const src = detectLang(current);
    state.target = src === 'en' ? 'hi' : 'en';
    const sel = el('select');
    Object.entries(LANGS).forEach(([k, v]) => {
      if (k !== src) sel.append(el('option', { value: k, textContent: 'To ' + v, selected: k === state.target }));
    });
    sel.onchange = () => { state.target = sel.value; };
    state.target = sel.value;
    setBox(
      el('div', { className: 'row' },
        el('span', { className: 'grow', textContent: 'Translate this with PITC?' }), closeBtn()),
      el('div', { className: 'sp' }),
      el('div', { className: 'row' }, sel,
        el('button', { className: 'primary', textContent: 'Translate', onclick: stepQuestions }))
    );
  }

  // ---------- step 2: CRT questions ----------
  async function stepQuestions() {
    const my = ++runId;
    setBox(el('div', { className: 'row' }, el('span', { className: 'grow', textContent: 'Checking cultural context…' }), closeBtn()), srcBlock());
    const r = await callApi('/crt/questions', { text: current, source_language: 'auto', target_language: state.target });
    if (my !== runId) return log('discarded stale questions response');
    if (!r.ok) return setBox(el('div', { className: 'row' }, el('b', { className: 'grow', textContent: 'PITC' }), closeBtn()), srcBlock(), errorBlock(r.error, stepQuestions));

    state.questions = r.data.questions || [];
    state.answers = {};
    if (state.questions.length === 0) {
      log('no CRT questions needed; translating directly');
      return stepResult();
    }
    renderQuestions();
  }

  function renderQuestions() {
    const form = el('div');
    state.questions.forEach((q) => {
      const group = el('div', { className: 'q' },
        el('div', { className: 'qt' }, el('span', { className: 'tag', textContent: q.crt_code }), q.question));
      q.options.forEach((opt) => {
        const input = el('input', { type: 'radio', name: 'q_' + q.id, value: opt });
        input.onchange = () => { state.answers[q.id] = opt; log('answer', q.crt_code, opt); };
        group.append(el('label', { className: 'opt' }, input, opt));
      });
      form.append(group);
    });
    setBox(
      el('div', { className: 'row' }, el('b', { className: 'grow', textContent: 'A few quick questions' }), closeBtn()),
      srcBlock(), form, el('div', { className: 'sp' }),
      el('div', { className: 'row' },
        el('button', { className: 'primary', textContent: 'Translate', onclick: stepResult }),
        el('button', { textContent: 'Skip questions', onclick: () => { state.answers = {}; stepResult(); } }))
    );
  }

  // ---------- step 3: translate using the answers ----------
  async function stepResult() {
    const my = ++runId;
    setBox(el('div', { className: 'row' }, el('span', { className: 'grow', textContent: 'Translating…' }), closeBtn()), srcBlock());
    const answers = state.questions
      .filter((q) => state.answers[q.id])
      .map((q) => ({ id: q.id, crt_code: q.crt_code, question: q.question, answer: state.answers[q.id] }));
    const r = await callApi('/crt/translate', {
      text: current, source_language: 'auto', target_language: state.target, answers,
    });
    if (my !== runId) return log('discarded stale translate response');
    if (!r.ok) return setBox(el('div', { className: 'row' }, el('b', { className: 'grow', textContent: 'PITC' }), closeBtn()), srcBlock(), errorBlock(r.error, stepResult));

    const d = r.data;
    const kids = [
      el('div', { className: 'row' }, el('b', { className: 'grow', textContent: 'Translation' }), closeBtn()),
      el('div', { className: 'out', textContent: d.translated_text }),
      el('div', { className: 'sp' }),
      copyButton(d.translated_text),
    ];
    if (d.register_used) kids.push(el('div', { className: 'note', textContent: 'Register: ' + d.register_used }));
    (d.crt_applied || []).forEach((n) => kids.push(
      el('div', { className: 'note' }, el('span', { className: 'tag', textContent: n.code }), n.note)));
    if (d.cultural_notes) kids.push(el('div', { className: 'note', textContent: d.cultural_notes }));
    (d.variants || []).forEach((v) => kids.push(
      el('div', { className: 'card' },
        el('div', { className: 'h', textContent: v.label }),
        el('div', { textContent: v.text }),
        el('div', { className: 'note', textContent: v.nuance || '' }),
        copyButton(v.text))));
    kids.push(el('div', { className: 'sp' }), el('button', { textContent: 'Start over', onclick: stepPrompt }));
    setBox(...kids);
  }

  function copyButton(text) {
    const b = el('button', { textContent: 'Copy' });
    b.onclick = () => navigator.clipboard.writeText(text)
      .then(() => { b.textContent = 'Copied'; })
      .catch((e) => { warn('copy failed', e); b.textContent = 'Copy failed'; });
    return b;
  }

  // ---------- selection handling ----------
  function readSelection() {
    const ae = document.activeElement;
    // Text inside <input>/<textarea> is not exposed through the normal selection range.
    if (ae && (ae.tagName === 'TEXTAREA' || (ae.tagName === 'INPUT' && /^(text|search|url|email|)$/i.test(ae.type)))) {
      try {
        const t = ae.value.substring(ae.selectionStart, ae.selectionEnd).trim();
        if (t) return { text: t, rect: ae.getBoundingClientRect() };
      } catch (_) { /* some input types throw on selectionStart */ }
    }
    const sel = window.getSelection();
    const text = sel ? sel.toString().trim() : '';
    if (!text || sel.rangeCount === 0) return { text: '' };
    let rect = sel.getRangeAt(0).getBoundingClientRect();
    if (!rect.width && !rect.height && ae) rect = ae.getBoundingClientRect();
    return { text, rect };
  }

  document.addEventListener('mouseup', (e) => {
    if (e.composedPath().includes(host)) return;
    setTimeout(() => {
      const { text, rect } = readSelection();
      if (text.length < 2) return hide();
      if (text.length > MAX_CHARS) {
        log('selection too long, ignored:', text.length);
        return hide();
      }
      current = text;
      anchorRect = rect;
      log('selected', text.length, 'chars');
      stepPrompt();
    }, 10);
  });
  document.addEventListener('mousedown', (e) => { if (!e.composedPath().includes(host)) hide(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') hide(); });

  document.documentElement.appendChild(host);
  log('content script ready on', location.hostname);
})();
