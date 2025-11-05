import CommunityCards from './CommunityCards.vue';
import type { Meta, StoryFn } from '@storybook/vue3';

export default {
  title: 'component/Cards/CommunityCards',
  component: CommunityCards,
  tags: ['autodocs'],
} as Meta<typeof CommunityCards>;

const Template: StoryFn<typeof CommunityCards> = (args) => ({
  components: { CommunityCards },
  setup() {
    return { args };
  },
  template: '<CommunityCards v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  cards: [],
};

export const CardsDealt = Template.bind({});
CardsDealt.args = {
  cards: [
    { id: 1, state: 'dealt', label: '' },
    { id: 2, state: 'dealt', label: '' },
    { id: 3, state: 'dealt', label: '' },
  ],
};

export const CardsRevealed = Template.bind({});
CardsRevealed.args = {
  cards: [
    { id: 1, state: 'revealed', label: 'A♠' },
    { id: 2, state: 'revealed', label: 'K♣' },
    { id: 3, state: 'revealed', label: 'Q♦' },
  ],
};

export const Empty = Template.bind({});
Empty.args = {
  cards: [],
};

export const Full = Template.bind({});
Full.args = {
  cards: [
    { id: 1, state: 'revealed', label: 'A♠' },
    { id: 2, state: 'revealed', label: 'K♣' },
    { id: 3, state: 'revealed', label: 'Q♦' },
    { id: 4, state: 'revealed', label: 'J♥' },
    { id: 5, state: 'revealed', label: '10♠' },
  ],
};