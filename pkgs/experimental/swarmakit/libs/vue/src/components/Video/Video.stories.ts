import { Meta, StoryFn } from '@storybook/vue3';
import Video from './Video.vue';

export default {
  title: 'component/Media/Video',
  component: Video,
  tags: ['autodocs'],
  argTypes: {
    videoSrc: { control: 'text' },
    initialState: { control: 'select', options: ['uploading', 'paused', 'completed', 'error'] },
  },
} as Meta<typeof Video>;

const Template: StoryFn<typeof Video> = (args) => ({
  components: { Video },
  setup() {
    return { args };
  },
  template: '<Video v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  videoSrc: 'https://www.w3schools.com/html/mov_bbb.mp4',
  initialState: 'paused',
};

export const Uploading = Template.bind({});
Uploading.args = {
  ...Default.args,
  initialState: 'uploading',
};

export const Paused = Template.bind({});
Paused.args = {
  ...Default.args,
  initialState: 'paused',
};

export const Completed = Template.bind({});
Completed.args = {
  ...Default.args,
  initialState: 'completed',
};

export const Error = Template.bind({});
Error.args = {
  ...Default.args,
  initialState: 'error',
};