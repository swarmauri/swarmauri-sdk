import { Meta, StoryFn } from '@storybook/vue3';
import VideoPlayer from './VideoPlayer.vue';

export default {
  title: 'component/Media/VideoPlayer',
  component: VideoPlayer,
  tags: ['autodocs'],
  argTypes: {
    videoSrc: { control: 'text' },
  },
} as Meta<typeof VideoPlayer>;

const Template: StoryFn<typeof VideoPlayer> = (args) => ({
  components: { VideoPlayer },
  setup() {
    return { args };
  },
  template: '<VideoPlayer v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  videoSrc: 'https://www.w3schools.com/html/mov_bbb.mp4',
};

export const Play = Template.bind({});
Play.args = {
  ...Default.args,
};

export const Pause = Template.bind({});
Pause.args = {
  ...Default.args,
};

export const Buffering = Template.bind({});
Buffering.args = {
  ...Default.args,
};

export const Fullscreen = Template.bind({});
Fullscreen.args = {
  ...Default.args,
};