import React from "react";
import {
  AbsoluteFill,
  Audio,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/Literata";

// Preload Literata with explicit Vietnamese subset and weights to eliminate any glittering
const { fontFamily } = loadFont("normal", {
  weights: ["400", "500", "600"],
  subsets: ["latin", "vietnamese"],
});

export interface WordInfo {
  text: string;
  start: number;
  end: number;
  vn?: string; // Vietnamese interlinear gloss translation
}

export interface EditorialPage {
  id: number;
  startTime: number;
  endTime: number;
  words: WordInfo[];
}

export interface EditorialPageReaderProps {
  totalDurationSeconds: number;
  audioFile?: string;
  pages: EditorialPage[];
}

export const EditorialPageReader: React.FC<EditorialPageReaderProps> = ({
  totalDurationSeconds = 41,
  audioFile,
  pages,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  const activePageIndex = pages.findIndex(
    (p) => currentTime >= p.startTime && currentTime < p.endTime
  );

  const currentPageIndex =
    activePageIndex !== -1 ? activePageIndex : pages.length - 1;
  const activePage = pages[currentPageIndex] || pages[0];

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#faf9f6", // Calm luxury editorial off-white paper
        fontFamily,
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        padding: "90px 140px",
      }}
    >
      {/* Multi-Line Calm Editorial Interlinear Canvas */}
      <div
        style={{
          width: "100%",
          maxWidth: 1640,
          display: "flex",
          flexWrap: "wrap",
          columnGap: "20px",
          rowGap: "22px",
          alignItems: "flex-end",
        }}
      >
        {activePage &&
          activePage.words.map((w, idx) => {
            const isSpoken = currentTime >= w.start;

            return (
              <div
                key={`${activePage.id}-${idx}`}
                style={{
                  display: "inline-flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "flex-end",
                  verticalAlign: "bottom",
                }}
              >
                {/* Vietnamese Interlinear Gloss Above */}
                <span
                  style={{
                    fontSize: 28,
                    lineHeight: "32px",
                    height: 32,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: isSpoken ? "#0f766e" : "#94a3b8", // elegant vintage teal when spoken
                    fontWeight: 500,
                    letterSpacing: 0,
                    whiteSpace: "nowrap",
                    visibility: w.vn ? "visible" : "hidden",
                    marginBottom: 6,
                    userSelect: "none",
                  }}
                >
                  {w.vn || "\u00A0"}
                </span>

                {/* English Base Word */}
                <span
                  style={{
                    fontSize: 82,
                    lineHeight: "1.0em",
                    color: isSpoken ? "#000000" : "#b8b5ad",
                    fontWeight: 400,
                    letterSpacing: -0.5,
                    whiteSpace: "nowrap",
                  }}
                >
                  {w.text}
                </span>
              </div>
            );
          })}
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
