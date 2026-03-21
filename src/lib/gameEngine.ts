import countries from "@/data/countries.json";
import celebrities from "@/data/celebrities.json";
import animals from "@/data/animals.json";
import type { CategoryId, ChoiceQuestion } from "@/types/game";

const ROUND_SECONDS = 15;

const byCategory: Record<CategoryId, ChoiceQuestion[]> = {
  countries: countries as ChoiceQuestion[],
  celebrities: celebrities as ChoiceQuestion[],
  animals: animals as ChoiceQuestion[]
};

export function getRoundSeconds(): number {
  return ROUND_SECONDS;
}

export function listQuestions(category: CategoryId): ChoiceQuestion[] {
  return byCategory[category];
}

export function pickNextQuestion(category: CategoryId, recentIds: string[]): ChoiceQuestion {
  const pool = byCategory[category];
  const filtered = pool.filter((q) => !recentIds.includes(q.id));
  const source = filtered.length > 0 ? filtered : pool;
  return source[Math.floor(Math.random() * source.length)];
}

export function shuffleChoices(options: string[]): string[] {
  const arr = [...options];
  for (let i = arr.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

export function calculateRoundScore(remainingSeconds: number, streak: number): number {
  const base = 100;
  const speedBonus = Math.max(0, remainingSeconds) * 4;
  const streakMultiplier = 1 + Math.min(streak, 10) * 0.1;
  return Math.round((base + speedBonus) * streakMultiplier);
}

export function calculateRoundXp(remainingSeconds: number): number {
  return 40 + Math.max(0, remainingSeconds) * 2;
}
