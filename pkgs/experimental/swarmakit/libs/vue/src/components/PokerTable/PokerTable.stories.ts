import { Meta, StoryFn } from '@storybook/vue3';
import PokerTable from './PokerTable.vue';

export default {
  title: 'component/Poker/PokerTable',
  component: PokerTable,
  tags: ['autodocs'],
  argTypes: {
    tableColor: { control: 'color' },
  },
} as Meta;

const Template: StoryFn = (args) => ({
  components: { PokerTable },
  setup() {
    return { args };
  },
  template: '<PokerTable v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  seats: [],
  communityCards: [],
  tableColor: 'var(--table-green)',
};

export const Empty = Template.bind({});
Empty.args = {
  ...Default.args,
};

export const PlayersSeated = Template.bind({});
PlayersSeated.args = {
  seats: [
    { id: 1, name: 'Player 1', active: false },
    { id: 2, name: 'Player 2', active: true },
  ],
  communityCards: [],
};

export const InProgress = Template.bind({});
InProgress.args = {
  seats: [
    { id: 1, name: 'Player 1', active: false },
    { id: 2, name: 'Player 2', active: true },
  ],
  communityCards: [
    { id: 1, suit: '♠', rank: 'A' },
    { id: 2, suit: '♥', rank: 'K' },
  ],
};

export const Completed = Template.bind({});
Completed.args = {
  seats: [
    { id: 1, name: 'Player 1', active: false },
    { id: 2, name: 'Player 2', active: false },
  ],
  communityCards: [
    { id: 1, suit: '♠', rank: 'A' },
    { id: 2, suit: '♥', rank: 'K' },
    { id: 3, suit: '♦', rank: 'Q' },
    { id: 4, suit: '♣', rank: 'J' },
    { id: 5, suit: '♠', rank: '10' },
  ],
};