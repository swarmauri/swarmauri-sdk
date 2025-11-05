import { Meta, StoryFn } from '@storybook/vue3';
import CardHeader from './CardHeader.vue';

export default {
  title: 'Component/Card Elements/CardHeader',
  component: CardHeader,
  tags: ['autodocs'],
  argTypes: {
    title: { control: 'text' },
    subtitle: { control: 'text' },
    image: { control: 'text' },
    icon: { control: 'text' },
  },
} as Meta;

const Template: StoryFn = (args) => ({
  components: { CardHeader },
  setup() {
    return { args };
  },
  template: '<CardHeader v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  title: 'Card Title',
  subtitle: 'Card Subtitle',
};

export const WithImage = Template.bind({});
WithImage.args = {
  title: 'Card Title',
  subtitle: 'Card Subtitle',
  image: 'https://via.placeholder.com/150',
};

export const WithIcon = Template.bind({});
WithIcon.args = {
  title: 'Card Title',
  subtitle: 'Card Subtitle',
  icon: 'fas fa-star',
};

export const Hovered = Template.bind({});
Hovered.args = {
  title: 'Card Title',
  subtitle: 'Card Subtitle',
};
Hovered.parameters = {
  pseudo: { hover: true },
};