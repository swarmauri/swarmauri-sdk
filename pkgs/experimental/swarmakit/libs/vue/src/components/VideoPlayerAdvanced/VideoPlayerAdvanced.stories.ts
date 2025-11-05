import { Meta, StoryFn } from '@storybook/vue3';
import VideoPlayerAdvanced from './VideoPlayerAdvanced.vue';

export default {
  title: 'component/Media/VideoPlayerAdvanced',
  component: VideoPlayerAdvanced,
  tags: ['autodocs'],
  argTypes: {
    videoSrc: { control: 'text' },
    subtitlesSrc: { control: 'text' },
  },
} as Meta<typeof VideoPlayerAdvanced>;

const Template: StoryFn<typeof VideoPlayerAdvanced> = (args) => ({
  components: { VideoPlayerAdvanced },
  setup() {
    return { args };
  },
  template: '<VideoPlayerAdvanced v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  videoSrc: 'https://www.w3schools.com/html/mov_bbb.mp4',
  subtitlesSrc: 'https://example.com/subtitles.vtt',
};

export const Play = Template.bind({});
Play.args = {
  ...Default.args,
};

export const Pause = Template.bind({});
Pause.args = {
  ...Default.args,
};

export const Fullscreen = Template.bind({});
Fullscreen.args = {
  ...Default.args,
};

export const Buffering = Template.bind({});
Buffering.args = {
  ...Default.args,
};

export const SubtitlesOnOff = Template.bind({});
SubtitlesOnOff.args = {
  ...Default.args,
};

export const PiPMode = Template.bind({});
PiPMode.args = {
  ...Default.args,
};