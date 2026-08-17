import React from "react";
import {
  AbsoluteFill,
  Audio,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/Literata";

// Block Remotion rendering until Literata is 100% loaded and active
const { fontFamily } = loadFont("normal", {
  weights: ["400", "500"],
});

export interface WordInfo {
  text: string;
  start: number;
  end: number;
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

  // Find active page by time interval [startTime, endTime)
  // Clean, instantaneous cut with zero opacity fading or in-between flickering
  const activePageIndex = pages.findIndex(
    (p) => currentTime >= p.startTime && currentTime < p.endTime
  );

  const currentPageIndex = activePageIndex !== -1 ? activePageIndex : pages.length - 1;
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

      {/* Multi-Line Calm Editorial Typography Canvas */}
      <div
        style={{
          width: "100%",
          maxWidth: 1640,
          fontSize: 98,
          fontWeight: 400, // Strictly unchanged font weight to ensure zero letter jitter
          lineHeight: 1.2,
          letterSpacing: -1.2,
          textAlign: "left",
          display: "flex",
          flexWrap: "wrap",
          columnGap: "22px",
          rowGap: "6px",
          alignItems: "baseline",
        }}
      >
        {activePage &&
          activePage.words.map((w, idx) => {
            const isSpoken = currentTime >= w.start;

            return (
              <span
                key={`${activePage.id}-${idx}`}
                style={{
                  color: isSpoken ? "#000000" : "#b8b5ad",
                  fontWeight: 400,
                  display: "inline-block",
                }}
              >
                {w.text}
              </span>
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
