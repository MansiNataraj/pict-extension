import React from 'react';

const DIMENSIONS = [
  { code: 'C1', title: 'Register / Pronoun mismatch', desc: 'T-V distinction: Tu vs. Tum vs. Aap; Nee vs. Neenga; Inta vs. Antum.', bad: 'तुम फ़ाइल भेजो (to a Director)', good: 'आप फ़ाइल भेजिए' },
  { code: 'C2', title: 'Idiomatic opacity', desc: 'Detects literal translations of culture-specific idioms that lose or flip meaning.', bad: '“It’s raining cats and dogs” translated word for word', good: 'बहुत तेज़ बारिश हो रही है' },
  { code: 'C3', title: 'Gender agreement discordance', desc: 'Flags grammatical concord that does not match the speaker or addressee.', bad: 'मैं आ रहा हूँ (female speaker)', good: 'मैं आ रही हूँ' },
  { code: 'C4', title: 'Hierarchy & seniority violations', desc: 'Audits the deference expected toward superiors and elders.', bad: 'Do this by tonight.', good: 'Sir, may I share it with you by this evening?' },
  { code: 'C5', title: 'Socio-cultural & religious sensitivities', desc: 'Warns about timing, greetings and references that may clash with religious or cultural practice.', bad: 'Let’s hold the all-hands on Friday at 1 PM (Arabic-speaking team)', good: 'Suggest a slot that avoids Friday midday prayer time', wide: true },
];

export default function CrtGuide() {
  return (
    <section className="page page-crt">
      <div className="crt-in">
        <p>
          The Cultural Risk Taxonomy scores every outbound draft against five sociopragmatic dimensions. When a
          risk is found, PITC explains it and suggests calibrated rewrites.
        </p>
        <div className="crt-grid">
          {DIMENSIONS.map((d) => (
            <div key={d.code} className="card crt" style={d.wide ? { gridColumn: '1 / -1' } : undefined}>
              <div className="top"><div className="code">{d.code}</div><h3>{d.title}</h3></div>
              <p>{d.desc}</p>
              <div className="ex">
                <div className="bad"><b>Risky</b>{d.bad}</div>
                <div className="good"><b>Better</b>{d.good}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
