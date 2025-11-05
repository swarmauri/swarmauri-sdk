import DiscardPile from './DiscardPile.vue';
import {Meta,StoryFn} from '@storybook/vue3';

export default {
  title: 'component/Cards/DiscardPile',
  component: DiscardPile,
  tags: ['autodocs'],
} as Meta

const Template:StoryFn = (args) => ({
  components: { DiscardPile },
  setup() {
    return { args };
  },
  template: `
    <DiscardPile v-bind="args">
      <template #card="{ card }">
        <div>{{ card.content }}</div>
      </template>
    </DiscardPile>
  `,
});

const sampleCards = Array.from({ length: 5 }, (_, i) => ({ id: i + 1, content: `Card ${i + 1}` }));

export const Default = Template.bind({});
Default.args = {
  cards: sampleCards,
  maxCards: 10,
  overlapOffset: 5,
};

export const Empty = Template.bind({});
Empty.args = {
  cards: [],
  maxCards: 10,
  overlapOffset: 5,
};

export const ContainsCards = Template.bind({});
ContainsCards.args = {
  cards: sampleCards,
  maxCards: 10,
  overlapOffset: 5,
};

export const Hovered = Template.bind({});
Hovered.args = {
  cards: sampleCards,
  maxCards: 10,
  overlapOffset: 5,
};

export const Full = Template.bind({});
Full.args = {
  cards: Array.from({ length: 10 }, (_, i) => ({ id: i + 1, content: `Card ${i + 1}` })),
  maxCards: 10,
  overlapOffset: 5,
};