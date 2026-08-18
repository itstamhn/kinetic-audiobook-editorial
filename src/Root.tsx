import React from 'react';
import { Composition } from 'remotion';
import { KineticTypography, KineticVideoProps } from './KineticTypography';
import { MinimalistKinetic, MinimalistProps } from './MinimalistKinetic';
import { SciFiAudioReactive, SciFiProps } from './SciFiAudioReactive';
import { KineticShowcase, KineticShowcaseProps } from './KineticShowcase';
import { EditorialPageReader, EditorialPageReaderProps } from './EditorialPageReader';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Honda Video Style: Calm Multi-Line Editorial Reader */}
      <Composition
        id="Honda-Editorial-Light"
        component={EditorialPageReader}
        durationInFrames={41 * 60}
        fps={60}
        width={1920}
        height={1080}
        calculateMetadata={({ props }: { props: EditorialPageReaderProps }) => {
          const lastPage =
            props.pages && props.pages.length > 0
              ? props.pages[props.pages.length - 1]
              : null;
          const duration =
            props.totalDurationSeconds ||
            (lastPage ? lastPage.endTime + 0.5 : 41);
          return {
            durationInFrames: Math.ceil(duration * 60),
            fps: 60,
            width: 1920,
            height: 1080,
            defaultOutName: "audiobook_chapter_60fps",
          };
        }}
        defaultProps={{
          totalDurationSeconds: 41,
          audioFile: 'chapters_audio/chapter_00_prologue.mp3',
          pages: [],
        }}
      />

      {/* 2. Reference Video Match: Editorial Page Reader (Dark) */}
      <Composition
        id="Editorial-Page-Dark"
        component={EditorialPageReader}
        durationInFrames={31 * 60}
        fps={60}
        width={1920}
        height={1080}
        calculateMetadata={({ props }: { props: EditorialPageReaderProps }) => {
          const duration = props.totalDurationSeconds || 31;
          return {
            durationInFrames: Math.ceil(duration * 60),
            fps: 60,
            width: 1920,
            height: 1080,
          };
        }}
        defaultProps={{
          theme: 'dark',
          totalDurationSeconds: 31,
          audioFile: 'chapters_audio/chapter_00_prologue.mp3',
          pages: [],
        }}
      />
      {/* 1. Minimalist Paper Cream (Newsreader) */}
      <Composition
        id="Minimalist-Paper-Light"
        component={MinimalistKinetic}
        durationInFrames={30 * 60}
        fps={60}
        width={1920}
        height={1080}
        calculateMetadata={({ props }: { props: MinimalistProps }) => {
          const duration = props.totalDurationSeconds || 30;
          return {
            durationInFrames: Math.ceil(duration * 60),
            fps: 60,
            width: 1920,
            height: 1080,
          };
        }}
        defaultProps={{
          theme: 'light-paper',
          mode: 'continuous-ink',
          headerTitle: "Douglas Adams • The Hitchhiker's Guide to the Galaxy",
          totalDurationSeconds: 30,
          audioFile: 'chapters_audio/chapter_00_prologue.mp3',
          subtitles: [],
        }}
      />

      {/* 2. Minimalist Charcoal Dark (Newsreader) */}
      <Composition
        id="Minimalist-Charcoal-Dark"
        component={MinimalistKinetic}
        durationInFrames={30 * 60}
        fps={60}
        width={1920}
        height={1080}
        calculateMetadata={({ props }: { props: MinimalistProps }) => {
          const duration = props.totalDurationSeconds || 30;
          return {
            durationInFrames: Math.ceil(duration * 60),
            fps: 60,
            width: 1920,
            height: 1080,
          };
        }}
        defaultProps={{
          theme: 'dark-charcoal',
          mode: 'continuous-ink',
          headerTitle: "Douglas Adams • The Hitchhiker's Guide to the Galaxy",
          totalDurationSeconds: 30,
          audioFile: 'chapters_audio/chapter_00_prologue.mp3',
          subtitles: [],
        }}
      />

      {/* 3. Sci-Fi Terminal & Audio-Reactive Spectrum */}
      <Composition
        id="SciFi-AudioReactive-Demo"
        component={SciFiAudioReactive}
        durationInFrames={15 * 60}
        fps={60}
        width={1920}
        height={1080}
        calculateMetadata={({ props }: { props: SciFiProps }) => {
          const duration = props.totalDurationSeconds || 15;
          return {
            durationInFrames: Math.ceil(duration * 60),
            fps: 60,
            width: 1920,
            height: 1080,
          };
        }}
        defaultProps={{
          headerTitle: "THE HITCHHIKER'S GUIDE TO THE GALAXY • PROLOGUE",
          totalDurationSeconds: 15,
          audioFile: 'chapters_audio/chapter_00_prologue.mp3',
          subtitles: [],
          themeColor: '#00f0ff',
          accentColor: '#ffd700',
        }}
      />

      {/* 4. Universal Kinetic Chapter */}
      <Composition
        id="Universal-Kinetic-Chapter"
        component={KineticTypography}
        durationInFrames={30 * 60}
        fps={60}
        width={1920}
        height={1080}
        calculateMetadata={({ props }: { props: KineticVideoProps }) => {
          const duration = props.totalDurationSeconds || 30;
          return {
            durationInFrames: Math.ceil(duration * 60),
            fps: 60,
            width: 1920,
            height: 1080,
          };
        }}
        defaultProps={{
          primaryColor: '#111111',
          mutedColor: '#c8c8c8',
          backgroundColor: '#faf9f6',
          fontFamily: 'Newsreader, Georgia, Garamond, serif',
          mode: 'cumulative',
          headerTitle: "DOUGLAS ADAMS • THE HITCHHIKER'S GUIDE TO THE GALAXY",
          totalDurationSeconds: 30,
          audioFile: 'audio_chapter1.mp3',
        }}
      />
    </>
  );
};
