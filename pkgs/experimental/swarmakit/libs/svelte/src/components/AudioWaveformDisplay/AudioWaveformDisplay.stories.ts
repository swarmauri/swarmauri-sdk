import AudioWaveformDisplay from './AudioWaveformDisplay.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta = {
  title: 'Components/Media/AudioWaveformDisplay',
  component: AudioWaveformDisplay,
  tags: ['autodocs'],
  argTypes: {
    src: {
      control: { type: 'text' },
    },
    isPlaying: {
      control: { type: 'boolean' },
    },
    isLoading: {
      control: { type: 'boolean' },
    },
    currentTime: {
      control: { type: 'number' },
    },
    duration: {
      control: { type: 'number' },
    },
  },
};

export default meta;

const Template: StoryFn = (args) => ({
  Component: AudioWaveformDisplay,
  props: args,
});

export const Default = Template.bind({});
Default.args = {
  src: 'path/to/audio.mp3',
  isPlaying: false,
  isLoading: false,
  currentTime: 0,
  duration: 0,
};

export const Playing = Template.bind({});
Playing.args = {
  src: 'path/to/audio.mp3',
  isPlaying: true,
  isLoading: false,
  currentTime: 10,
  duration: 100,
};

export const Paused = Template.bind({});
Paused.args = {
  src: 'path/to/audio.mp3',
  isPlaying: false,
  isLoading: false,
  currentTime: 10,
  duration: 100,
};

export const Loading = Template.bind({});
Loading.args = {
  src: 'path/to/audio.mp3',
  isPlaying: false,
  isLoading: true,
  currentTime: 0,
  duration: 0,
};

export const Scrubbing = Template.bind({});
Scrubbing.args = {
  src: 'path/to/audio.mp3',
  isPlaying: false,
  isLoading: false,
  currentTime: 50,
  duration: 100,
};