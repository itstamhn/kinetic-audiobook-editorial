import React from "react";
import {
  AbsoluteFill,
  Audio,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { SubtitleCard } from "./SciFiAudioReactive";

export interface MinimalistProps {
  theme?: "light-paper" | "dark-charcoal";
  mode?: "continuous-ink" | "crisp-word";
  headerTitle?: string;
  totalDurationSeconds: number;
  audioFile?: string;
  subtitles: SubtitleCard[];
}

export const MinimalistKinetic: React.FC<MinimalistProps> = ({
  theme = "light-paper",
  mode = "continuous-ink",
  headerTitle = "Douglas Adams • The Hitchhiker's Guide to the Galaxy",
  totalDurationSeconds = 15,
  audioFile,
  subtitles,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  // Active subtitle card
  const activeCard =
    subtitles.find(
      (card) => currentTime >= card.startTime && currentTime <= card.endTime
    ) || subtitles[0];

  const isLight = theme === "light-paper";

  // Color tokens
  const bgColor = isLight ? "#FBF9F5" : "#131313";
  const solidInkColor = isLight ? "#111111" : "#FFFFFF";
  const ghostGreyColor = isLight ? "#D2CDC4" : "#3C3C3C";
  const headerColor = isLight ? "#8C877D" : "#6E6E6E";
  const progressBg = isLight ? "rgba(0, 0, 0, 0.06)" : "rgba(255, 255, 255, 0.08)";
  const progressFill = isLight ? "#111111" : "#FFFFFF";

  const progressPercent = Math.min(100, (currentTime / totalDurationSeconds) * 100);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: bgColor,
        fontFamily: "'Newsreader', 'EB Garamond', 'Charter', Georgia, serif",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        padding: "85px 150px",
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400&family=Inter:wght@400;500;600&display=swap');
      `}</style>

      {/* 1. Chapter Header */}
      <div
        style={{
          fontFamily: "'Inter', sans-serif",
          fontSize: 13,
          letterSpacing: 2.5,
          textTransform: "uppercase",
          color: headerColor,
          fontWeight: 600,
          opacity: 0.85,
        }}
      >
        {headerTitle}
      </div>

      {/* 2. Main Reading Text - Firm, Smooth, Grounded Typography */}
      <div
        style={{
          maxWidth: 1420,
          margin: "auto 0",
          fontSize: 68,
          lineHeight: 1.44,
          letterSpacing: -0.4,
          fontWeight: 400,
        }}
      >
        {activeCard &&
          activeCard.words.map((w, idx) => {
            const isFinished = currentTime >= w.end;
            const isUpcoming = currentTime < w.start;
            const isCurrentlySpeaking = currentTime >= w.start && currentTime < w.end;

            // Continuous Syllabic Ink Flow (0% -> 100% smooth gradient fill across the word)
            if (mode === "continuous-ink") {
              if (isFinished) {
                return (
                  <span
                    key={idx}
                    style={{
                      color: solidInkColor,
                      fontWeight: 500,
                      marginRight: 18,
                      display: "inline-block",
                    }}
                  >
                    {w.text}
                  </span>
                );
              }

              if (isUpcoming) {
                return (
                  <span
                    key={idx}
                    style={{
                      color: ghostGreyColor,
                      fontWeight: 400,
                      marginRight: 18,
                      display: "inline-block",
                    }}
                  >
                    {w.text}
                  </span>
                );
              }

              // Active speaking: Sub-frame gradient fill strictly locked to voice duration
              const fillPct = interpolate(
                currentTime,
                [w.start, w.end],
                [0, 100],
                { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
              );

              return (
                <span
                  key={idx}
                  style={{
                    background: `linear-gradient(90deg, ${solidInkColor} ${fillPct}%, ${ghostGreyColor} ${fillPct}%)`,
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                    fontWeight: 600,
                    marginRight: 18,
                    display: "inline-block",
                  }}
                >
                  {w.text}
                </span>
              );
            }

            // Crisp-word mode: Instant, solid, firm switch without any fade lag
            const color = isFinished || isCurrentlySpeaking ? solidInkColor : ghostGreyColor;
            const fontWeight = isCurrentlySpeaking ? 600 : isFinished ? 500 : 400;

            return (
              <span
                key={idx}
                style={{
                  color,
                  fontWeight,
                  marginRight: 18,
                  display: "inline-block",
                }}
              >
                {w.text}
              </span>
            );
          })}
      </div>

      {/* 3. Hairline Progress Bar */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 12,
        }}
      >
        <div
          style={{
            width: "100%",
            height: 2,
            backgroundColor: progressBg,
            position: "relative",
          }}
        >
          <div
            style={{
              width: `${progressPercent}%`,
              height: "100%",
              backgroundColor: progressFill,
            }}
          />
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            fontFamily: "'Inter', sans-serif",
            fontSize: 12,
            color: headerColor,
            letterSpacing: 1.5,
            fontWeight: 500,
          }}
        >
          <span>PROLOGUE // RUNNING NARRATION</span>
          <span>
            {Math.floor(currentTime / 60)
              .toString()
              .padStart(2, "0")}
            :{(currentTime % 60).toFixed(0).padStart(2, "0")} /{" "}
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
            audioFile.startsWith("http")
              ? audioFile
              : staticFile(audioFile.replace(/^public\//, ""))
          }
        />
      )}
    </AbsoluteFill>
  );
};
