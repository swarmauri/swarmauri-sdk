import { Meta, StoryFn } from '@storybook/vue3';
import DealerButton from './DealerButton.vue';

export default {
  title: 'component/Poker/DealerButton',
  component: DealerButton,
  tags: ['autodocs'],
} as Meta;

const Template: StoryFn = (args) => ({
  components: { DealerButton },
  setup() {
    return { args };
  },
  template: '<DealerButton v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  state: 'default',
};

export const Moving = Template.bind({});
Moving.args = {
  state: 'moving',
};

export const Hovered = Template.bind({});
Hovered.args = {
  state: 'hovered',
};