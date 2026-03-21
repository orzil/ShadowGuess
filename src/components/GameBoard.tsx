"use client";

import { useEffect, useMemo, useState } from "react";
import {
  calculateRoundScore,
  calculateRoundXp,
  getRoundSeconds,
  pickNextQuestion,
  shuffleChoices
} from "@/lib/gameEngine";
import { applyXp, defaultProfile, loadProfile, saveProfile, xpToNextLevel } from "@/lib/progression";
import type { CategoryId, ChoiceQuestion, PlayerProfile, UnlockableCategoryId } from "@/types/game";

type ActiveCategoryCard = {
  id: UnlockableCategoryId;
  label: string;
};

const categoryCards: ActiveCategoryCard[] = [
  { id: "countries", label: "Countries" },
  { id: "celebrities", label: "Celebrities" },
  { id: "landmarks", label: "Landmarks" },
  { id: "animals", label: "Animals" },
  { id: "objects", label: "Objects" }
];

export default function GameBoard() {
  const [profile, setProfile] = useState<PlayerProfile>(defaultProfile);
  const [isMounted, setIsMounted] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<CategoryId | null>(null);
  const [question, setQuestion] = useState<ChoiceQuestion | null>(null);
  const [choices, setChoices] = useState<string[]>([]);
  const [remaining, setRemaining] = useState<number>(getRoundSeconds());
  const [score, setScore] = useState(0);
  const [streak, setStreak] = useState(0);
  const [hintUsed, setHintUsed] = useState(false);
  const [status, setStatus] = useState<"idle" | "playing" | "gameover">("idle");
  const [usedQuestionIds, setUsedQuestionIds] = useState<string[]>([]);
  const [message, setMessage] = useState("Pick a category to start.");

  useEffect(() => {
    const raf = window.requestAnimationFrame(() => {
      setProfile(loadProfile());
      setIsMounted(true);
    });
    return () => window.cancelAnimationFrame(raf);
  }, []);

  useEffect(() => {
    if (status !== "playing") return;
    const timer = window.setTimeout(() => {
      setRemaining((s) => {
        if (s <= 1) {
          setStatus("gameover");
          setMessage("Time is up! Game over.");
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => window.clearTimeout(timer);
  }, [remaining, status]);

  useEffect(() => {
    saveProfile(profile);
  }, [profile]);

  const xpNext = useMemo(() => xpToNextLevel(profile.level), [profile.level]);

  const startRound = (category: CategoryId, resetRun: boolean) => {
    const excludedIds = resetRun ? [] : usedQuestionIds;
    const q = pickNextQuestion(category, excludedIds);
    setSelectedCategory(category);
    setQuestion(q);
    setChoices(shuffleChoices(q.options));
    setRemaining(getRoundSeconds());
    setHintUsed(false);
    setStatus("playing");
    setMessage(`Category: ${category}. Guess before time runs out.`);
    if (resetRun) {
      setScore(0);
      setStreak(0);
      setUsedQuestionIds([q.id]);
    } else {
      setUsedQuestionIds((prev) => [...prev, q.id]);
    }
  };

  const handleChoice = (choice: string) => {
    if (!question || status !== "playing") return;

    if (choice !== question.answer) {
      setStatus("gameover");
      setMessage(`Wrong answer: ${choice}. Correct was ${question.answer}.`);
      setProfile((prev) => ({
        ...prev,
        bestScore: Math.max(prev.bestScore, score),
        bestStreak: Math.max(prev.bestStreak, streak)
      }));
      return;
    }

    const addedScore = calculateRoundScore(remaining, streak);
    const addedXp = calculateRoundXp(remaining);
    setScore((s) => s + addedScore);
    setStreak((s) => s + 1);
    setProfile((prev) =>
      applyXp(
        {
          ...prev,
          bestScore: Math.max(prev.bestScore, score + addedScore),
          bestStreak: Math.max(prev.bestStreak, streak + 1)
        },
        addedXp
      )
    );
    setMessage(`Correct! +${addedScore} points, +${addedXp} XP.`);
    if (selectedCategory) {
      startRound(selectedCategory, false);
    }
  };

  return (
    <main style={{ maxWidth: 980, margin: "0 auto", padding: 24 }}>
      <h1 style={{ marginBottom: 6, color: "#fef08a", textShadow: "0 2px 14px rgba(245, 158, 11, 0.45)" }}>
        ShadowGuess
      </h1>
      <p style={{ marginTop: 0, opacity: 0.95, color: "#bfdbfe" }}>
        30s per silhouette. 1 wrong answer ends the run. Use one hint per round.
      </p>

      <section style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 16 }}>
        {categoryCards.map((cat) => {
          const unlocked = isMounted && profile.unlockedCategories.includes(cat.id);
          return (
            <button
              key={cat.id}
              disabled={!unlocked}
              onClick={() => unlocked && startRound(cat.id as CategoryId, true)}
              style={{
                border: "1px solid #60a5fa",
                borderRadius: 12,
                padding: "10px 14px",
                background: unlocked
                  ? "linear-gradient(135deg, rgba(14,165,233,0.28), rgba(99,102,241,0.35))"
                  : "rgba(15, 23, 42, 0.5)",
                color: unlocked ? "#fef9c3" : "#94a3b8",
                cursor: unlocked ? "pointer" : "not-allowed"
              }}
            >
              {cat.label}
              {!unlocked ? " (Locked)" : ""}
            </button>
          );
        })}
      </section>

      <section
        style={{
          border: "1px solid rgba(96, 165, 250, 0.45)",
          borderRadius: 14,
          padding: 16,
          marginBottom: 14,
          background: "linear-gradient(170deg, rgba(30,41,59,0.86), rgba(30,58,138,0.45))"
        }}
      >
        <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 10, color: "#fde68a" }}>
          <strong>Score: {score}</strong>
          <strong>Streak: {streak}</strong>
          <strong>Timer: {remaining}s</strong>
          <strong>
            Level: {profile.level} ({profile.xp}/{xpNext} XP)
          </strong>
        </div>
        <p style={{ marginTop: 0 }}>{message}</p>

        {question && (
          <>
            <div
              style={{
                position: "relative",
                width: "min(100%, 460px)",
                aspectRatio: "1 / 1",
                borderRadius: 12,
                overflow: "hidden",
                border: "1px solid rgba(56, 189, 248, 0.7)",
                marginBottom: 14
              }}
            >
              <img
                src={question.silhouetteImage}
                alt="silhouette"
                style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
              />
              <img
                src={question.originalImage}
                alt="hint reveal"
                style={{
                  position: "absolute",
                  inset: 0,
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                  display: hintUsed ? "block" : "none",
                  maskImage: `url(${question.hintMask})`,
                  maskSize: "cover",
                  WebkitMaskImage: `url(${question.hintMask})`,
                  WebkitMaskSize: "cover"
                }}
              />
            </div>

            <button
              onClick={() => setHintUsed(true)}
              disabled={hintUsed || status !== "playing"}
              style={{
                border: "1px solid #22d3ee",
                borderRadius: 10,
                padding: "8px 12px",
                marginBottom: 12,
                background: hintUsed
                  ? "rgba(15,23,42,0.7)"
                  : "linear-gradient(135deg, rgba(34,211,238,0.35), rgba(99,102,241,0.35))",
                color: hintUsed ? "#94a3b8" : "#f0f9ff"
              }}
            >
              {hintUsed ? "Hint used" : "Use hint"}
            </button>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 10 }}>
              {choices.map((choice) => (
                <button
                  key={choice}
                  onClick={() => handleChoice(choice)}
                  disabled={status !== "playing"}
                  style={{
                    border: "1px solid rgba(167, 139, 250, 0.7)",
                    borderRadius: 10,
                    padding: "10px 12px",
                    textAlign: "left",
                    background: "linear-gradient(130deg, rgba(30,41,59,0.78), rgba(88,28,135,0.35))",
                    color: "#f8fafc"
                  }}
                >
                  {choice}
                </button>
              ))}
            </div>
          </>
        )}
      </section>

      {status === "gameover" && selectedCategory && (
        <button
          onClick={() => startRound(selectedCategory, true)}
          style={{
            border: "1px solid #f59e0b",
            borderRadius: 10,
            padding: "10px 16px",
            background: "linear-gradient(135deg, rgba(245,158,11,0.5), rgba(239,68,68,0.45))",
            color: "#fff7ed"
          }}
        >
          Play again
        </button>
      )}
    </main>
  );
}
