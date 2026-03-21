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
  comingSoon?: boolean;
};

const categoryCards: ActiveCategoryCard[] = [
  { id: "countries", label: "Countries" },
  { id: "celebrities", label: "Celebrities" },
  { id: "animals", label: "Animals" },
  { id: "landmarks", label: "Landmarks", comingSoon: true },
  { id: "objects", label: "Objects", comingSoon: true }
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
  const [gameOverReason, setGameOverReason] = useState("");

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
          setGameOverReason("Time's up!");
          setProfile((prev) => ({
            ...prev,
            bestScore: Math.max(prev.bestScore, score),
            bestStreak: Math.max(prev.bestStreak, streak)
          }));
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => window.clearTimeout(timer);
  }, [remaining, status, score, streak]);

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
    setGameOverReason("");
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
      setGameOverReason(`Wrong! It was ${question.answer}`);
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

  const timerPct = (remaining / getRoundSeconds()) * 100;
  const timerColor = remaining <= 5 ? "#ef4444" : remaining <= 10 ? "#f59e0b" : "#22d3ee";

  return (
    <main style={{ maxWidth: 540, margin: "0 auto", padding: "20px 16px" }}>
      <header style={{ textAlign: "center", marginBottom: 20 }}>
        <h1 style={{ margin: 0, fontSize: "2rem", color: "#fef08a", textShadow: "0 2px 14px rgba(245, 158, 11, 0.45)" }}>
          ShadowGuess
        </h1>
        <p style={{ margin: "4px 0 0", fontSize: "0.85rem", opacity: 0.8, color: "#bfdbfe" }}>
          30s per silhouette. 1 wrong answer ends the run.
        </p>
      </header>

      <section style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "center", marginBottom: 16 }}>
        {categoryCards.map((cat) => {
          const unlocked = !cat.comingSoon && isMounted && profile.unlockedCategories.includes(cat.id);
          const disabled = cat.comingSoon || !unlocked;
          return (
            <button
              key={cat.id}
              disabled={disabled}
              onClick={() => unlocked && startRound(cat.id as CategoryId, true)}
              style={{
                border: cat.comingSoon ? "1px solid #334155" : "1px solid #60a5fa",
                borderRadius: 10,
                padding: "8px 16px",
                fontSize: "0.9rem",
                background: unlocked
                  ? "linear-gradient(135deg, rgba(14,165,233,0.28), rgba(99,102,241,0.35))"
                  : "rgba(15, 23, 42, 0.5)",
                color: cat.comingSoon ? "#475569" : unlocked ? "#fef9c3" : "#94a3b8",
                cursor: disabled ? "not-allowed" : "pointer",
                textDecoration: cat.comingSoon ? "line-through" : "none"
              }}
            >
              {cat.label}
            </button>
          );
        })}
      </section>

      <section
        style={{
          border: "1px solid rgba(96, 165, 250, 0.3)",
          borderRadius: 16,
          padding: "16px 16px 20px",
          background: "linear-gradient(170deg, rgba(30,41,59,0.9), rgba(30,58,138,0.4))"
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8, fontSize: "0.85rem", color: "#fde68a" }}>
          <span>Score: <strong>{score}</strong></span>
          <span>Streak: <strong>{streak}</strong></span>
          <span>Lv <strong>{profile.level}</strong> ({profile.xp}/{xpNext})</span>
        </div>

        {status === "playing" && (
          <div style={{ height: 4, borderRadius: 2, background: "rgba(255,255,255,0.1)", marginBottom: 12, overflow: "hidden" }}>
            <div style={{
              height: "100%",
              width: `${timerPct}%`,
              background: timerColor,
              borderRadius: 2,
              transition: "width 1s linear, background 0.3s"
            }} />
          </div>
        )}

        {status === "idle" && (
          <p style={{ textAlign: "center", color: "#94a3b8", margin: "40px 0" }}>{message}</p>
        )}

        {question && status === "playing" && (
          <>
            <div
              style={{
                position: "relative",
                width: "100%",
                maxWidth: 400,
                aspectRatio: "1 / 1",
                borderRadius: 14,
                overflow: "hidden",
                border: "1px solid rgba(56, 189, 248, 0.4)",
                margin: "0 auto 14px",
                background: "#0f172a"
              }}
            >
              <img
                src={question.silhouetteImage}
                alt="silhouette"
                style={{ width: "100%", height: "100%", objectFit: "contain", display: "block" }}
              />
              <img
                src={question.originalImage}
                alt="hint reveal"
                style={{
                  position: "absolute",
                  inset: 0,
                  width: "100%",
                  height: "100%",
                  objectFit: "contain",
                  display: hintUsed ? "block" : "none",
                  maskImage: `url(${question.hintMask})`,
                  maskSize: "cover",
                  WebkitMaskImage: `url(${question.hintMask})`,
                  WebkitMaskSize: "cover"
                }}
              />
            </div>

            <div style={{ textAlign: "center", marginBottom: 12 }}>
              <button
                onClick={() => setHintUsed(true)}
                disabled={hintUsed}
                style={{
                  border: "1px solid #22d3ee",
                  borderRadius: 8,
                  padding: "6px 16px",
                  fontSize: "0.85rem",
                  background: hintUsed
                    ? "rgba(15,23,42,0.7)"
                    : "linear-gradient(135deg, rgba(34,211,238,0.3), rgba(99,102,241,0.3))",
                  color: hintUsed ? "#64748b" : "#f0f9ff"
                }}
              >
                {hintUsed ? "Hint used" : "Use hint"}
              </button>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
              {choices.map((choice) => (
                <button
                  key={choice}
                  onClick={() => handleChoice(choice)}
                  style={{
                    border: "1px solid rgba(167, 139, 250, 0.5)",
                    borderRadius: 10,
                    padding: "12px 10px",
                    textAlign: "center",
                    fontSize: "0.9rem",
                    background: "linear-gradient(130deg, rgba(30,41,59,0.8), rgba(88,28,135,0.3))",
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

      {status === "gameover" && (
        <div className="overlay" onClick={() => {}}>
          <div className="modal">
            <div style={{ fontSize: "2.5rem", marginBottom: 8 }}>
              {gameOverReason.startsWith("Wrong") ? "X" : "O"}
            </div>
            <h2 style={{ margin: "0 0 4px", color: "#fef08a", fontSize: "1.4rem" }}>Game Over</h2>
            <p style={{ margin: "0 0 16px", color: "#94a3b8", fontSize: "0.9rem" }}>{gameOverReason}</p>

            <div style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: 12,
              marginBottom: 20,
              textAlign: "center"
            }}>
              <div style={{ background: "rgba(255,255,255,0.05)", borderRadius: 10, padding: "12px 8px" }}>
                <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#fef08a" }}>{score}</div>
                <div style={{ fontSize: "0.75rem", color: "#94a3b8" }}>Score</div>
              </div>
              <div style={{ background: "rgba(255,255,255,0.05)", borderRadius: 10, padding: "12px 8px" }}>
                <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#fef08a" }}>{streak}</div>
                <div style={{ fontSize: "0.75rem", color: "#94a3b8" }}>Streak</div>
              </div>
              <div style={{ background: "rgba(255,255,255,0.05)", borderRadius: 10, padding: "12px 8px" }}>
                <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#a78bfa" }}>{profile.bestScore}</div>
                <div style={{ fontSize: "0.75rem", color: "#94a3b8" }}>Best Score</div>
              </div>
              <div style={{ background: "rgba(255,255,255,0.05)", borderRadius: 10, padding: "12px 8px" }}>
                <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#a78bfa" }}>{profile.bestStreak}</div>
                <div style={{ fontSize: "0.75rem", color: "#94a3b8" }}>Best Streak</div>
              </div>
            </div>

            <button
              onClick={() => selectedCategory && startRound(selectedCategory, true)}
              style={{
                width: "100%",
                border: "none",
                borderRadius: 10,
                padding: "12px 20px",
                fontSize: "1rem",
                fontWeight: 600,
                background: "linear-gradient(135deg, #f59e0b, #ef4444)",
                color: "#fff",
                cursor: "pointer"
              }}
            >
              Play Again
            </button>
            <button
              onClick={() => { setStatus("idle"); setQuestion(null); setSelectedCategory(null); setScore(0); setStreak(0); }}
              style={{
                width: "100%",
                border: "1px solid rgba(148,163,184,0.3)",
                borderRadius: 10,
                padding: "10px 20px",
                marginTop: 8,
                fontSize: "0.85rem",
                background: "transparent",
                color: "#94a3b8",
                cursor: "pointer"
              }}
            >
              Change Category
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
