import React, { useState, useEffect, useRef } from 'react';
import Icon from './Icon';

const API_BASE = 'http://localhost:8000';

const BCP_MAP = { en: 'en-US', hi: 'hi-IN', ta: 'ta-IN', kn: 'kn-IN', ar: 'ar-SA' };

const LANG_OPTIONS = [
  { code: 'en', label: 'English (US)' },
  { code: 'hi', label: 'Hindi (हिन्दी)' },
  { code: 'ta', label: 'Tamil (தமிழ்)' },
  { code: 'kn', label: 'Kannada (ಕನ್ನಡ)' },
  { code: 'ar', label: 'Arabic (العربية)' },
];

const TONE_INFO = [
  { id: 'polite', title: 'Polite', text: 'Everyday respectful register. Uses formal “you” (Aap / Neenga) without heavy honorifics.' },
  { id: 'traditional', title: 'Traditional', text: 'Elevated, deferential phrasing for elders, officials and ceremonial settings.' },
  { id: 'casual', title: 'Casual', text: 'Close, informal register (Tum / Tu) for friends, juniors and family.' },
];

const shortName = (code) => LANG_OPTIONS.find((l) => l.code === code)?.label.split(' ')[0];

export default function SpeechTranslator({ settings, onInsertToChat }) {
  const [langA, setLangA] = useState('en');
  const [langB, setLangB] = useState('hi');
  const [tone, setTone] = useState(settings.defaultTone);
  const [isRecording, setIsRecording] = useState(null); // 'A' | 'B' | null
  const [isLoading, setIsLoading] = useState(false);
  const [turns, setTurns] = useState([]); // [{ side, heard, result }]
  const [error, setError] = useState('');

  const recognitionRef = useRef(null);
  const voicesRef = useRef([]);
  const activeSpeakerRef = useRef(null); // live speaker for the speech callback (avoids stale closures)
  const settingsRef = useRef(settings);
  const threadRef = useRef(null);

  useEffect(() => { settingsRef.current = settings; }, [settings]);

  useEffect(() => {
    if (threadRef.current) threadRef.current.scrollTop = threadRef.current.scrollHeight;
  }, [turns, isLoading]);

  // Cache browser TTS voices
  useEffect(() => {
    if (!('speechSynthesis' in window)) return;
    const update = () => { voicesRef.current = window.speechSynthesis.getVoices(); };
    update();
    window.speechSynthesis.onvoiceschanged = update;
  }, []);

  // (Re)build the Web Speech recognizer whenever the language pair, tone or engine changes
  useEffect(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return;
    const recognition = new SR();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = async (event) => {
      const text = event.results[0][0].transcript;
      const side = activeSpeakerRef.current;
      setIsRecording(null);
      if (side) await handleTranslate(text, side);
    };
    recognition.onerror = (e) => {
      console.error('Speech recognition error:', e);
      setIsRecording(null);
      activeSpeakerRef.current = null;
      if (e.error && e.error !== 'aborted' && e.error !== 'no-speech') setError(`Speech recognition error: ${e.error}`);
    };
    recognition.onend = () => {
      setIsRecording(null);
      activeSpeakerRef.current = null;
    };
    recognitionRef.current = recognition;
  }, [langA, langB, tone, settings.provider]);

  const toggleRecording = (side) => {
    setError('');
    if (!recognitionRef.current) {
      setError('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }
    if (isRecording === side) {
      recognitionRef.current.stop();
      setIsRecording(null);
      activeSpeakerRef.current = null;
      return;
    }
    activeSpeakerRef.current = side;
    setIsRecording(side);
    // Speaker A speaks langA; Speaker B speaks langB
    recognitionRef.current.lang = BCP_MAP[side === 'A' ? langA : langB] || 'en-US';
    try {
      recognitionRef.current.start();
    } catch (err) {
      console.warn('Recognition already active or interrupted:', err);
    }
  };

  const handleTranslate = async (text, side) => {
    setIsLoading(true);
    // Speaker A: langA → langB. Speaker B: langB → langA.
    const src = side === 'A' ? langA : langB;
    const tgt = side === 'A' ? langB : langA;
    try {
      const res = await fetch(`${API_BASE}/speech-translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          audio_text: text,
          source_language: src,
          target_language: tgt,
          tone,
          provider: settingsRef.current.provider,
        }),
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Translation request failed');
      }
      const data = await res.json();
      setTurns((prev) => [...prev, { side, heard: text, srcLang: src, result: data }]);
      if (settingsRef.current.autoSpeak) playSpeech(data.translated_text, tgt);
    } catch (err) {
      console.error(err);
      setError(`Error translating speech: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const playSpeech = (text, langCode) => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = BCP_MAP[langCode] || 'en-US';
    utterance.rate = settingsRef.current.speechRate;
    const voices = voicesRef.current.length ? voicesRef.current : window.speechSynthesis.getVoices();
    const match = voices.find(
      (v) => v.lang && (v.lang.toLowerCase() === BCP_MAP[langCode]?.toLowerCase() || v.lang.toLowerCase().startsWith(langCode))
    );
    if (match) utterance.voice = match;
    window.speechSynthesis.speak(utterance);
  };

  const swapLanguages = () => {
    setLangA(langB);
    setLangB(langA);
  };

  return (
    <section className="page page-voice">
      <div className="v-wrap">
        <div className="v-main">
          <div className="card v-cfg">
            <div className="langrow">
              <div className="a">
                <label>Speaker 1 · Side A</label>
                <select value={langA} onChange={(e) => setLangA(e.target.value)}>
                  {LANG_OPTIONS.map((o) => <option key={o.code} value={o.code}>{o.label}</option>)}
                </select>
              </div>
              <button className="swapb" onClick={swapLanguages} title="Swap languages"><Icon name="swap" /></button>
              <div className="b">
                <label>Speaker 2 · Side B</label>
                <select value={langB} onChange={(e) => setLangB(e.target.value)}>
                  {LANG_OPTIONS.map((o) => <option key={o.code} value={o.code}>{o.label}</option>)}
                </select>
              </div>
            </div>
            <div>
              <div className="cap">Target tone</div>
              <div className="seg">
                {TONE_INFO.map((t) => (
                  <button key={t.id} className={tone === t.id ? 'on' : ''} onClick={() => setTone(t.id)}>{t.id}</button>
                ))}
              </div>
            </div>
          </div>

          <div className="card thread" ref={threadRef}>
            {turns.length === 0 && !isLoading && (
              <div className="empty">Tap a microphone below and speak.<br />The conversation and its calibrated translation will appear here.</div>
            )}
            {turns.map((t, i) => (
              <div key={i} className={`vb ${t.side === 'A' ? 'a' : 'b'}`}>
                <small>{t.side === 'A' ? 'Speaker 1' : 'Speaker 2'} · {shortName(t.srcLang)}</small>
                {t.heard}
                <div className="tr">{t.result.translated_text}</div>
                <div className="row">
                  {t.result.t_v_pronoun_used && <span className="pron">{t.result.t_v_pronoun_used}</span>}
                  <button onClick={() => playSpeech(t.result.translated_text, t.result.target_language)}>🔊 Replay</button>
                  <button onClick={() => onInsertToChat(t.result.translated_text)}>Insert to chat</button>
                </div>
                {t.result.cultural_notes && <div className="note">💡 {t.result.cultural_notes}</div>}
              </div>
            ))}
            {isLoading && <div className="loading"><span className="spin" />Applying {tone} pragmatic calibration…</div>}
          </div>

          {error && <div className="err" style={{ margin: 0 }}>{error}</div>}

          <div className="mics">
            <div className={`card mic ${isRecording === 'A' ? 'rec' : ''}`} onClick={() => !isLoading && toggleRecording('A')}>
              <div className="ring"><Icon name="mic" size={32} /></div>
              <b>Speak {shortName(langA)}</b>
              <span>{isRecording === 'A' ? 'Listening… tap to stop' : `Translates to ${shortName(langB)}`}</span>
            </div>
            <div className={`card mic bside ${isRecording === 'B' ? 'rec' : ''}`} onClick={() => !isLoading && toggleRecording('B')}>
              <div className="ring"><Icon name="mic" size={32} /></div>
              <b>Speak {shortName(langB)}</b>
              <span>{isRecording === 'B' ? 'Listening… tap to stop' : `Translates to ${shortName(langA)}`}</span>
            </div>
          </div>
        </div>

        <div className="v-side">
          {TONE_INFO.map((t) => (
            <div key={t.id} className="card tonecard" style={tone === t.id ? { borderColor: 'var(--accent)' } : undefined}
              onClick={() => setTone(t.id)}>
              <h4>{t.title}</h4>
              <p>{t.text}</p>
            </div>
          ))}
          <div className="card tonecard" style={{ borderColor: 'rgba(245,185,66,.35)' }}>
            <h4 style={{ color: 'var(--amber)' }}>Browser speech</h4>
            <p>Uses native Web Speech (STT + TTS). Best in Chrome or Edge.</p>
          </div>
        </div>
      </div>
    </section>
  );
}
