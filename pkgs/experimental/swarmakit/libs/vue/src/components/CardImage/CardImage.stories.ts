import { Meta, StoryFn } from '@storybook/vue3';
import CardImage from './CardImage.vue';

export default {
  title: 'Component/Card Elements/CardImage',
  component: CardImage,
  tags: ['autodocs'],
  argTypes: {
    src: {
      control: { type: 'text' },
    },
    caption: {
      control: { type: 'text' },
    },
    overlay: {
      control: { type: 'text' },
    },
  },
} as Meta;

const Template: StoryFn = (args) => ({
  components: { CardImage },
  setup() {
    return { args };
  },
  template: '<CardImage v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  src: 'https://via.placeholder.com/400x225',
};

export const Hovered = Template.bind({});
Hovered.args = {
  src: 'https://via.placeholder.com/400x225',
  overlay: 'Overlay Text',
};

export const Expanded = Template.bind({});
Expanded.args = {
  src: 'https://via.placeholder.com/800x450',
};

export const WithCaption = Template.bind({});
WithCaption.args = {
  src: 'https://via.placeholder.com/400x225',
  caption: 'Sample Caption',
};