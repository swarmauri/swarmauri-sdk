import AudioPlayerAdvanced from './AudioPlayerAdvanced.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta = {
  title: 'Components/Media/AudioPlayerAdvanced',
  component: AudioPlayerAdvanced,
  tags: ['autodocs'],
  argTypes: {
    src: {
      control: { type: 'text' },
    },
    isPlaying: {
      control: { type: 'boolean' },
    },
    isMuted: {
      control: { type: 'boolean' },
    },
    volume: {
      control: { type: 'number' },
    },
    playbackRate: {
      control: { type: 'number' },
    },
  },
};

export default meta;

const Template: StoryFn = (args) => ({
  Component: AudioPlayerAdvanced,
  props: args,
});

export const Default = Template.bind({});
Default.args = {
  src: 'path/to/audio.mp3',
  isPlaying: false,
  isMuted: false,
  volume: 1,
  playbackRate: 1,
};

export const Play = Template.bind({});
Play.args = {
  src: 'path/to/audio.mp3',
  isPlaying: true,
  isMuted: false,
  volume: 1,
  playbackRate: 1,
};

export const Pause = Template.bind({});
Pause.args = {
  src: 'path/to/audio.mp3',
  isPlaying: false,
  isMuted: false,
  volume: 1,
  playbackRate: 1,
};

export const Seek = Template.bind({});
Seek.args = {
  src: 'path/to/audio.mp3',
  isPlaying: false,
  isMuted: false,
  volume: 1,
  playbackRate: 1,
};

export const Mute = Template.bind({});
Mute.args = {
  src: 'path/to/audio.mp3',
  isPlaying: false,
  isMuted: true,
  volume: 1,
  playbackRate: 1,
};

export const VolumeControl = Template.bind({});
VolumeControl.args = {
  src: 'path/to/audio.mp3',
  isPlaying: false,
  isMuted: false,
  volume: 0.5,
  playbackRate: 1,
};

export const SpeedControl = Template.bind({});
SpeedControl.args = {
  src: 'path/to/audio.mp3',
  isPlaying: false,
  isMuted: false,
  volume: 1,
  playbackRate: 1.5,
};