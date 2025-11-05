import HandOfCards from './HandOfCards.vue';
import {Meta,StoryFn} from '@storybook/vue3'

export default {
  title: 'component/Cards/HandOfCards',
  component: HandOfCards,
  tags: ['autodocs'],
  argTypes: {
    cards: { control: 'object' },
    maxCards: { control: 'number' },
  },
} as Meta <typeof HandOfCards>

const Template:StoryFn<typeof HandOfCards> = (args) => ({
  components: { HandOfCards },
  setup() {
    return { args };
  },
  template: `
    <HandOfCards v-bind="args">
      <template #card="{ card }">
        <div>{{ card.content }}</div>
      </template>
    </HandOfCards>
  `,
});

const sampleCards = Array.from({ length: 5 }, (_, i) => ({ id: i + 1, content: `Card ${i + 1}` }));

export const Default = Template.bind({});
Default.args = {
  cards: sampleCards,
  maxCards: 5,
};

export const Selected = Template.bind({});
Selected.args = {
  cards: sampleCards,
  maxCards: 5,
};

export const Unselected = Template.bind({});
Unselected.args = {
  cards: sampleCards,
  maxCards: 5,
};

export const Full = Template.bind({});
Full.args = {
  cards: Array.from({ length: 5 }, (_, i) => ({ id: i + 1, content: `Card ${i + 1}` })),
  maxCards: 5,
};

export const Empty = Template.bind({});
Empty.args = {
  cards: [],
  maxCards: 5,
};

export const MaxLimitReached = Template.bind({});
MaxLimitReached.args = {
  cards: sampleCards,
  maxCards: 3,
};