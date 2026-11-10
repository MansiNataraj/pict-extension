import React from 'react';
import Icon from './Icon';

export default function HomePage({ threads, onNavigate, onOpenChat }) {
  const list = Object.values(threads);
  return (
    <section className="page page-home">
      <div className="home-in">
        <div className="hero">
          <div className="eyebrow"><span />Cultural Risk Taxonomy (CRT) active</div>
          <h1>Communicate across cultures with zero pragmatic friction</h1>
          <p>
            Catch honorific mismatches, hierarchy risks and register errors before you hit send — across Hindi,
            Tamil, Kannada and Arabic, in text and in speech.
          </p>
          <div className="acts">
            <button className="btn primary" onClick={() => onNavigate('chats')}><Icon name="chat" />Open Text Chat</button>
            <button className="btn ghost" onClick={() => onNavigate('voice')}><Icon name="mic" />Start Voice Coach</button>
          </div>
        </div>

        <div className="stats">
          <div className="card stat"><b>4</b><span>Languages &amp; scripts</span></div>
          <div className="card stat"><b>5</b><span>CRT risk dimensions</span></div>
          <div className="card stat"><b>3</b><span>Role-calibrated workspaces</span></div>
          <div className="card stat"><b>2</b><span>Inference engines (cloud + local)</span></div>
        </div>

        <div className="modes">
          <div className="card mode" onClick={() => onNavigate('chats')}>
            <div className="ic-box"><Icon name="chat" size={26} /></div>
            <h3>Text Chat Guardrail</h3>
            <p>Messaging with a pre-send check. Flags wrong T-V pronouns (Tu vs. Aap) and hierarchy slips, then offers one-click Formal, Semi-Formal and Informal rewrites.</p>
            <div className="chips"><span>Pre-send hook</span><span>CRT checks</span><span>3-tone coaching</span></div>
          </div>
          <div className="card mode v" onClick={() => onNavigate('voice')}>
            <div className="ic-box"><Icon name="mic" size={26} /></div>
            <h3>Bidirectional Voice Coach</h3>
            <p>Live speech-to-speech translation with tone calibration. Speak naturally and choose Polite, Traditional or Casual output for each side of the conversation.</p>
            <div className="chips"><span>Push-to-talk</span><span>Tone calibration</span><span>Replay audio</span></div>
          </div>
        </div>

        <div className="two">
          <div className="card">
            <div className="sec-h"><h3>Recent conversations</h3><a onClick={() => onNavigate('chats')}>View all</a></div>
            <div className="recent">
              {list.map((t) => {
                const last = t.messages[t.messages.length - 1];
                return (
                  <div key={t.id} className="rrow" onClick={() => onOpenChat(t.id)}>
                    <div className="av">{t.avatar}</div>
                    <div className="t">
                      <b>{t.name} · <span className={`role ${t.role}`}>{t.roleLabel}</span></b>
                      <span>{last ? last.text : 'No messages yet'}</span>
                    </div>
                    <small style={{ color: 'var(--muted)' }}>{last?.time}</small>
                  </div>
                );
              })}
            </div>
          </div>
          <div className="card">
            <div className="sec-h"><h3>How PITC works</h3></div>
            <div className="how">
              <div><em>1</em><div><b>Draft</b><br /><span>Write in your own words, in any supported script.</span></div></div>
              <div><em>2</em><div><b>Coach</b><br /><span>CRT flags risk against the recipient’s role.</span></div></div>
              <div><em>3</em><div><b>Calibrate</b><br /><span>Pick the tone that fits and send with confidence.</span></div></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
