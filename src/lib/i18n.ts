export type Lang = "en" | "he";

const LANG_KEY = "shadowguess.lang";

export function loadLang(): Lang {
  if (typeof window === "undefined") return "en";
  const stored = window.localStorage.getItem(LANG_KEY);
  return stored === "he" ? "he" : "en";
}

export function saveLang(lang: Lang): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(LANG_KEY, lang);
}

const translations: Record<string, Record<Lang, string>> = {
  title: { en: "ShadowGuess", he: "ShadowGuess" },
  subtitle: { en: "15 seconds to guess as many silhouettes as you can. Pick your best category and beat your high score!", he: "15 שניות לנחש כמה שיותר צלליות. בחרו את הקטגוריה הטובה ביותר שלכם ושברו את השיא!" },
  pickCategory: { en: "Choose a category and start guessing!", he: "!בחרו קטגוריה והתחילו לנחש" },
  bestScore: { en: "Best Score", he: "שיא" },
  bestStreak: { en: "Best Streak", he: "רצף שיא" },
  score: { en: "Score", he: "ניקוד" },
  streak: { en: "Streak", he: "רצף" },
  inCategory: { en: "in", he: "-ב" },
  useHint: { en: "Use hint", he: "רמז" },
  hintUsed: { en: "Hint used", he: "רמז נוצל" },
  gameOver: { en: "Game Over", he: "המשחק נגמר" },
  timesUp: { en: "Time's up!", he: "!נגמר הזמן" },
  wrong: { en: "Wrong! It was", he: "טעות! התשובה הייתה" },
  playAgain: { en: "Play Again", he: "שחקו שוב" },
  changeCategory: { en: "Change Category", he: "החלפת קטגוריה" },
  countries: { en: "Countries", he: "מדינות" },
  celebrities: { en: "Celebrities", he: "מפורסמים" },
  animals: { en: "Animals", he: "חיות" },
  landmarks: { en: "Landmarks", he: "אתרים" },
  objects: { en: "Objects", he: "חפצים" },
  noBestYet: { en: "No high score yet", he: "אין שיא עדיין" },
};

export function t(key: string, lang: Lang): string {
  return translations[key]?.[lang] ?? key;
}
