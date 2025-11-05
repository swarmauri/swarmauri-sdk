import Carousel from './Carousel.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta = {
  title: 'Components/Media/Carousel',
  component: Carousel,
  tags: ['autodocs'],
  argTypes: {
    images: {
      control: { type: 'object' },
    },
    autoPlay: {
      control: { type: 'boolean' },
    },
    autoPlayInterval: {
      control: { type: 'number' },
    },
  },
};

export default meta;

const Template: StoryFn<Carousel> = (args) => ({
  Component: Carousel,
  props: args,
});

export const Default = Template.bind({});
Default.args = {
  images: ['image1.jpg', 'image2.jpg', 'image3.jpg'],
  autoPlay: false,
  autoPlayInterval: 3000,
};

export const AutoPlay = Template.bind({});
AutoPlay.args = {
  images: ['image1.jpg', 'image2.jpg', 'image3.jpg'],
  autoPlay: true,
  autoPlayInterval: 3000,
};

export const Paused = Template.bind({});
Paused.args = {
  images: ['image1.jpg', 'image2.jpg', 'image3.jpg'],
  autoPlay: false,
  autoPlayInterval: 3000,
};

export const Hover = Template.bind({});
Hover.args = {
  images: ['image1.jpg', 'image2.jpg', 'image3.jpg'],
  autoPlay: true,
  autoPlayInterval: 3000,
};

export const Active = Template.bind({});
Active.args = {
  images: ['image1.jpg', 'image2.jpg', 'image3.jpg'],
  autoPlay: true,
  autoPlayInterval: 1000,
};