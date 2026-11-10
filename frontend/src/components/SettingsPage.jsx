import React from 'react';
import { SCRIPT_OPTIONS } from '../data/chats';

const ENGINES = [
  { id: 'auto', label: 'Auto', desc: 'Gemini, then Ollama aya-expanse:8b' },
  { id: 'cloud', label: 'Cloud only', desc: 'Gemini 2.5 Flash / Flash-Lite' },
  { id: 'local', label: 'Local only', desc: 'Ollama on this machine' },
];

function Toggle({ on, onClick }) {
  return <div className={`tg ${on ? 'on' : ''}`} onClick={onClick} role="switch" aria-checked={on} />;
}

export default function SettingsPage({ settings, onChange }) {
  return (
    <section className="page page-set">
      <div className="set-in">
        <div className="card group">
          <h3>Inference engine</h3>
          <p>Primary cloud model with an automatic local fallback when rate-limited or offline.</p>
          <div className="engs">
            {ENGINES.map((e) => (
              <div key={e.id} className={`eng ${settings.provider === e.id ? 'on' : ''}`} onClick={() => onChange('provider', e.id)}>
                <b>{e.label}</b><span>{e.desc}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card group">
          <h3>Language &amp; coaching</h3>
          <div className="srow">
            <div><b>Default script</b><span>Used when opening a chat</span></div>
            <select value={settings.defaultScript} onChange={(e) => onChange('defaultScript', e.target.value)}>
              {SCRIPT_OPTIONS.map((o) => <option key={o.code} value={o.code}>{o.label}</option>)}
            </select>
          </div>
          <div className="srow">
            <div><b>Show predicted recipient reaction</b><span>Display a one-line perception under each tone card</span></div>
            <Toggle on={settings.showReactions} onClick={() => onChange('showReactions', !settings.showReactions)} />
          </div>
        </div>

        <div className="card group">
          <h3>Voice</h3>
          <div className="srow">
            <div><b>Default tone</b><span>Starting tone for the Voice Coach</span></div>
            <select value={settings.defaultTone} onChange={(e) => onChange('defaultTone', e.target.value)}>
              <option value="polite">Polite</option>
              <option value="traditional">Traditional</option>
              <option value="casual">Casual</option>
            </select>
          </div>
          <div className="srow">
            <div><b>Speak translation aloud</b><span>Play the translated text with browser text-to-speech</span></div>
            <Toggle on={settings.autoSpeak} onClick={() => onChange('autoSpeak', !settings.autoSpeak)} />
          </div>
          <div className="srow">
            <div><b>Speech rate</b><span>Playback speed of spoken output ({settings.speechRate.toFixed(2)}×)</span></div>
            <input type="range" min="0.6" max="1.3" step="0.02" value={settings.speechRate}
              onChange={(e) => onChange('speechRate', parseFloat(e.target.value))} />
          </div>
        </div>

        <div className="card group">
          <h3>Appearance</h3>
          <div className="srow">
            <div><b>Light theme</b><span>Switch between dark and light</span></div>
            <Toggle on={settings.theme === 'light'} onClick={() => onChange('theme', settings.theme === 'light' ? 'dark' : 'light')} />
          </div>
        </div>
      </div>
    </section>
  );
}
