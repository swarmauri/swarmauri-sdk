import { Meta, StoryFn } from '@storybook/vue3';
import SliderPoll from './SliderPoll.vue';

export default {
  title: 'component/Polls/SliderPoll',
  component: SliderPoll,
  tags: ['autodocs'],
  argTypes: {
    question: { control: 'text' },
    min: { control: 'number' },
    max: { control: 'number' },
    initialValue: { control: 'number' },
    isDisabled: { control: 'boolean' },
    showResults: { control: 'boolean' },
  },
} as Meta;

const Template: StoryFn = (args) => ({
  components: { SliderPoll },
  setup() {
    return { args };
  },
  template: '<SliderPoll v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  question: 'How satisfied are you with our service?',
  min: 1,
  max: 100,
  initialValue: 50,
  isDisabled: false,
  showResults: false,
};

export const Unanswered = Template.bind({});
Unanswered.args = {
  ...Default.args,
  initialValue: 50,
};

export const Answered = Template.bind({});
Answered.args = {
  ...Default.args,
  initialValue: 75,
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