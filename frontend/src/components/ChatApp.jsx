import React, { useState, useEffect, useRef } from 'react';
import Icon from './Icon';
import { SCRIPT_OPTIONS, nowTime } from '../data/chats';

const API_BASE = 'http://localhost:8000';

const TICKS = (
  <svg className="ticks" viewBox="0 0 16 11" width="15" height="11" fill="currentColor">
    <path d="M11.07.65 4.9 7.49 2.6 5.4l-.9.99 3.26 3 7.1-7.84-1-.9zm3.6 0-6.17 6.84-.7-.64-.9.99 1.7 1.56 7.1-7.84-1.03-.91z" />
  </svg>
);

const TONES = [
  { key: 'formal', cls: 'formal', label: 'Formal', badge: 'High deference', field: 'formal', reaction: 'formal_reaction', fallback: 'Perceived as respectful and hierarchical.' },
  { key: 'semi_formal', cls: 'semi', label: 'Semi-Formal', badge: 'Polite / balanced', field: 'semi_formal', reaction: 'semi_formal_reaction', fallback: 'Standard polite workplace register.' },
  { key: 'casual', cls: 'casual', label: 'Informal', badge: 'Peer / direct', field: 'casual', reaction: 'casual_reaction', fallback: 'Close peer register; friendly and direct.' },
];

