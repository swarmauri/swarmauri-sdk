import ImageSlider from './ImageSlider.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta = {
  title: 'Components/Media/ImageSlider',
  component: ImageSlider,
  tags: ['autodocs'],
  argTypes: {
    images: {
      control: { type: 'object' },
    },
    activeIndex: {
      control: { type: 'number' },
    },
  },
};

export default meta;

const Template: StoryFn = (args) => ({
  Component: ImageSlider,
  props: args,
});

export const Default = Template.bind({});
Default.args = {
  images: [
    'https://via.placeholder.com/800x450?text=Image+1',
    'https://via.placeholder.com/800x450?text=Image+2',
    'https://via.placeholder.com/800x450?text=Image+3',
  ],
  activeIndex: 0,
};

export const Active = Template.bind({});
Active.args = {
  images: [
    'https://via.placeholder.com/800x450?text=Image+1',
    'https://via.placeholder.com/800x450?text=Image+2',
    'https://via.placeholder.com/800x450?text=Image+3',
  ],
  activeIndex: 1,
};

export const Hover = Template.bind({});
Hover.args = {
  images: [
    'https://via.placeholder.com/800x450?text=Image+1',
    'https://via.placeholder.com/800x450?text=Image+2',
    'https://via.placeholder.com/800x450?text=Image+3',
  ],
  activeIndex: 0,
};