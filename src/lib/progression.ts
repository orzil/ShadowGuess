import type { PlayerProfile, UnlockableCategoryId } from "@/types/game";

const PROFILE_KEY = "shadowguess.profile.v1";
const BASE_UNLOCKS: UnlockableCategoryId[] = ["countries", "celebrities", "animals"];

const unlockTable: Array<{ level: number; category: UnlockableCategoryId }> = [
  { level: 2, category: "landmarks" },
  { level: 3, category: "objects" }
];

export const defaultProfile: PlayerProfile = {
  xp: 0,
  level: 1,
  unlockedCategories: BASE_UNLOCKS,
  bestScore: 0,
  bestStreak: 0
};

export function xpToNextLevel(level: number): number {
  return 250 + (level - 1) * 150;
}

export function loadProfile(): PlayerProfile {
  if (typeof window === "undefined") {
    return defaultProfile;
  }

  try {
    const raw = window.localStorage.getItem(PROFILE_KEY);
    if (!raw) return defaultProfile;
    const parsed = JSON.parse(raw) as PlayerProfile;
    return {
      ...defaultProfile,
      ...parsed,
      unlockedCategories: Array.from(
        new Set([...(parsed.unlockedCategories ?? []), ...BASE_UNLOCKS])
      )
    };
  } catch {
    return defaultProfile;
  }
}

export function saveProfile(profile: PlayerProfile): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
}

export function applyXp(profile: PlayerProfile, addedXp: number): PlayerProfile {
  let xpPool = profile.xp + addedXp;
  let level = profile.level;

  while (xpPool >= xpToNextLevel(level)) {
    xpPool -= xpToNextLevel(level);
    level += 1;
  }

  const unlocked = new Set<UnlockableCategoryId>([...profile.unlockedCategories, ...BASE_UNLOCKS]);
  unlockTable.forEach((entry) => {
    if (level >= entry.level) unlocked.add(entry.category);
  });

  return {
    ...profile,
    xp: xpPool,
    level,
    unlockedCategories: [...unlocked]
  };
}
