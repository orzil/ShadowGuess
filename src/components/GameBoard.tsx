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

  return (
    <main style={{ maxWidth: 540, margin: "0 auto", padding: "12px 12px 16px", direction: isHe ? "rtl" : "ltr" }}>
      <header style={{ textAlign: "center", marginBottom: 12, position: "relative" }}>
        <button
          onClick={toggleLang}
          style={{
            position: "absolute",
            top: 0,
            [isHe ? "left" : "right"]: 0,
            border: "1px solid rgba(148,163,184,0.3)",
            borderRadius: 8,
            padding: "4px 10px",
            fontSize: "0.75rem",
            background: "rgba(30,41,59,0.8)",
            color: "#94a3b8",
            cursor: "pointer"
          }}
        >
          {isHe ? "EN" : "HE"}
        </button>
        <h1 style={{ margin: 0, fontSize: "2.8rem", fontWeight: 800, letterSpacing: "-0.02em", color: "#fef08a", textShadow: "0 2px 20px rgba(245, 158, 11, 0.5), 0 0 40px rgba(245, 158, 11, 0.2)" }}>
          {t("title", lang)}
        </h1>
        <p style={{ margin: "8px 0 0", fontSize: "1.05rem", fontWeight: 500, color: "#bfdbfe", lineHeight: 1.5, whiteSpace: "pre-line" }}>
          {t("subtitle", lang)}
        </p>
      </header>

      <section style={{ display: "flex", gap: 6, flexWrap: "wrap", justifyContent: "center", marginBottom: 10 }}>
        {categoryCards.map((cat) => {
          const unlocked = !cat.comingSoon && isMounted && profile.unlockedCategories.includes(cat.id);
          const disabled = cat.comingSoon || !unlocked;
          return (
            <button
              key={cat.id}
              disabled={disabled}
              onClick={() => unlocked && startRound(cat.id as CategoryId)}
              style={{
                border: cat.comingSoon ? "1px solid #334155" : "1px solid #60a5fa",
                borderRadius: 10,
                padding: "6px 14px",
                fontSize: "0.85rem",
                background: unlocked
                  ? "linear-gradient(135deg, rgba(14,165,233,0.28), rgba(99,102,241,0.35))"
                  : "rgba(15, 23, 42, 0.5)",
                color: cat.comingSoon ? "#475569" : unlocked ? "#fef9c3" : "#94a3b8",
                cursor: disabled ? "not-allowed" : "pointer",
                textDecoration: cat.comingSoon ? "line-through" : "none"
              }}
            >
              {t(cat.labelKey, lang)}
            </button>
          );
        })}
      </section>

      {status === "idle" && isMounted && (
        <div style={{ textAlign: "center", margin: "16px 0", padding: "14px", borderRadius: 12, background: "rgba(30,41,59,0.6)", border: "1px solid rgba(96,165,250,0.2)" }}>
          {profile.bestScore > 0 && profile.bestCategory ? (
            <div>
              <div style={{ fontSize: "1.8rem", fontWeight: 700, color: "#fef08a" }}>{profile.bestScore}</div>
              <div style={{ fontSize: "0.8rem", color: "#94a3b8" }}>
                {t("bestScore", lang)} {t("inCategory", lang)} {t(profile.bestCategory, lang)}
              </div>
            </div>
          ) : (
            <div style={{ color: "#64748b", fontSize: "0.85rem" }}>{t("noBestYet", lang)}</div>
          )}
        </div>
      )}

      {(status === "playing" || (status === "idle" && !isMounted)) && (
        <section
          style={{
            border: "1px solid rgba(96, 165, 250, 0.3)",
            borderRadius: 14,
            padding: "10px 10px 12px",
            background: "linear-gradient(170deg, rgba(30,41,59,0.9), rgba(30,58,138,0.4))"
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6, fontSize: "0.8rem", color: "#fde68a" }}>
            <span>{t("score", lang)}: <strong>{score}</strong></span>
            <span>{t("streak", lang)}: <strong>{streak}</strong></span>
            <span>Lv <strong>{profile.level}</strong></span>
          </div>

          {status === "playing" && (
            <div style={{ height: 4, borderRadius: 2, background: "rgba(255,255,255,0.1)", marginBottom: 8, overflow: "hidden" }}>
              <div style={{
                height: "100%",
                width: `${timerPct}%`,
                background: timerColor,
                borderRadius: 2,
                transition: "width 1s linear, background 0.3s"
              }} />
            </div>
          )}

          {question && status === "playing" && (
            <>
              <div
                style={{
                  position: "relative",
                  width: "100%",
                  aspectRatio: "4 / 3",
                  borderRadius: 12,
                  overflow: "hidden",
                  border: "1px solid rgba(56, 189, 248, 0.4)",
                  marginBottom: 8,
                  background: "linear-gradient(135deg, #1e3a5f 0%, #374151 50%, #1e293b 100%)"
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

              <div style={{ textAlign: "center", marginBottom: 8 }}>
                <button
                  onClick={() => setHintUsed(true)}
                  disabled={hintUsed}
                  style={{
                    border: "1px solid #22d3ee",
                    borderRadius: 8,
                    padding: "4px 14px",
                    fontSize: "0.8rem",
                    background: hintUsed
                      ? "rgba(15,23,42,0.7)"
                      : "linear-gradient(135deg, rgba(34,211,238,0.3), rgba(99,102,241,0.3))",
                    color: hintUsed ? "#64748b" : "#f0f9ff"
                  }}
                >
                  {hintUsed ? t("hintUsed", lang) : t("useHint", lang)}
                </button>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
                {choices.map((choice) => (
                  <button
                    key={choice}
                    onClick={() => handleChoice(choice)}
                    style={{
                      border: "1px solid rgba(167, 139, 250, 0.5)",
                      borderRadius: 10,
                      padding: "10px 8px",
                      textAlign: "center",
                      fontSize: "0.85rem",
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
      )}

      {status === "gameover" && (
        <div className="overlay">
          <div className="modal" style={{ direction: isHe ? "rtl" : "ltr" }}>
            <h2 style={{ margin: "0 0 4px", color: "#fef08a", fontSize: "1.3rem" }}>{t("gameOver", lang)}</h2>
            <p style={{ margin: "0 0 14px", color: "#94a3b8", fontSize: "0.85rem" }}>{gameOverReason}</p>

            <div style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: 10,
              marginBottom: 16,
              textAlign: "center"
            }}>
              <div style={{ background: "rgba(255,255,255,0.05)", borderRadius: 10, padding: "10px 6px" }}>
                <div style={{ fontSize: "1.4rem", fontWeight: 700, color: "#fef08a" }}>{score}</div>
                <div style={{ fontSize: "0.7rem", color: "#94a3b8" }}>{t("score", lang)}</div>
              </div>
              <div style={{ background: "rgba(255,255,255,0.05)", borderRadius: 10, padding: "10px 6px" }}>
                <div style={{ fontSize: "1.4rem", fontWeight: 700, color: "#fef08a" }}>{streak}</div>
                <div style={{ fontSize: "0.7rem", color: "#94a3b8" }}>{t("streak", lang)}</div>
              </div>
              <div style={{ background: "rgba(255,255,255,0.05)", borderRadius: 10, padding: "10px 6px" }}>
                <div style={{ fontSize: "1.4rem", fontWeight: 700, color: "#a78bfa" }}>{profile.bestScore}</div>
                <div style={{ fontSize: "0.7rem", color: "#94a3b8" }}>{t("bestScore", lang)}</div>
              </div>
              <div style={{ background: "rgba(255,255,255,0.05)", borderRadius: 10, padding: "10px 6px" }}>
                <div style={{ fontSize: "1.4rem", fontWeight: 700, color: "#a78bfa" }}>{profile.bestStreak}</div>
                <div style={{ fontSize: "0.7rem", color: "#94a3b8" }}>{t("bestStreak", lang)}</div>
              </div>
            </div>

            <button
              onClick={() => selectedCategory && startRound(selectedCategory)}
              style={{
                width: "100%",
                border: "none",
                borderRadius: 10,
                padding: "11px 20px",
                fontSize: "0.95rem",
                fontWeight: 600,
                background: "linear-gradient(135deg, #f59e0b, #ef4444)",
                color: "#fff",
                cursor: "pointer"
              }}
            >
              {t("playAgain", lang)}
            </button>
            <button
              onClick={() => { setStatus("idle"); setQuestion(null); setSelectedCategory(null); setScore(0); setStreak(0); }}
              style={{
                width: "100%",
                border: "1px solid rgba(148,163,184,0.3)",
                borderRadius: 10,
                padding: "9px 20px",
                marginTop: 6,
                fontSize: "0.8rem",
                background: "transparent",
                color: "#94a3b8",
                cursor: "pointer"
              }}
            >
              {t("changeCategory", lang)}
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
