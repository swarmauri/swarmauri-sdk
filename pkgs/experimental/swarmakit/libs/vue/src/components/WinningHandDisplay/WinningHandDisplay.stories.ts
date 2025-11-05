import { Meta, StoryFn } from '@storybook/vue3';
import WinningHandDisplay from './WinningHandDisplay.vue';

export default {
  title: 'component/Poker/WinningHandDisplay',
  component: WinningHandDisplay,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    communityCards: { control: 'object' },
    playerCards: { control: 'object' },
    winningCards: { control: 'object' },
    isHidden: { control: 'boolean' },
  },
} as Meta<typeof WinningHandDisplay>;

const Template: StoryFn<typeof WinningHandDisplay> = (args) => ({
  components: { WinningHandDisplay },
  setup() {
    return { args };
  },
  template: '<WinningHandDisplay v-bind="args" />',
});

export const Visible = Template.bind({});
Visible.args = {
  communityCards: ['10H', 'JH', 'QH', 'KH', 'AH'],
  playerCards: ['10H', 'JH'],
  winningCards: ['10H', 'JH', 'QH', 'KH', 'AH'],
  isHidden: false,
};

export const Hidden = Template.bind({});
Hidden.args = {
  communityCards: ['10H', 'JH', 'QH', 'KH', 'AH'],
  playerCards: ['10H', 'JH'],
  winningCards: ['10H', 'JH', 'QH', 'KH', 'AH'],
  isHidden: true,
};