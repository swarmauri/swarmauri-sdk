import { Meta, StoryFn } from '@storybook/vue3';
import Carousel from './Carousel.vue';

export default {
  title: 'component/Media/Carousel',
  component: Carousel,
  tags: ['autodocs'],
  argTypes: {
    slides: { control: 'object' },
    interval: { control: 'number' },
  },
} as Meta<typeof Carousel>;

const Template: StoryFn<typeof Carousel> = (args) => ({
  components: { Carousel },
  setup() {
    return { args };
  },
  template: '<Carousel v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  slides: [
    { src: 'image1.jpg', alt: 'Image 1' },
    { src: 'image2.jpg', alt: 'Image 2' },
    { src: 'image3.jpg', alt: 'Image 3' },
  ],
  interval: 3000,
};

export const AutoPlay = Template.bind({});
AutoPlay.args = {
  ...Default.args,
};

export const Paused = Template.bind({});
Paused.args = {
  ...Default.args,
  interval: undefined,
};

export const Hover = Template.bind({});
Hover.args = {
  ...Default.args,
};

export const Active = Template.bind({});
Active.args = {
  ...Default.args,
};