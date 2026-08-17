import React, { useMemo } from 'react';
import {
  AbsoluteFill,
  Audio,
  Easing,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import fallbackSubtitles from './subtitles.json';

export interface WordTiming {
  text: string;
  start: number;
  end: number;
}

export interface SubtitlePage {
  id: number;
  startTime: number;
  endTime: number;
  fullText: string;
  words: WordTiming[];
}

export interface KineticVideoProps {
  primaryColor?: string;
  mutedColor?: string;
  backgroundColor?: string;
  fontFamily?: string;
  mode?: 'cumulative' | 'spotlight';
  headerTitle?: string;
  totalDurationSeconds?: number;
  audioFile?: string;
  subtitles?: SubtitlePage[];
}

// Color interpolation helper
const hexToRgb = (hex: string): [number, number, number] => {
  const cleanHex = hex.replace('#', '');
  if (cleanHex.length === 3) {
    return [
      parseInt(cleanHex[0] + cleanHex[0], 16),
      parseInt(cleanHex[1] + cleanHex[1], 16),
      parseInt(cleanHex[2] + cleanHex[2], 16),
    ];
  }
  return [
    parseInt(cleanHex.substring(0, 2), 16),
    parseInt(cleanHex.substring(2, 4), 16),
    parseInt(cleanHex.substring(4, 6), 16),
  ];
};

const lerpColor = (c1: [number, number, number], c2: [number, number, number], t: number): string => {
  const clampedT = Math.max(0, Math.min(1, t));
  const r = Math.round(c1[0] + (c2[0] - c1[0]) * clampedT);
  const g = Math.round(c1[1] + (c2[1] - c1[1]) * clampedT);
  const b = Math.round(c1[2] + (c2[2] - c1[2]) * clampedT);
  return `rgb(${r}, ${g}, ${b})`;
};

export const KineticTypography: React.FC<KineticVideoProps> = ({
  primaryColor = '#111111',
  mutedColor = '#c8c8c8',
  backgroundColor = '#faf9f6',
  fontFamily = 'Playfair Display, Georgia, Garamond, serif',
  mode = 'cumulative',
  headerTitle = "DOUGLAS ADAMS • THE HITCHHIKER'S GUIDE TO THE GALAXY",
  totalDurationSeconds = 180,
  audioFile = 'audio_chapter1.mp3',
  subtitles,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  const pages: SubtitlePage[] = subtitles && subtitles.length > 0 ? subtitles : fallbackSubtitles;

  const primaryRgb = useMemo(() => hexToRgb(primaryColor), [primaryColor]);
  const mutedRgb = useMemo(() => hexToRgb(mutedColor), [mutedColor]);

  // Find active sentence page dynamically
  const activePageIndex = useMemo(() => {
    return pages.findIndex(
      (p) => currentTime >= p.startTime - 0.25 && currentTime <= p.endTime + 0.25
    );
  }, [currentTime, pages]);

  const activePage = activePageIndex !== -1 ? pages[activePageIndex] : null;

  // Smooth page transition calculations
  let pageOpacity = 0;
  let pageTranslateY = 0;

  if (activePage) {
    const pageStart = activePage.startTime;
    const pageEnd = activePage.endTime;

    // Smooth entrance (0.18s)
    const enterProgress = interpolate(
      currentTime,
      [pageStart - 0.18, pageStart + 0.08],
      [0, 1],
      { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) }
    );

    // Smooth exit (0.16s)
    const exitProgress = interpolate(
      currentTime,
      [pageEnd - 0.15, pageEnd + 0.15],
      [1, 0],
      { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic) }
    );

    pageOpacity = Math.min(enterProgress, exitProgress);
    pageTranslateY = interpolate(enterProgress, [0, 1], [25, 0]) + interpolate(exitProgress, [0, 1], [-15, 0]);
  }

  return (
    <AbsoluteFill
      style={{
        backgroundColor,
        fontFamily,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '100px 140px',
        boxSizing: 'border-box',
        overflow: 'hidden',
      }}
    >
      {/* Synchronized Audio */}
      <Audio src={staticFile(audioFile)} />

      {/* Top Header Badge */}
      <div
        style={{
          position: 'absolute',
          top: '64px',
          left: '120px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
          fontSize: '15px',
          letterSpacing: '0.18em',
          textTransform: 'uppercase',
          color: '#8a8d93',
          fontWeight: 600,
        }}
      >
        <span
          style={{
            display: 'inline-block',
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: '#3b82f6',
          }}
        />
        {headerTitle}
      </div>

      {/* Center Sentence Render */}
      {activePage ? (
        <div
          style={{
            opacity: pageOpacity,
            transform: `translateY(${pageTranslateY}px)`,
            maxWidth: '1540px',
            width: '100%',
            lineHeight: 1.42,
            fontSize: '64px',
            textAlign: 'left',
            display: 'flex',
            flexWrap: 'wrap',
            alignContent: 'center',
            letterSpacing: '-0.015em',
          }}
        >
          {activePage.words.map((word, idx) => {
            // Frame-interpolated highlight progress (0 = inactive, 1 = fully spoken)
            const highlightProgress = interpolate(
              currentTime,
              [word.start - 0.04, word.start + 0.06],
              [0, 1],
              {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
                easing: Easing.bezier(0.16, 1, 0.3, 1),
              }
            );

            // Is the current word actively being spoken right now?
            const isCurrentlyActive = currentTime >= word.start && currentTime <= word.end + 0.04;
            
            // Safe monotonic input range for scale pop
            const mid = word.start + Math.max(0.02, (word.end - word.start) * 0.4);
            const safeEnd = Math.max(word.end, mid + 0.02);

            const scalePop = isCurrentlyActive
              ? interpolate(
                  currentTime,
                  [word.start, mid, safeEnd],
                  [1.0, 1.035, 1.0],
                  { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
                )
              : 1.0;

            // Interpolated color per frame
            const textColor = mode === 'cumulative'
              ? lerpColor(mutedRgb, primaryRgb, highlightProgress)
              : isCurrentlyActive
              ? lerpColor(mutedRgb, primaryRgb, highlightProgress)
              : lerpColor(
                  primaryRgb,
                  mutedRgb,
                  interpolate(currentTime, [word.end, word.end + 0.1], [0, 1], {
                    extrapolateLeft: 'clamp',
                    extrapolateRight: 'clamp',
                  })
                );

            // Interpolated weight / opacity
            const textOpacity = interpolate(highlightProgress, [0, 1], [0.55, 1.0]);

            return (
              <span
                key={`${activePage.id}-${idx}-${word.text}`}
                style={{
                  display: 'inline-block',
                  marginRight: '0.28em',
                  marginBottom: '0.14em',
                  color: textColor,
                  opacity: textOpacity,
                  fontWeight: highlightProgress > 0.6 ? 600 : 400,
                  transform: `scale(${scalePop})`,
                  transformOrigin: '50% 85%',
                }}
              >
                {word.text}
              </span>
            );
          })}
        </div>
      ) : null}

      {/* Progress Bar (60fps smooth) */}
      <div
        style={{
          position: 'absolute',
          bottom: '0px',
          left: '0px',
          right: '0px',
          height: '6px',
          backgroundColor: 'rgba(0, 0, 0, 0.04)',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${Math.min(100, (currentTime / (totalDurationSeconds || 180)) * 100)}%`,
            backgroundColor: primaryColor,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
