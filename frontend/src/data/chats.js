// Seed conversation threads, one per recipient role.
// `from` is 'me' (the user) or 'them' (the recipient).
export const INITIAL_ROLE_CHATS = {
  senior: {
    id: 'senior',
    name: 'Dr. Rajesh Sharma',
    title: 'Director',
    role: 'senior',
    roleLabel: 'Superior / Senior',
    targetTone: 'Formal',
    pronoun: 'Aap / Neenga',
    expectation: 'High deference expected',
    tip: 'Open with a respectful address (महोदय) and use आप consistently.',
    avatar: '👨‍💼',
    unread: 1,
    checked: 0,
    flagged: 0,
    messages: [
      { from: 'them', text: 'कल सुबह 10 बजे बोर्ड मीटिंग में प्रोजेक्ट की स्थिति की समीक्षा होगी।', time: '10:31' },
      { from: 'me', text: 'जी महोदय, हमने सभी स्लाइड्स तैयार कर ली हैं।', time: '10:36' },
      { from: 'them', text: 'उत्तम। कृपया अंतिम रिपोर्ट का मसौदा आज शाम तक अवश्य प्रस्तुत कर दें।', time: '10:42' },
    ],
  },
  peer: {
    id: 'peer',
    name: 'Priya Verma',
    title: 'Product Lead',
    role: 'peer',
    roleLabel: 'Peer / Colleague',
    targetTone: 'Semi-Formal',
    pronoun: 'Tum / Aap',
    expectation: 'Balanced professional register',
    tip: 'Mix polite verbs with a warm tone. Avoid the tu form until rapport is established.',
    avatar: '👩‍💻',
    unread: 0,
    checked: 0,
    flagged: 0,
    messages: [
      { from: 'them', text: 'अरे, क्या तुम्हें API एंडपॉइंट्स का नया दस्तावेज़ मिल गया?', time: '09:02' },
      { from: 'me', text: 'हाँ, मैंने देख लिया है। सब ठीक लग रहा है।', time: '09:08' },
      { from: 'them', text: 'बढ़िया! क्या हम 4 बजे एक बार सिंक-अप कॉल कर सकते हैं?', time: '09:15' },
    ],
  },
  junior: {
    id: 'junior',
    name: 'Arun Kumar',
    title: 'Intern / Team',
    role: 'junior',
    roleLabel: 'Subordinate / Friend',
    targetTone: 'Informal',
    pronoun: 'Tum / Tu',
    expectation: 'Direct, colloquial',
    tip: 'A friendly tum works well. Keep corrections constructive, not commanding.',
    avatar: '🧑‍🎓',
    unread: 0,
    checked: 0,
    flagged: 0,
    messages: [
      { from: 'them', text: 'भैया, मैंने PR सबमिट कर दिया है। जब समय मिले एक बार देख लेना।', time: 'Yesterday' },
      { from: 'me', text: 'शानदार काम, अरुण। मैं अभी चेक करता हूँ।', time: 'Yesterday' },
      { from: 'them', text: 'थैंक्स! अगर कोई बदलाव करना हो तो बता देना।', time: 'Yesterday' },
    ],
  },
};

export const SCRIPT_OPTIONS = [
  { code: 'hi', label: 'Hindi (हिन्दी)' },
  { code: 'ta', label: 'Tamil (தமிழ்)' },
  { code: 'kn', label: 'Kannada (ಕನ್ನಡ)' },
  { code: 'ar', label: 'Arabic (العربية)' },
];

export const nowTime = () => {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
};
