import { Meta, StoryFn } from '@storybook/vue3';
import PokerHand from './PokerHand.vue';

export default {
  title: 'component/Poker/PokerHand',
  component: PokerHand,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    cards: { control: 'object' },
    revealed: { control: 'boolean' },
    folded: { control: 'boolean' },
  },
} as Meta<typeof PokerHand>;

const Template: StoryFn<typeof PokerHand> = (args) => ({
  components: { PokerHand },
  setup() {
    return { args };
  },
  template: '<PokerHand v-bind="args" />',
});

export const Dealt = Template.bind({});
Dealt.args = {
  cards: [
    { id: 1, value: 'A♠' },
    { id: 2, value: 'K♠' },
  ],
  revealed: false,
  folded: false,
};

export const Revealed = Template.bind({});
Revealed.args = {
  cards: [
    { id: 1, value: 'A♠' },
    { id: 2, value: 'K♠' },
  ],
  revealed: true,
  folded: false,
};

export const Folded = Template.bind({});
Folded.args = {
  cards: [
    { id: 1, value: 'A♠' },
    { id: 2, value: 'K♠' },
  ],
  revealed: false,
  folded: true,
};