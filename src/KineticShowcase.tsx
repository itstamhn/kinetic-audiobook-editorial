import React from "react";
import {
  AbsoluteFill,
  Audio,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { SubtitleCard } from "./SciFiAudioReactive";

export type KineticStyleType = "viral-pop" | "editorial-swiss" | "parchment-gold";

export interface KineticShowcaseProps {
  styleType: KineticStyleType;
  headerTitle?: string;
  totalDurationSeconds: number;
  audioFile?: string;
  subtitles: SubtitleCard[];
}

export const KineticShowcase: React.FC<KineticShowcaseProps> = ({
  styleType = "viral-pop",
  headerTitle = "DOUGLAS ADAMS • THE HITCHHIKER'S GUIDE TO THE GALAXY",
  totalDurationSeconds = 15,
  audioFile,
  subtitles,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const currentTime = frame / fps;

  // Active card
  const activeCard =
    subtitles.find(
      (card) => currentTime >= card.startTime && currentTime <= card.endTime
    ) || subtitles[0];

  const progressPercent = Math.min(100, (currentTime / totalDurationSeconds) * 100);

  // ==========================================
  // STYLE 1: VIRAL POP / SPRING BOUNCE (Shorts/TikTok)
  // ==========================================
  if (styleType === "viral-pop") {
    return (
      <AbsoluteFill
        style={{
          backgroundColor: "#0d0f18",
          fontFamily: "'Syne', 'Montserrat', -apple-system, sans-serif",
          color: "#ffffff",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 80,
        }}
      >
        <style>{`
          @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800;900&family=Space+Grotesk:wght@600;700&display=swap');
          
          .viral-shadow {
            text-shadow: 0 10px 30px rgba(0,0,0,0.8), 0 0 25px rgba(255, 230, 0, 0.4);
          }
        `}</style>

        {/* Ambient Gradient Mesh */}
        <div
          style={{
            position: "absolute",
            width: 700,
            height: 700,
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(255, 0, 128, 0.15) 0%, rgba(0, 240, 255, 0.1) 50%, rgba(0,0,0,0) 70%)",
            filter: "blur(80px)",
            transform: `translate(${Math.sin(frame * 0.05) * 50}px, ${Math.cos(frame * 0.04) * 40}px)`,
          }}
        />

        {/* Top Floating Badge */}
        <div
          style={{
            position: "absolute",
            top: 60,
            padding: "10px 24px",
            borderRadius: 30,
            backgroundColor: "rgba(255, 255, 255, 0.08)",
            backdropFilter: "blur(12px)",
            border: "1px solid rgba(255, 255, 255, 0.15)",
            fontSize: 14,
            fontWeight: 700,
            letterSpacing: 2,
            textTransform: "uppercase",
            color: "#FFE600",
            display: "flex",
            alignItems: "center",
            gap: 10,
          }}
        >
          <span>🔥</span>
          <span>{headerTitle}</span>
        </div>

        {/* Words Container with Snappy Spring Pop */}
        <div
          style={{
            maxWidth: 1400,
            textAlign: "center",
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "center",
            alignItems: "center",
            gap: "18px 24px",
          }}
        >
          {activeCard &&
            activeCard.words.map((w, idx) => {
              const isPast = currentTime > w.end;
              const isCurrent = currentTime >= w.start && currentTime <= w.end;
              
              // Spring physics for current word
              const wordFrame = Math.max(0, (currentTime - w.start) * fps);
              const springScale = spring({
                frame: wordFrame,
                fps,
                config: { damping: 12, stiffness: 220, mass: 0.6 },
              });

              const scale = isCurrent ? 1.0 + springScale * 0.18 : 1.0;
              const rotate = isCurrent ? (idx % 2 === 0 ? -2.5 : 2.5) : 0;

              return (
                <div
                  key={idx}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    transform: `scale(${scale}) rotate(${rotate}deg)`,
                    transition: "transform 0.1s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
                  }}
                >
                  <span
                    className={isCurrent ? "viral-shadow" : ""}
                    style={{
                      fontFamily: "'Syne', sans-serif",
                      fontSize: 76,
                      fontWeight: 900,
                      textTransform: "uppercase",
                      letterSpacing: -1,
                      padding: isCurrent ? "6px 20px" : "4px 0",
                      borderRadius: 14,
                      backgroundColor: isCurrent ? "#FFE600" : "transparent",
                      color: isCurrent
                        ? "#000000"
                        : isPast
                        ? "#ffffff"
                        : "rgba(255, 255, 255, 0.25)",
                      display: "inline-block",
                    }}
                  >
                    {w.text}
                  </span>
                </div>
              );
            })}
        </div>

        {/* Bottom Energy Audio Bar */}
        <div
          style={{
            position: "absolute",
            bottom: 60,
            left: 100,
            right: 100,
            display: "flex",
            flexDirection: "column",
            gap: 12,
          }}
        >
          <div
            style={{
              height: 8,
              borderRadius: 4,
              backgroundColor: "rgba(255, 255, 255, 0.12)",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${progressPercent}%`,
                height: "100%",
                background: "linear-gradient(90deg, #FF0080, #FFE600)",
                boxShadow: "0 0 16px #FFE600",
              }}
            />
          </div>
        </div>

        {audioFile && (
          <Audio
            src={
              audioFile.startsWith("http")
                ? audioFile
                : staticFile(audioFile.replace(/^public\//, ""))
            }
          />
        )}
      </AbsoluteFill>
    );
  }

  // ==========================================
  // STYLE 2: EDITORIAL SWISS / MINIMALIST DOCUMENTARY (Vox/Apple Keynote)
  // ==========================================
  if (styleType === "editorial-swiss") {
    return (
      <AbsoluteFill
        style={{
          backgroundColor: "#121316",
          fontFamily: "'Inter', 'Helvetica Neue', Arial, sans-serif",
          color: "#f3f4f6",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "70px 100px",
        }}
      >
        <style>{`
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800;900&family=JetBrains+Mono:wght@500;700&display=swap');
        `}</style>

        {/* Minimalist Top Grid Header */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            borderBottom: "1px solid rgba(255, 255, 255, 0.15)",
            paddingBottom: 24,
          }}
        >
          <div>
            <div
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 13,
                letterSpacing: 2,
                color: "#9ca3af",
                textTransform: "uppercase",
                marginBottom: 6,
              }}
            >
              AUDIO ARCHIVE // CHAPTER RECORD
            </div>
            <div style={{ fontSize: 24, fontWeight: 800, letterSpacing: -0.5 }}>
              {headerTitle}
            </div>
          </div>

          <div
            style={{
              textAlign: "right",
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 16,
              fontWeight: 700,
              color: "#38bdf8",
            }}
          >
            {Math.floor(currentTime / 60)
              .toString()
              .padStart(2, "0")}
            :{(currentTime % 60).toFixed(1).padStart(4, "0")}
          </div>
        </div>

        {/* Center Editorial Typography with Smooth Masking Reveal */}
        <div style={{ maxWidth: 1500, margin: "auto 0" }}>
          <div
            style={{
              fontSize: 68,
              fontWeight: 800,
              lineHeight: 1.32,
              letterSpacing: -1.5,
            }}
          >
            {activeCard &&
              activeCard.words.map((w, idx) => {
                const isPast = currentTime > w.end;
                const isCurrent = currentTime >= w.start && currentTime <= w.end;

                let opacity = 0.2;
                let color = "#ffffff";
                let underline = "none";

                if (isPast) {
                  opacity = 0.9;
                } else if (isCurrent) {
                  opacity = 1.0;
                  color = "#38bdf8"; // Electric sky blue
                }

                return (
                  <span
                    key={idx}
                    style={{
                      display: "inline-block",
                      opacity,
                      color,
                      marginRight: 16,
                      transition: "opacity 0.15s ease, color 0.15s ease",
                      position: "relative",
                    }}
                  >
                    {w.text}
                    {isCurrent && (
                      <span
                        style={{
                          position: "absolute",
                          left: 0,
                          bottom: -4,
                          width: "100%",
                          height: 4,
                          backgroundColor: "#38bdf8",
                          borderRadius: 2,
                        }}
                      />
                    )}
                  </span>
                );
              })}
          </div>
        </div>

        {/* Bottom Minimalist Ruled Timeline */}
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <div
            style={{
              width: "100%",
              height: 2,
              backgroundColor: "rgba(255, 255, 255, 0.15)",
              position: "relative",
            }}
          >
            <div
              style={{
                width: `${progressPercent}%`,
                height: "100%",
                backgroundColor: "#38bdf8",
              }}
            />
          </div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 12,
              color: "#6b7280",
            }}
          >
            <span>NARRATION: STEPHEN FRY</span>
            <span>FORMAT: 1080P 60FPS SWISS EDITION</span>
          </div>
        </div>

        {audioFile && (
          <Audio
            src={
              audioFile.startsWith("http")
                ? audioFile
                : staticFile(audioFile.replace(/^public\//, ""))
            }
          />
        )}
      </AbsoluteFill>
    );
  }

  // ==========================================
  // STYLE 3: PARCHMENT & GOLD FOIL LUXURY (Folio Society Antique Edition)
  // ==========================================
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#161311", // Deep warm leather noir
        fontFamily: "'Cinzel', 'Playfair Display', Georgia, serif",
        color: "#f5ece1",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: 90,
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;900&family=Playfair+Display:ital,wght@0,500;0,700;1,400;1,600&family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap');
        
        .gold-shimmer {
          background: linear-gradient(135deg, #ffd700 0%, #fff2a3 50%, #d4af37 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          filter: drop-shadow(0 0 16px rgba(255, 215, 0, 0.45));
        }
      `}</style>

      {/* Antique Vignette Frame */}
      <div
        style={{
          position: "absolute",
          inset: 35,
          border: "1px solid rgba(212, 175, 55, 0.3)",
          pointerEvents: "none",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 42,
          border: "1px solid rgba(212, 175, 55, 0.15)",
          pointerEvents: "none",
        }}
      />

      {/* Floating Gold Embers */}
      {Array.from({ length: 25 }).map((_, i) => {
        const x = (i * 187) % width;
        const y = ((i * 311 + frame * 0.4) % height);
        const opacity = 0.2 + 0.5 * Math.sin(frame * 0.05 + i);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: 3,
              height: 3,
              borderRadius: "50%",
              backgroundColor: "#d4af37",
              opacity,
              boxShadow: "0 0 8px #ffd700",
              pointerEvents: "none",
            }}
          />
        );
      })}

      {/* Top Gold Book Header */}
      <div
        style={{
          position: "absolute",
          top: 65,
          fontFamily: "'Cinzel', serif",
          fontSize: 15,
          fontWeight: 700,
          letterSpacing: 5,
          color: "rgba(212, 175, 55, 0.8)",
          textTransform: "uppercase",
          borderBottom: "1px solid rgba(212, 175, 55, 0.25)",
          paddingBottom: 10,
        }}
      >
        ✦ {headerTitle} ✦
      </div>

      {/* Luxury Classical Typography */}
      <div
        style={{
          maxWidth: 1350,
          textAlign: "center",
          fontFamily: "'Playfair Display', Georgia, serif",
          fontSize: 66,
          lineHeight: 1.45,
          fontStyle: "italic",
        }}
      >
        {activeCard &&
          activeCard.words.map((w, idx) => {
            const isPast = currentTime > w.end;
            const isCurrent = currentTime >= w.start && currentTime <= w.end;

            if (isCurrent) {
              return (
                <span
                  key={idx}
                  className="gold-shimmer"
                  style={{
                    display: "inline-block",
                    margin: "0 10px",
                    fontWeight: 700,
                    transform: "scale(1.06)",
                    transition: "transform 0.15s ease",
                  }}
                >
                  {w.text}
                </span>
              );
            }

            return (
              <span
                key={idx}
                style={{
                  display: "inline-block",
                  margin: "0 10px",
                  color: isPast ? "#f5ece1" : "rgba(245, 236, 225, 0.25)",
                  fontWeight: isPast ? 600 : 400,
                  transition: "color 0.15s ease",
                }}
              >
                {w.text}
              </span>
            );
          })}
      </div>

      {/* Bottom Gold Filigree & Scrubber */}
      <div
        style={{
          position: "absolute",
          bottom: 60,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 12,
          width: 600,
        }}
      >
        <div
          style={{
            width: "100%",
            height: 2,
            backgroundColor: "rgba(212, 175, 55, 0.2)",
            position: "relative",
          }}
        >
          <div
            style={{
              width: `${progressPercent}%`,
              height: "100%",
              backgroundColor: "#d4af37",
              boxShadow: "0 0 10px #ffd700",
            }}
          />
        </div>
        <div
          style={{
            fontFamily: "'Cinzel', serif",
            fontSize: 12,
            letterSpacing: 3,
            color: "rgba(212, 175, 55, 0.6)",
          }}
        >
          FOLIO SOCIETY EDITION
        </div>
      </div>

      {audioFile && (
        <Audio
          src={
            audioFile.startsWith("http")
              ? audioFile
              : staticFile(audioFile.replace(/^public\//, ""))
          }
        />
      )}
    </AbsoluteFill>
  );
};
