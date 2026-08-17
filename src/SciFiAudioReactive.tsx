import React from "react";
import {
  AbsoluteFill,
  Audio,
  staticFile,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export interface WordInfo {
  text: string;
  start: number;
  end: number;
}

export interface SubtitleCard {
  id: number;
  startTime: number;
  endTime: number;
  fullText: string;
  words: WordInfo[];
}

export interface SciFiProps {
  headerTitle?: string;
  totalDurationSeconds: number;
  audioFile: string;
  subtitles: SubtitleCard[];
  themeColor?: string;
  accentColor?: string;
}

export const SciFiAudioReactive: React.FC<SciFiProps> = ({
  headerTitle = "THE HITCHHIKER'S GUIDE TO THE GALAXY • SUB-ETHA TERMINAL",
  totalDurationSeconds = 15,
  audioFile,
  subtitles,
  themeColor = "#00f0ff", // Cyan neon
  accentColor = "#ffd700", // Gold star
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const currentTime = frame / fps;

  // 1. Locate current subtitle card
  const activeCard =
    subtitles.find(
      (card) => currentTime >= card.startTime && currentTime <= card.endTime
    ) ||
    subtitles[0];

  // 2. Compute audio frequency visualizer bars (48 bars)
  const numBars = 52;
  const bars = Array.from({ length: numBars }).map((_, i) => {
    // Generate organic speech frequency modulation based on frame, index and time
    const seed = i * 1.37;
    const wave1 = Math.sin(frame * 0.22 + seed * 0.8);
    const wave2 = Math.cos(frame * 0.15 - seed * 1.2);
    const wave3 = Math.sin(frame * 0.45 + i * 2.1);
    
    // Voice activity envelope (higher when words are spoken)
    const isSpeaking = activeCard && activeCard.words.some(
      (w) => currentTime >= w.start && currentTime <= w.end
    );
    const speechAmp = isSpeaking ? 1.0 : 0.25;

    // Bass bias in the middle, highs on the edges
    const centerDist = Math.abs(i - numBars / 2) / (numBars / 2);
    const bellCurve = Math.exp(-centerDist * centerDist * 2.5);

    const rawHeight = (Math.abs(wave1 * 0.5 + wave2 * 0.3 + wave3 * 0.2) * bellCurve + 0.08) * speechAmp;
    const barHeight = Math.max(8, rawHeight * 110);

    return {
      id: i,
      height: barHeight,
      hue: (i / numBars) * 45 + 175, // Cyan to electric blue
    };
  });

  // 3. Starfield particles (30 stars)
  const stars = Array.from({ length: 40 }).map((_, i) => {
    const startX = ((i * 137.5) % width);
    const startY = ((i * 223.7) % height);
    const speed = 0.2 + (i % 5) * 0.15;
    const size = 1.5 + (i % 3) * 1.2;
    const currentY = (startY + frame * speed) % height;
    const twinkle = 0.3 + 0.7 * Math.abs(Math.sin(frame * 0.08 + i));

    return {
      id: i,
      x: startX,
      y: currentY,
      size,
      opacity: twinkle,
    };
  });

  // Progress percentage
  const progressPercent = Math.min(100, (currentTime / totalDurationSeconds) * 100);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#06080e",
        fontFamily: "'Space Grotesk', 'Playfair Display', Georgia, serif",
        color: "#ffffff",
        overflow: "hidden",
      }}
    >
      {/* 1. Google Fonts imports */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;0,900;1,400;1,700&family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;600;800&display=swap');
        
        .crt-glow {
          text-shadow: 0 0 18px rgba(0, 240, 255, 0.4), 0 0 40px rgba(0, 240, 255, 0.15);
        }
        .gold-glow {
          text-shadow: 0 0 20px rgba(255, 215, 0, 0.6), 0 0 45px rgba(255, 215, 0, 0.25);
        }
      `}</style>

      {/* 2. Starfield & Nebula Background */}
      <AbsoluteFill style={{ pointerEvents: "none" }}>
        {/* Radial Nebula Glow */}
        <div
          style={{
            position: "absolute",
            top: "20%",
            left: "30%",
            width: 800,
            height: 600,
            background: "radial-gradient(circle, rgba(0, 150, 255, 0.08) 0%, rgba(0,0,0,0) 70%)",
            filter: "blur(60px)",
          }}
        />
        <div
          style={{
            position: "absolute",
            bottom: "10%",
            right: "20%",
            width: 600,
            height: 500,
            background: "radial-gradient(circle, rgba(147, 51, 234, 0.07) 0%, rgba(0,0,0,0) 70%)",
            filter: "blur(50px)",
          }}
        />

        {/* Stars */}
        {stars.map((s) => (
          <div
            key={s.id}
            style={{
              position: "absolute",
              left: s.x,
              top: s.y,
              width: s.size,
              height: s.size,
              borderRadius: "50%",
              backgroundColor: "#ffffff",
              opacity: s.opacity,
              boxShadow: s.size > 2 ? "0 0 6px rgba(255,255,255,0.8)" : "none",
            }}
          />
        ))}
      </AbsoluteFill>

      {/* 3. Top Sci-Fi Telemetry HUD */}
      <div
        style={{
          position: "absolute",
          top: 48,
          left: 72,
          right: 72,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 13,
          letterSpacing: 2.5,
          color: "rgba(0, 240, 255, 0.75)",
          borderBottom: "1px solid rgba(0, 240, 255, 0.18)",
          paddingBottom: 18,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div
            style={{
              width: 9,
              height: 9,
              borderRadius: "50%",
              backgroundColor: "#00f0ff",
              boxShadow: "0 0 10px #00f0ff",
              animation: "pulse 1.5s infinite",
            }}
          />
          <span style={{ fontWeight: 700 }}>SUB-ETHA LOG // 94.2 MHz</span>
          <span style={{ color: "rgba(255,255,255,0.3)" }}>|</span>
          <span style={{ color: "rgba(255,255,255,0.7)" }}>SEC ZZ9 PLURAL Z ALPHA</span>
        </div>

        <div style={{ display: "flex", gap: 24, color: "rgba(255,255,255,0.55)" }}>
          <span>PROBABILITY: <strong style={{ color: "#ffd700" }}>2^276,709:1</strong></span>
          <span>STABILITY: <strong style={{ color: "#00f0ff" }}>99.8%</strong></span>
          <span>REC: <strong style={{ color: "#ff4444" }}>● LIVE</strong></span>
        </div>
      </div>

      {/* 4. Center Kinetic Typography Container */}
      <div
        style={{
          position: "absolute",
          top: 140,
          bottom: 220,
          left: 120,
          right: 120,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          textAlign: "center",
        }}
      >
        {/* Book Header Tag */}
        <div
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 14,
            letterSpacing: 4,
            textTransform: "uppercase",
            color: "rgba(255, 215, 0, 0.8)",
            marginBottom: 36,
            display: "flex",
            alignItems: "center",
            gap: 12,
          }}
        >
          <span style={{ opacity: 0.5 }}>[</span>
          <span>{headerTitle}</span>
          <span style={{ opacity: 0.5 }}>]</span>
        </div>

        {/* Spoken Subtitle Text with Word-by-Word Active Karaoke Highlighting */}
        <div
          style={{
            fontFamily: "'Playfair Display', Georgia, serif",
            fontSize: 66,
            fontWeight: 700,
            lineHeight: 1.36,
            maxWidth: 1450,
            transition: "all 0.15s ease-out",
          }}
        >
          {activeCard &&
            activeCard.words.map((w, idx) => {
              const isPast = currentTime > w.end;
              const isCurrent = currentTime >= w.start && currentTime <= w.end;
              const isFuture = currentTime < w.start;

              let wordColor = "rgba(255, 255, 255, 0.22)"; // Future dimmed
              let fontWeight = 500;
              let transform = "scale(1)";
              let filter = "none";
              let className = "";

              if (isPast) {
                wordColor = "rgba(255, 255, 255, 0.88)";
                fontWeight = 600;
              } else if (isCurrent) {
                wordColor = "#ffd700"; // Active glowing gold
                fontWeight = 900;
                transform = "scale(1.06)";
                className = "gold-glow";
              }

              return (
                <span
                  key={idx}
                  className={className}
                  style={{
                    color: wordColor,
                    fontWeight,
                    display: "inline-block",
                    margin: "0 9px",
                    transform,
                    transition: "color 0.12s ease, transform 0.12s ease",
                  }}
                >
                  {w.text}
                </span>
              );
            })}
        </div>
      </div>

      {/* 5. Bottom Audio-Reactive Visualizer & Frequency Oscilloscope */}
      <div
        style={{
          position: "absolute",
          bottom: 40,
          left: 72,
          right: 72,
          display: "flex",
          flexDirection: "column",
          gap: 14,
        }}
      >
        {/* Frequency Spectrum Bars */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "flex-end",
            height: 90,
            gap: 6,
            paddingBottom: 8,
          }}
        >
          {bars.map((b) => (
            <div
              key={b.id}
              style={{
                width: 7,
                height: `${b.height}px`,
                background: `linear-gradient(to top, rgba(0, 240, 255, 0.2), #00f0ff 70%, #ffffff)`,
                borderRadius: "3px 3px 1px 1px",
                boxShadow: b.height > 40 ? "0 0 10px rgba(0, 240, 255, 0.7)" : "none",
                transition: "height 0.05s ease",
              }}
            />
          ))}
        </div>

        {/* Progress Bar with Cyan Glow */}
        <div
          style={{
            width: "100%",
            height: 4,
            backgroundColor: "rgba(255, 255, 255, 0.1)",
            borderRadius: 2,
            overflow: "hidden",
            position: "relative",
          }}
        >
          <div
            style={{
              width: `${progressPercent}%`,
              height: "100%",
              background: "linear-gradient(90deg, #00f0ff, #ffd700)",
              boxShadow: "0 0 12px #00f0ff",
            }}
          />
        </div>

        {/* Bottom Timecode HUD */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 12,
            letterSpacing: 2,
            color: "rgba(255, 255, 255, 0.45)",
          }}
        >
          <span>AUDIOSTREAM: STEPHEN FRY // VOCAL FREQ 120Hz-4kHz</span>
          <span style={{ color: "rgba(0, 240, 255, 0.9)", fontWeight: 700 }}>
            {Math.floor(currentTime / 60)
              .toString()
              .padStart(2, "0")}
            :{(currentTime % 60).toFixed(2).padStart(5, "0")} /{" "}
            {Math.floor(totalDurationSeconds / 60)
              .toString()
              .padStart(2, "0")}
            :{(totalDurationSeconds % 60).toFixed(0).padStart(2, "0")}
          </span>
        </div>
      </div>

      {/* Audio Playback */}
      {audioFile && (
        <Audio
          src={
            audioFile.startsWith("http") || audioFile.startsWith("data:")
              ? audioFile
              : staticFile(audioFile.replace(/^public\//, ""))
          }
        />
      )}
    </AbsoluteFill>
  );
};
