import EmbeddedMediaIframe from './EmbeddedMediaIframe.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta = {
  title: 'Components/Media/EmbeddedMediaIframe',
  component: EmbeddedMediaIframe,
  tags: ['autodocs'],
  argTypes: {
    src: {
      control: { type: 'text' },
    },
    title: {
      control: { type: 'text' },
    },
    allowFullscreen: {
      control: { type: 'boolean' },
    },
  },
};

export default meta;

const Template: StoryFn<EmbeddedMediaIframe> = (args) => ({
  Component: EmbeddedMediaIframe,
  props: args,
});

export const Default = Template.bind({});
Default.args = {
  src: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
  title: 'Default Media',
  allowFullscreen: false,
};

export const Fullscreen = Template.bind({});
Fullscreen.args = {
  src: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
  title: 'Fullscreen Enabled Media',
  allowFullscreen: true,
};

export const Buffering = Template.bind({});
Buffering.args = {
  src: 'https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1',
  title: 'Buffering Media',
  allowFullscreen: false,
};