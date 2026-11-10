// Select-to-translate: the content script asks us to call the local backend.
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg && msg.type === 'PITC_TRANSLATE') {
    fetch('http://localhost:8000/speech-translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(msg.payload),
    })
      .then(async (res) => {
        const body = await res.json().catch(() => ({}));
        if (!res.ok) sendResponse({ ok: false, error: body.detail || `Backend error ${res.status}` });
        else sendResponse({ ok: true, data: body });
      })
      .catch(() => sendResponse({ ok: false, error: 'Cannot reach the PITC backend at localhost:8000. Is it running?' }));
    return true; // async response
  }
});
