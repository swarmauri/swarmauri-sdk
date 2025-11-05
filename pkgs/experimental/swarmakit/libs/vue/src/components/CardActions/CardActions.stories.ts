import { Meta, StoryFn } from '@storybook/vue3';
import CardActions from './CardActions.vue';

export default {
  title: 'Component/Card Elements/CardActions',
  component: CardActions,
  tags: ['autodocs'],
  argTypes: {
    actions: {
      control: { type: 'object' },
    },
  },
} as Meta;

const Template: StoryFn = (args) => ({
  components: { CardActions },
  setup() {
    return { args };
  },
  template: '<CardActions v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  actions: [
    { label: 'Button 1', onClick: () => alert('Button 1 clicked') },
    { label: 'Button 2', onClick: () => alert('Button 2 clicked') },
  ],
};

export const Hovered = Template.bind({});
Hovered.args = {
  actions: [
    { label: 'Button 1', onClick: () => alert('Button 1 clicked') },
    { label: 'Button 2', onClick: () => alert('Button 2 clicked') },
  ],
};

export const Disabled = Template.bind({});
Disabled.args = {
  actions: [
    { label: 'Button 1', onClick: () => alert('Button 1 clicked'), disabled: true },
    { label: 'Button 2', onClick: () => alert('Button 2 clicked') },
  ],
};