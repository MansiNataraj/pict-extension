// PITC select-to-translate: shows a small prompt when text is selected on a page.
(() => {
  if (window.top !== window) return; // top frame only
  const LANGS = { en: 'English', hi: 'Hindi', ta: 'Tamil', kn: 'Kannada', ar: 'Arabic' };

  function detectLang(text) {
    if (/[ऀ-ॿ]/.test(text)) return 'hi';
    if (/[஀-௿]/.test(text)) return 'ta';
    if (/[ಀ-೿]/.test(text)) return 'kn';
    if (/[؀-ۿ]/.test(text)) return 'ar';
    return 'en';
  }

  const host = document.createElement('div');
  host.style.cssText = 'all:initial;position:absolute;z-index:2147483647;top:0;left:0;';
  const root = host.attachShadow({ mode: 'closed' });
  root.innerHTML = `
    <style>
      *{box-sizing:border-box;font-family:system-ui,sans-serif}
      .box{position:absolute;background:#fff;color:#111;border:1px solid #d0d5dd;border-radius:10px;
        box-shadow:0 6px 24px rgba(0,0,0,.2);padding:8px 10px;font-size:13px;max-width:320px;display:none}
      button,select{font-size:12px;border-radius:6px;border:1px solid #c5cad3;padding:4px 8px;background:#f6f7f9;cursor:pointer}
      button.primary{background:#4f46e5;color:#fff;border-color:#4f46e5}
      .row{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
      .src{color:#555;margin:6px 0;max-height:60px;overflow:auto;font-size:12px}
      .out{margin-top:8px;font-size:14px;white-space:pre-wrap}
      .note{margin-top:4px;font-size:11px;color:#666}
      .err{color:#b42318;margin-top:6px;font-size:12px}
    </style>
    <div class="box" id="box"></div>`;
  const box = root.getElementById('box');
  let current = '';

  function place(rect) {
    box.style.display = 'block';
    box.style.left = Math.max(8, rect.left + window.scrollX) + 'px';
    box.style.top = rect.bottom + window.scrollY + 8 + 'px';
  }
  function hide() { box.style.display = 'none'; }

  function showPrompt(rect) {
    box.innerHTML = `<div class="row"><span>Translate this with PITC?</span>
      <button class="primary" id="yes">Translate</button><button id="no">✕</button></div>`;
    place(rect);
    root.getElementById('yes').onclick = () => showTranslate(rect);
    root.getElementById('no').onclick = hide;
  }

  function showTranslate(rect) {
    const src = detectLang(current);
    const defTgt = src === 'en' ? 'hi' : 'en';
    const opts = (sel) => Object.entries(LANGS)
      .map(([k, v]) => `<option value="${k}" ${k === sel ? 'selected' : ''}>${v}</option>`).join('');
    box.innerHTML = `
      <div class="row"><select id="s">${opts(src)}</select>→<select id="t">${opts(defTgt)}</select>
        <select id="tone"><option value="polite">Polite</option><option value="traditional">Traditional</option><option value="casual">Casual</option></select>
        <button class="primary" id="go">Go</button><button id="x">✕</button></div>
      <div class="src"></div><div id="res"></div>`;
    box.querySelector('.src').textContent = current;
    place(rect);
    root.getElementById('x').onclick = hide;
    const run = () => {
      const res = root.getElementById('res');
      res.innerHTML = '<div class="note">Translating…</div>';
      chrome.runtime.sendMessage({
        type: 'PITC_TRANSLATE',
        payload: {
          audio_text: current,
          source_language: root.getElementById('s').value,
          target_language: root.getElementById('t').value,
          tone: root.getElementById('tone').value,
        },
      }, (r) => {
        if (chrome.runtime.lastError || !r) {
          res.innerHTML = '<div class="err">Extension error. Reload the page and try again.</div>';
        } else if (!r.ok) {
          res.innerHTML = '';
          const e = document.createElement('div'); e.className = 'err'; e.textContent = r.error; res.appendChild(e);
        } else {
          res.innerHTML = '<div class="out"></div><div class="note"></div>';
          res.querySelector('.out').textContent = r.data.translated_text;
          res.querySelector('.note').textContent = r.data.cultural_notes || '';
        }
      });
    };
    root.getElementById('go').onclick = run;
    run();
  }

  document.addEventListener('mouseup', (e) => {
    if (e.composedPath().includes(host)) return;
    setTimeout(() => {
      const sel = window.getSelection();
      const text = sel ? sel.toString().trim() : '';
      if (text.length < 2 || text.length > 1500) { hide(); return; }
      current = text;
      showPrompt(sel.getRangeAt(0).getBoundingClientRect());
    }, 10);
  });
  document.addEventListener('mousedown', (e) => {
    if (!e.composedPath().includes(host)) hide();
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') hide(); });

  document.documentElement.appendChild(host);
})();
