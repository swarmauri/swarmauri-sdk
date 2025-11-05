import { Meta, StoryFn } from '@storybook/vue3';
import PokerPlayerSeat from './PokerPlayerSeat.vue';

export default {
  title: 'component/Poker/PokerPlayerSeat',
  component: PokerPlayerSeat,
  tags: ['autodocs'],
} as Meta;

const Template: StoryFn = (args) => ({
  components: { PokerPlayerSeat },
  setup() {
    return { args };
  },
  template: '<PokerPlayerSeat v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  playerName: 'Player',
  playerChips: 0,
  playerCards: [],
  isActive: false,
  isFolded: false,
};

export const Empty = Template.bind({});
Empty.args = {
  ...Default.args,
};

export const Occupied = Template.bind({});
Occupied.args = {
  playerName: 'Player 1',
  playerChips: 1000,
  playerCards: [
    { id: 1, suit: '♠', rank: 'A' },
    { id: 2, suit: '♥', rank: 'K' },
  ],
};

export const Active = Template.bind({});
Active.args = {
  playerName: 'Player 2',
  playerChips: 1200,
  playerCards: [
    { id: 1, suit: '♦', rank: 'Q' },
    { id: 2, suit: '♣', rank: 'J' },
  ],
  isActive: true,
};

export const Folded = Template.bind({});
Folded.args = {
  playerName: 'Player 3',
  playerChips: 500,
  playerCards: [],
  isFolded: true,
};