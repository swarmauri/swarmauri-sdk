import { Meta, StoryFn } from '@storybook/vue3';
import ImageSlider from './ImageSlider.vue';

export default {
  title: 'component/Media/ImageSlider',
  component: ImageSlider,
  tags: ['autodocs'],
  argTypes: {
    images: { control: 'object' },
  },
} as Meta<typeof ImageSlider>;

const Template: StoryFn<typeof ImageSlider> = (args) => ({
  components: { ImageSlider },
  setup() {
    return { args };
  },
  template: '<ImageSlider v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  images: [
    'https://via.placeholder.com/800x400?text=Image+1',
    'https://via.placeholder.com/800x400?text=Image+2',
    'https://via.placeholder.com/800x400?text=Image+3',
  ],
};

export const Active = Template.bind({});
Active.args = {
  ...Default.args,
};

export const Inactive = Template.bind({});
Inactive.args = {
  ...Default.args,
  images: [],
};

export const Hover = Template.bind({});
Hover.args = {
  ...Default.args,
};