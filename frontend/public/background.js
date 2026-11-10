// PITC service worker: relays requests from the content script to the local backend.
// View its logs: chrome://extensions -> PITC -> "service worker" link -> Console.
const BACKEND = 'http://localhost:8000';
const ALLOWED_PATHS = ['/crt/questions', '/crt/translate'];
const TIMEOUT_MS = 60000; // backend may try several models before answering

const log = (...a) => console.log('[PITC bg]', ...a);

chrome.runtime.onInstalled.addListener((d) => log('installed/updated:', d.reason));

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (!msg || msg.type !== 'PITC_API') return;

  if (!ALLOWED_PATHS.includes(msg.path)) {
    log('rejected path', msg.path);
    sendResponse({ ok: false, error: 'Unsupported request.' });
    return;
  }

  const started = Date.now();
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  log('->', msg.path, 'chars=' + ((msg.payload && msg.payload.text) || '').length);

  fetch(BACKEND + msg.path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(msg.payload),
    signal: ctrl.signal,
  })
    .then(async (res) => {
      const body = await res.json().catch(() => ({}));
      const ms = Date.now() - started;
      if (!res.ok) {
        const error = body.detail
          ? (typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail))
          : `Backend error ${res.status}`;
        log('<-', msg.path, res.status, ms + ' ms', error);
        sendResponse({ ok: false, error });
      } else {
        log('<-', msg.path, res.status, ms + ' ms');
        sendResponse({ ok: true, data: body });
      }
    })
    .catch((err) => {
      const ms = Date.now() - started;
      const timedOut = err && err.name === 'AbortError';
      log('<-', msg.path, timedOut ? 'TIMEOUT' : 'NETWORK ERROR', ms + ' ms', err && err.message);
      sendResponse({
        ok: false,
        error: timedOut
          ? 'The backend took too long to respond. Check backend/pitc.log.'
          : 'Cannot reach the PITC backend at localhost:8000. Is it running?',
      });
    })
    .finally(() => clearTimeout(timer));

  return true; // keep the channel open for the async response
});
