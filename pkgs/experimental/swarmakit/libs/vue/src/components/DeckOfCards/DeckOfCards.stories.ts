import DeckOfCards from './DeckOfCards.vue';
import {Meta,StoryFn} from '@storybook/vue3'

export default {
  title: 'component/Cards/DeckOfCards',
  component: DeckOfCards,
  tags: ['autodocs'],
} as Meta; 

const Template:StoryFn = (args: any) => ({
  components: { DeckOfCards },
  setup() {
    return { args };
  },
  template: '<DeckOfCards v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  cards: Array.from({ length: 5 }, (_, id) => ({ id })),
  overlap: 10,
};

export const Shuffled = Template.bind({});
Shuffled.args = {
  cards: Array.from({ length: 5 }, (_, id) => ({ id })).sort(() => Math.random() - 0.5),
  overlap: 10,
};

export const Ordered = Template.bind({});
Ordered.args = {
  cards: Array.from({ length: 5 }, (_, id) => ({ id })),
  overlap: 10,
};

export const Empty = Template.bind({});
Empty.args = {
  cards: [],
  overlap: 10,
};

export const Full = Template.bind({});
Full.args = {
  cards: Array.from({ length: 10 }, (_, id) => ({ id })),
  overlap: 5,
};