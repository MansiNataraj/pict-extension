import { useState } from 'react';

export const useThread = (initialMessages = []) => {
  const [thread, setThread] = useState(
    initialMessages.length > 0
      ? initialMessages
      : [
          { speaker: 'Manager', message: 'Kal presentation ready hona chahiye.' },
          { speaker: 'Employee', message: 'Haan tu chinta mat kar, ho jayega.' },
        ]
  );

  const addMessage = (speaker, message) => {
    if (!message || !message.trim()) return;
    setThread((prev) => [...prev, { speaker: speaker.trim() || 'Speaker', message: message.trim() }]);
  };

  const removeMessage = (index) => {
    setThread((prev) => prev.filter((_, i) => i !== index));
  };

  const parseRawText = (rawText) => {
    if (!rawText.trim()) return;
    const lines = rawText.split('\n').filter((l) => l.trim().length > 0);
    const parsed = lines.map((line) => {
      const match = line.match(/^([^:]+):\s*(.*)$/);
      if (match) {
        return { speaker: match[1].trim(), message: match[2].trim() };
      }
      return { speaker: 'Speaker', message: line.trim() };
    });
    setThread(parsed);
  };

  const clearThread = () => setThread([]);

  return { thread, setThread, addMessage, removeMessage, parseRawText, clearThread };
};