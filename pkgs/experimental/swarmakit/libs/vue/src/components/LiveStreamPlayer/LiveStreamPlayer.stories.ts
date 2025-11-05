import { Meta, StoryFn } from '@storybook/vue3';
import LiveStreamPlayer from './LiveStreamPlayer.vue';

export default {
  title: 'component/Media/LiveStreamPlayer',
  component: LiveStreamPlayer,
  tags: ['autodocs'],
  argTypes: {
    streamSrc: { control: 'text' },
  },
} as Meta<typeof LiveStreamPlayer>;

const Template: StoryFn<typeof LiveStreamPlayer> = (args) => ({
  components: { LiveStreamPlayer },
  setup() {
    return { args };
  },
  template: '<LiveStreamPlayer v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  streamSrc: 'https://www.w3schools.com/html/mov_bbb.mp4',
};

export const Live = Template.bind({});
Live.args = {
  ...Default.args,
};

export const Paused = Template.bind({});
Paused.args = {
  ...Default.args,
};

export const Buffering = Template.bind({});
Buffering.args = {
  ...Default.args,
};

export const Muted = Template.bind({});
Muted.args = {
  ...Default.args,
};