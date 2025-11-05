import { Meta, StoryFn } from '@storybook/vue3';
import Pot from './Pot.vue';

export default {
  title: 'component/Poker/Pot',
  component: Pot,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    chips: { control: 'object' },
    totalChips: { control: 'number' },
    isWon: { control: 'boolean' },
  },
} as Meta<typeof Pot>;

const Template: StoryFn<typeof Pot> = (args) => ({
  components: { Pot },
  setup() {
    return { args };
  },
  template: '<Pot v-bind="args" />',
});

export const Empty = Template.bind({});
Empty.args = {
  chips: [],
  totalChips: 0,
  isWon: false,
};

export const ChipsAdded = Template.bind({});
ChipsAdded.args = {
  chips: [10, 20, 50],
  totalChips: 80,
  isWon: false,
};

export const Won = Template.bind({});
Won.args = {
  chips: [10, 20, 50],
  totalChips: 80,
  isWon: true,
};