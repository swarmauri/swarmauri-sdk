import { Meta, StoryFn } from '@storybook/vue3';
import EmbeddedMediaIframe from './EmbeddedMediaIframe.vue';

export default {
  title: 'component/Media/EmbeddedMediaIframe',
  component: EmbeddedMediaIframe,
  tags: ['autodocs'],
  argTypes: {
    src: { control: 'text' },
  },
} as Meta<typeof EmbeddedMediaIframe>;

const Template: StoryFn<typeof EmbeddedMediaIframe> = (args) => ({
  components: { EmbeddedMediaIframe },
  setup() {
    return { args };
  },
  template: '<EmbeddedMediaIframe v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  src: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
};

export const Fullscreen = Template.bind({});
Fullscreen.args = {
  ...Default.args,
};

export const Buffering = Template.bind({});
Buffering.args = {
  ...Default.args,
  src: '', // Simulate buffering state by providing an empty or slow-loading source
};