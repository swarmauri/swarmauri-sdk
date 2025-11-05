import { Meta, StoryFn } from '@storybook/vue3';
import RankingPoll from './RankingPoll.vue';

export default {
  title: 'component/Polls/RankingPoll',
  component: RankingPoll,
  tags: ['autodocs'],
  argTypes: {
    question: { control: 'text' },
    options: { control: 'object' },
    isDisabled: { control: 'boolean' },
    showResults: { control: 'boolean' },
  },
} as Meta;

const Template: StoryFn = (args) => ({
  components: { RankingPoll },
  setup() {
    return { args };
  },
  template: '<RankingPoll v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  question: 'Rank your favorite fruits:',
  options: ['Apple', 'Banana', 'Cherry'],
  isDisabled: false,
  showResults: false,
};

export const Unanswered = Template.bind({});
Unanswered.args = {
  ...Default.args,
  showResults: false,
};

export const Answered = Template.bind({});
Answered.args = {
  ...Default.args,
  options: ['Cherry', 'Apple', 'Banana'],
  showResults: false,
};

export const ResultsVisible = Template.bind({});
ResultsVisible.args = {
  ...Default.args,
  showResults: true,
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Default.args,
  isDisabled: true,
};