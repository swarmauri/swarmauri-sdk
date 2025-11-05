import type { Meta, StoryFn } from '@storybook/vue3';
import PlayingCard from './PlayingCard.vue';

export default {
  title: 'component/Cards/PlayingCard',
  component: PlayingCard,
  tags: ['autodocs'],
  argTypes: {
    flipped: { control: 'boolean' },
    disabled: { control: 'boolean' }
  }
} as Meta<typeof PlayingCard>;

const Template: StoryFn<typeof PlayingCard> = (args) => ({
  components: { PlayingCard },
  setup() {
    return { args };
  },
  template: `
    <PlayingCard v-bind="args">
      <template #back>Back Design</template>
      <template #front>Ace of Spades</template>
    </PlayingCard>
  `
});

export const Default = Template.bind({});
Default.args = {
  flipped: false,
  disabled: false
};

export const FaceUp = Template.bind({});
FaceUp.args = {
  flipped: true
};

export const FaceDown = Template.bind({});
FaceDown.args = {
  flipped: false
};

export const Flipped = Template.bind({});
Flipped.args = {
  flipped: true
};

export const Hovered = Template.bind({});
Hovered.args = {
  flipped: false
};

export const Disabled = Template.bind({});
Disabled.args = {
  disabled: true
};