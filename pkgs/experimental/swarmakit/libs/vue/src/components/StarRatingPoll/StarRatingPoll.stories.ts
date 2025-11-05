import { Meta, StoryFn } from '@storybook/vue3';
import StarRatingPoll from './StarRatingPoll.vue';

export default {
  title: 'component/Polls/StarRatingPoll',
  component: StarRatingPoll,
  tags: ['autodocs'],
  argTypes: {
    question: { control: 'text' },
    totalStars: { control: 'number' },
    initialRating: { control: 'number' },
    isDisabled: { control: 'boolean' },
    showResults: { control: 'boolean' },
  },
} as Meta;

const Template: StoryFn = (args) => ({
  components: { StarRatingPoll },
  setup() {
    return { args };
  },
  template: '<StarRatingPoll v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  question: 'Rate your experience:',
  totalStars: 5,
  initialRating: 0,
  isDisabled: false,
  showResults: false,
};

export const Unanswered = Template.bind({});
Unanswered.args = {
  ...Default.args,
  initialRating: 0,
};

export const Answered = Template.bind({});
Answered.args = {
  ...Default.args,
  initialRating: 3,
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