import { Meta, StoryFn } from '@storybook/vue3';
import PokerChips from './PokerChips.vue';

export default {
  title: 'component/Poker/PokerChips',
  component: PokerChips,
  tags: ['autodocs'],
} as Meta;

const Template: StoryFn = (args) => ({
  components: { PokerChips },
  setup() {
    return { args };
  },
  template: '<PokerChips v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  chips: [
    { id: 1, color: '#FF0000', denomination: 5 },
    { id: 2, color: '#00FF00', denomination: 10 },
    { id: 3, color: '#0000FF', denomination: 25 },
  ],
  state: 'stacked',
};

export const Stacked = Template.bind({});
Stacked.args = {
  ...Default.args,
  state: 'stacked',
};

export const Moving = Template.bind({});
Moving.args = {
  ...Default.args,
  state: 'moving',
};

export const BetPlaced = Template.bind({});
BetPlaced.args = {
  ...Default.args,
  state: 'betPlaced',
};

export const AllIn = Template.bind({});
AllIn.args = {
  ...Default.args,
  state: 'allIn',
};