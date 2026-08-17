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
  vn?: string; // Vietnamese gloss translation
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
          fontSize: 84,
          fontWeight: 400,
          lineHeight: 1.35,
          letterSpacing: -0.5,
          textAlign: "left",
          display: "flex",
          flexWrap: "wrap",
          columnGap: "18px",
          rowGap: "8px",
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
                  display: "inline-block",
                  color: isSpoken ? "#000000" : "#b8b5ad",
                  fontWeight: 400,
                }}
              >
                {w.text}
                {w.vn && (
                  <span
                    style={{
                      fontSize: "0.46em",
                      color: isSpoken ? "#0f766e" : "#94a3b8", // elegant vintage teal when active
                      fontStyle: "italic",
                      fontWeight: 400,
                      marginLeft: "6px",
                      letterSpacing: "0px",
                    }}
                  >
                    ({w.vn})
                  </span>
                )}
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
