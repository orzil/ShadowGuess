export type CategoryId = "countries" | "celebrities" | "animals" | "landmarks" | "food";

export type FutureCategoryId = "objects";

export type UnlockableCategoryId = CategoryId | FutureCategoryId;

export type ChoiceQuestion = {
  id: string;
  category: CategoryId;
  answer: string;
  options: string[];
  silhouetteImage: string;
  originalImage: string;
  hintMask: string;
  sourceUrl: string;
  license: string;
  author: string;
};

export type PlayerProfile = {
  xp: number;
  level: number;
  unlockedCategories: UnlockableCategoryId[];
  bestScore: number;
  bestStreak: number;
  bestCategory: CategoryId | null;
};

export type RoundView = {
  question: ChoiceQuestion;
  choices: string[];
  remainingSeconds: number;
  hintUsed: boolean;
  score: number;
  streak: number;
};