export default function ChatApp({
  threads,
  activeChatId,
  onSelectChat,
  onUpdateThread,
  settings,
  initialDraft = '',
  onDraftConsumed,
}) {
  const [draft, setDraft] = useState(initialDraft);
  const [language, setLanguage] = useState(settings.defaultScript);
  const [coachResult, setCoachResult] = useState(null);
  const [coachError, setCoachError] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedTone, setSelectedTone] = useState('formal');
  const [mobileOpen, setMobileOpen] = useState(false);
  const [filter, setFilter] = useState('all');
  const feedRef = useRef(null);

  const activeChat = threads[activeChatId];

  // Text handed over from the Voice Coach ("Insert to chat")
  useEffect(() => {
    if (initialDraft) {
      setDraft(initialDraft);
      setCoachResult(null);
      setMobileOpen(true);
      onDraftConsumed?.();
    }
  }, [initialDraft]);

  useEffect(() => {
    if (feedRef.current) feedRef.current.scrollTop = feedRef.current.scrollHeight;
  }, [activeChat.messages.length, activeChatId]);

  const selectThread = (id) => {
    onSelectChat(id);
    setDraft('');
    setCoachResult(null);
    setCoachError('');
    setMobileOpen(true);
  };

  // On-demand Cultural Risk coaching (calls the FastAPI /coach endpoint)
  const handleCoachDraft = async () => {
    if (!draft.trim()) return;
    setIsAnalyzing(true);
    setCoachError('');
    try {
      const res = await fetch(`${API_BASE}/coach`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          draft_message: draft,
          language_code: language,
          recipient_role: activeChat.role,
          provider: settings.provider,
        }),
      });
      if (!res.ok) throw new Error('Coaching check failed');
      const data = await res.json();
      setCoachResult(data);
      setSelectedTone('formal');
      onUpdateThread(activeChat.id, (t) => ({
        checked: (t.checked || 0) + 1,
        flagged: (t.flagged || 0) + (data.crt_code ? 1 : 0),
      }));
    } catch (err) {
      console.error('Coaching error:', err);
      setCoachResult(null);
      setCoachError(err.message || 'Coaching check failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSend = () => {
    if (!draft.trim()) return;
    onUpdateThread(activeChat.id, (t) => ({
      messages: [...t.messages, { from: 'me', text: draft.trim(), time: nowTime() }],
    }));
    setDraft('');
    setCoachResult(null);
    setCoachError('');
  };

  const visibleThreads = Object.values(threads).filter((t) => filter === 'all' || t.role === filter);
  const coachTag = coachResult?.risk_level === 'red' ? 'red' : coachResult?.risk_level === 'amber' ? 'amber' : 'green';

  return (
    <section className={`page page-chats ${mobileOpen ? 'open' : ''}`}>
      {/* ---------- conversation list ---------- */}
      <aside className="clist">
        <div className="clist-h"><h3>Conversations</h3></div>
        <div className="search"><Icon name="search" size={18} /><input placeholder="Search conversations" /></div>
        <div className="filters">
          {[['all', 'All'], ['senior', 'Senior'], ['peer', 'Peer'], ['junior', 'Junior']].map(([k, l]) => (
            <button key={k} className={filter === k ? 'on' : ''} onClick={() => setFilter(k)}>{l}</button>
          ))}
        </div>
        <div className="items">
          {visibleThreads.map((t) => {
            const last = t.messages[t.messages.length - 1];
            return (
              <div key={t.id} className={`item ${t.id === activeChatId ? 'on' : ''}`} onClick={() => selectThread(t.id)}>
                <div className="av">{t.avatar}</div>
                <div className="mid">
                  <div className="r"><span className="n">{t.name}</span><span className={`tm ${t.unread ? 'u' : ''}`}>{last?.time}</span></div>
                  <div className="r">
                    <span className="pv">{last?.from === 'me' ? 'You: ' : ''}{last?.text}</span>
                    {t.unread > 0 && <span className="bd">{t.unread}</span>}
                  </div>
                  <div><span className={`role ${t.role}`}>{t.roleLabel}</span></div>
                </div>
              </div>
            );
          })}
        </div>
        <div className="guard">
          <Icon name="shield" />
          <span><b>CRT guardrail on.</b> Drafts are checked for register, idiom, gender, hierarchy and sensitivity before sending.</span>
        </div>
      </aside>

      {/* ---------- active conversation ---------- */}
      <div className="convo">
        <div className="ch">
          <button className="tbtn back" onClick={() => setMobileOpen(false)} title="Back to conversations"><Icon name="back" /></button>
          <div className="av">{activeChat.avatar}</div>
          <div className="who">
            <b>{activeChat.name} · {activeChat.title}</b>
            <span>Enforcing register: <em>{activeChat.targetTone} ({activeChat.pronoun})</em></span>
          </div>
          <div className="scriptsel">
            <span>Script</span>
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              {SCRIPT_OPTIONS.map((o) => <option key={o.code} value={o.code}>{o.label}</option>)}
            </select>
          </div>
        </div>

        <div className="feed" ref={feedRef}>
          <div className="sys amber"><span>🛡️ Drafts in this thread are screened by the CRT before sending</span></div>
          {activeChat.messages.map((m, i) => {
            const prev = activeChat.messages[i - 1];
            return (
              <div key={i} className={`m ${m.from === 'me' ? 'out' : 'in'} ${prev && prev.from !== m.from ? 'gap' : ''}`}>
                <div className="bub">
                  {m.text}
                  <div className="meta">{m.time}{m.from === 'me' && TICKS}</div>
                </div>
              </div>
            );
          })}
        </div>

        {coachError && <div className="err">Coaching check failed: {coachError}. Is the backend running on port 8000?</div>}

        {coachResult && (
          <div className="coach">
            <div className="c-head">
              <div className="shield"><Icon name="shield" /></div>
              <div className="c-body">
                <div className="c-tags">
                  <span className={`tag ${coachTag}`}>{coachResult.crt_code ? `CRT violation · ${coachResult.crt_code}` : 'Tone verified'}</span>
                  <small>Recipient role: <b>{activeChat.roleLabel}</b></small>
                </div>
                <div className="c-warn">{coachResult.warning_message || 'Draft evaluated for sociopragmatic alignment.'}</div>
              </div>
              <button className="tbtn" onClick={() => setCoachResult(null)} title="Dismiss"><Icon name="close" /></button>
            </div>

            {coachResult.variants && (
              <>
                <div className="variants">
                  {TONES.map((t) => (
                    <div
                      key={t.key}
                      className={`var ${t.cls} ${selectedTone === t.key ? 'sel' : ''}`}
                      onClick={() => {
                        setSelectedTone(t.key);
                        setDraft(coachResult.variants[t.field]);
                      }}
                    >
                      <div className="vt"><b>{t.label}</b><i>{t.badge}</i></div>
                      <p>“{coachResult.variants[t.field]}”</p>
                      {settings.showReactions && (
                        <em>{coachResult.predicted_reactions?.[t.reaction] || t.fallback}</em>
                      )}
                    </div>
                  ))}
                </div>
                <div className="c-foot">Select a card to swap it into your draft. You can still edit before sending.</div>
              </>
            )}
          </div>
        )}

        <div className="comp">
          <div className="field">
            <input
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder={`Write a message to ${activeChat.name.replace(/^Dr\.\s*/, '').split(' ')[0]}…`}
            />
          </div>
          <button className="cbtn" onClick={handleCoachDraft} disabled={!draft.trim() || isAnalyzing}
            title="Analyse draft and calibrate across Formal, Semi-Formal and Informal tones">
            {isAnalyzing ? <span className="spin" /> : <Icon name="shield" />}Coach Me
          </button>
          <button className="sendb" onClick={handleSend} disabled={!draft.trim()} title="Send"><Icon name="send" /></button>
        </div>
      </div>

      {/* ---------- recipient side panel ---------- */}
      <aside className="info">
        <div className="prof">
          <div className="av">{activeChat.avatar}</div>
          <b>{activeChat.name}</b>
          <small style={{ color: 'var(--muted)' }}>{activeChat.title}</small>
          <span className={`role ${activeChat.role}`}>{activeChat.roleLabel}</span>
        </div>
        <div className="box">
          <h4>Register guide</h4>
          <div className="kv"><span>Target tone</span><b>{activeChat.targetTone}</b></div>
          <div className="kv"><span>Pronoun</span><b>{activeChat.pronoun}</b></div>
          <div className="kv"><span>Expectation</span><b style={{ textAlign: 'right' }}>{activeChat.expectation}</b></div>
        </div>
        <div className="box">
          <h4>Thread insights</h4>
          <div className="kv"><span>Drafts checked</span><b>{activeChat.checked}</b></div>
          <div className="kv"><span>Risks flagged</span><b>{activeChat.flagged}</b></div>
          {activeChat.checked > 0 && (
            <>
              <div className="kv"><span>Clean drafts</span><b>{Math.round(((activeChat.checked - activeChat.flagged) / activeChat.checked) * 100)}%</b></div>
              <div className="meter"><i style={{ width: `${((activeChat.checked - activeChat.flagged) / activeChat.checked) * 100}%` }} /></div>
            </>
          )}
        </div>
        <div className="box">
          <h4>Coaching tip</h4>
          <div className="tip">{activeChat.tip}</div>
        </div>
      </aside>
    </section>
  );
}
