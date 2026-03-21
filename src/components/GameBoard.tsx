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
import { loadLang, saveLang, t } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import type { CategoryId, ChoiceQuestion, PlayerProfile, UnlockableCategoryId } from "@/types/game";

type ActiveCategoryCard = {
  id: UnlockableCategoryId;
  labelKey: string;
  comingSoon?: boolean;
};

const categoryCards: ActiveCategoryCard[] = [
  { id: "countries", labelKey: "countries" },
  { id: "celebrities", labelKey: "celebrities" },
  { id: "animals", labelKey: "animals" },
  { id: "landmarks", labelKey: "landmarks" },
  { id: "food", labelKey: "food" },
  { id: "objects", labelKey: "objects", comingSoon: true }
];

export default function GameBoard() {
  const [lang, setLang] = useState<Lang>("en");
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
  const [gameOverReason, setGameOverReason] = useState("");

  const isHe = lang === "he";

  useEffect(() => {
    const raf = window.requestAnimationFrame(() => {
      setProfile(loadProfile());
      setLang(loadLang());
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
          setGameOverReason(t("timesUp", lang));
          setProfile((prev) => {
            const isBest = score > prev.bestScore;
            return {
              ...prev,
              bestScore: Math.max(prev.bestScore, score),
              bestStreak: Math.max(prev.bestStreak, streak),
              bestCategory: isBest && selectedCategory ? selectedCategory : prev.bestCategory
            };
          });
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => window.clearTimeout(timer);
  }, [remaining, status, score, streak, lang, selectedCategory]);

  useEffect(() => {
    saveProfile(profile);
  }, [profile]);

  const xpNext = useMemo(() => xpToNextLevel(profile.level), [profile.level]);

  const toggleLang = () => {
    const next = lang === "en" ? "he" : "en";
    setLang(next);
    saveLang(next);
  };

  const nextQuestion = (category: CategoryId, excludedIds: string[]) => {
    const q = pickNextQuestion(category, excludedIds);
    setQuestion(q);
    setChoices(shuffleChoices(q.options));
    setHintUsed(false);
    return q;
  };

  const startRound = (category: CategoryId) => {
    const q = nextQuestion(category, []);
    setSelectedCategory(category);
    setRemaining(getRoundSeconds());
    setStatus("playing");
    setGameOverReason("");
    setScore(0);
    setStreak(0);
    setUsedQuestionIds([q.id]);
  };

  const handleChoice = (choice: string) => {
    if (!question || status !== "playing") return;

    if (choice !== question.answer) {
      setStatus("gameover");
      setGameOverReason(`${t("wrong", lang)} ${question.answer}`);
      setProfile((prev) => {
        const isBest = score > prev.bestScore;
        return {
          ...prev,
          bestScore: Math.max(prev.bestScore, score),
          bestStreak: Math.max(prev.bestStreak, streak),
          bestCategory: isBest && selectedCategory ? selectedCategory : prev.bestCategory
        };
      });
      return;
    }

    const addedScore = calculateRoundScore(remaining, streak);
    const addedXp = calculateRoundXp(remaining);
    const newScore = score + addedScore;
    const newStreak = streak + 1;
    setScore(newScore);
    setStreak(newStreak);
    setProfile((prev) => {
      const isBest = newScore > prev.bestScore;
      return applyXp(
        {
          ...prev,
          bestScore: Math.max(prev.bestScore, newScore),
          bestStreak: Math.max(prev.bestStreak, newStreak),
          bestCategory: isBest && selectedCategory ? selectedCategory : prev.bestCategory
        },
        addedXp
      );
    });
    if (selectedCategory) {
      const newUsed = [...usedQuestionIds, question.id];
      setUsedQuestionIds(newUsed);
      nextQuestion(selectedCategory, newUsed);
    }
  };

  const timerPct = (remaining / getRoundSeconds()) * 100;
  const timerColor = remaining <= 3 ? "#ef4444" : remaining <= 7 ? "#f59e0b" : "#22d3ee";

  const xpPct = xpNext > 0 ? Math.min((profile.xp / xpNext) * 100, 100) : 0;

  return (
    <main style={{ maxWidth: 520, margin: "0 auto", padding: "16px 14px 20px", direction: isHe ? "rtl" : "ltr" }}>
      {/* Header */}
      <header style={{ textAlign: "center", marginBottom: 16, position: "relative" }}>
        <button className="lang-toggle" onClick={toggleLang} style={{ position: "absolute", top: 4, [isHe ? "left" : "right"]: 0 }}>
          {isHe ? "EN" : "HE"}
        </button>

        <h1 style={{
          margin: 0,
          fontSize: "3.2rem",
          fontWeight: 900,
          letterSpacing: "-0.03em",
          background: "linear-gradient(135deg, #fef08a 0%, #fbbf24 40%, #f59e0b 70%, #fef08a 100%)",
          backgroundSize: "200% auto",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          animation: "shimmer 3s linear infinite",
          filter: "drop-shadow(0 2px 12px rgba(251, 191, 36, 0.4))",
          lineHeight: 1.1
        }}>
          {t("title", lang)}
        </h1>

        <p style={{
          margin: "10px auto 0",
          maxWidth: 400,
          fontSize: "1.05rem",
          fontWeight: 500,
          color: "#94a3b8",
          lineHeight: 1.6,
          whiteSpace: "pre-line"
        }}>
          {t("subtitle", lang)}
        </p>
      </header>

      {/* Category chips */}
      <section style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "center", marginBottom: 14 }}>
        {categoryCards.map((cat) => {
          const unlocked = !cat.comingSoon && isMounted && profile.unlockedCategories.includes(cat.id);
          const disabled = cat.comingSoon || !unlocked;
          return (
            <button
              key={cat.id}
              disabled={disabled}
              onClick={() => unlocked && startRound(cat.id as CategoryId)}
              className={`cat-chip${cat.comingSoon ? " coming-soon" : ""}`}
              style={unlocked ? {
                background: "linear-gradient(135deg, rgba(99,102,241,0.25), rgba(139,92,246,0.3))",
                borderColor: "rgba(167,139,250,0.5)",
                color: "#ede9fe",
                boxShadow: "0 0 16px rgba(139,92,246,0.15)"
              } : undefined}
            >
              {t(cat.labelKey, lang)}
            </button>
          );
        })}
      </section>

      {/* Idle: Best score + XP bar */}
      {status === "idle" && isMounted && (
        <div className="glass" style={{ padding: "18px 20px", marginBottom: 14 }}>
          {profile.bestScore > 0 && profile.bestCategory ? (
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "2.4rem", fontWeight: 800, color: "var(--gold)", lineHeight: 1.1 }}>
                {profile.bestScore}
              </div>
              <div style={{ fontSize: "0.82rem", color: "#64748b", marginTop: 4 }}>
                {t("bestScore", lang)} {t("inCategory", lang)} {t(profile.bestCategory, lang)}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: "center", color: "#475569", fontSize: "0.88rem" }}>
              {t("noBestYet", lang)}
            </div>
          )}

          {/* XP progress */}
          <div style={{ marginTop: 14 }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.72rem", color: "#64748b", marginBottom: 4 }}>
              <span>Lv {profile.level}</span>
              <span>{profile.xp} / {xpNext} XP</span>
            </div>
            <div style={{ height: 4, borderRadius: 100, background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
              <div style={{
                height: "100%",
                width: `${xpPct}%`,
                borderRadius: 100,
                background: "linear-gradient(90deg, var(--accent), #6366f1)",
                transition: "width 0.5s ease"
              }} />
            </div>
          </div>
        </div>
      )}

      {/* Playing area */}
      {(status === "playing" || (status === "idle" && !isMounted)) && (
        <section className="glass" style={{ padding: "14px 14px 16px" }}>
          {/* Score bar */}
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 8,
            fontSize: "0.82rem",
            fontWeight: 600
          }}>
            <span style={{ color: "var(--gold)" }}>{t("score", lang)}: <strong>{score}</strong></span>
            <span style={{ color: "#22d3ee" }}>{t("streak", lang)}: <strong>{streak}</strong></span>
            <span style={{ color: "var(--accent)" }}>Lv <strong>{profile.level}</strong></span>
          </div>

          {/* Timer */}
          {status === "playing" && (
            <div className="timer-track" style={{ marginBottom: 10 }}>
              <div
                className="timer-fill"
                style={{
                  width: `${timerPct}%`,
                  background: timerColor,
                  color: timerColor
                }}
              />
            </div>
          )}

          {/* Question */}
          {question && status === "playing" && (
            <>
              <div className="sil-frame" style={{ marginBottom: 10 }}>
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

              {/* Hint button */}
              <div style={{ textAlign: "center", marginBottom: 10 }}>
                <button
                  className="hint-btn"
                  onClick={() => setHintUsed(true)}
                  disabled={hintUsed}
                >
                  {hintUsed ? t("hintUsed", lang) : t("useHint", lang)}
                </button>
              </div>

              {/* Choices */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                {choices.map((choice) => (
                  <button
                    key={choice}
                    className="choice-btn"
                    onClick={() => handleChoice(choice)}
                  >
                    {choice}
                  </button>
                ))}
              </div>
            </>
          )}
        </section>
      )}

      {/* Game Over Modal */}
      {status === "gameover" && (
        <div className="overlay">
          <div className="modal" style={{ direction: isHe ? "rtl" : "ltr" }}>
            <h2 style={{
              margin: "0 0 4px",
              fontSize: "1.5rem",
              fontWeight: 800,
              background: "linear-gradient(135deg, #fef08a, #f59e0b)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent"
            }}>
              {t("gameOver", lang)}
            </h2>
            <p style={{ margin: "0 0 16px", color: "#64748b", fontSize: "0.85rem" }}>
              {gameOverReason}
            </p>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 18 }}>
              <div className="stat-card">
                <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "var(--gold)" }}>{score}</div>
                <div style={{ fontSize: "0.7rem", color: "#64748b", marginTop: 2 }}>{t("score", lang)}</div>
              </div>
              <div className="stat-card">
                <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "#22d3ee" }}>{streak}</div>
                <div style={{ fontSize: "0.7rem", color: "#64748b", marginTop: 2 }}>{t("streak", lang)}</div>
              </div>
              <div className="stat-card">
                <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "var(--accent)" }}>{profile.bestScore}</div>
                <div style={{ fontSize: "0.7rem", color: "#64748b", marginTop: 2 }}>{t("bestScore", lang)}</div>
              </div>
              <div className="stat-card">
                <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "var(--accent)" }}>{profile.bestStreak}</div>
                <div style={{ fontSize: "0.7rem", color: "#64748b", marginTop: 2 }}>{t("bestStreak", lang)}</div>
              </div>
            </div>

            <button
              className="btn-primary"
              onClick={() => selectedCategory && startRound(selectedCategory)}
            >
              {t("playAgain", lang)}
            </button>
            <button
              className="btn-ghost"
              onClick={() => { setStatus("idle"); setQuestion(null); setSelectedCategory(null); setScore(0); setStreak(0); }}
              style={{ marginTop: 8 }}
            >
              {t("changeCategory", lang)}
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
