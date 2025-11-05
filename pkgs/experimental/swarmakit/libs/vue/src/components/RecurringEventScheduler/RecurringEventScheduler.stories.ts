import { Meta, StoryFn } from '@storybook/vue3';
import RecurringEventScheduler from './RecurringEventScheduler.vue';

export default {
  title: 'component/Scheduling/RecurringEventScheduler',
  component: RecurringEventScheduler,
  tags: ['autodocs']
} as Meta<typeof RecurringEventScheduler>;

const Template: StoryFn<typeof RecurringEventScheduler> = (args) => ({
  components: { RecurringEventScheduler },
  setup() {
    return { args };
  },
  template: '<RecurringEventScheduler v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {};

export const EventCreated = Template.bind({});
EventCreated.args = {
  feedbackMessageProp: 'Event created successfully!'
};

export const RecurrenceSet = Template.bind({});
RecurrenceSet.args = {
  feedbackMessageProp: 'Recurrence set: weekly from 2023-11-01 to 2023-12-01'
};

export const RecurrenceEnded = Template.bind({});
RecurrenceEnded.args = {
  feedbackMessageProp: 'Recurrence ended on 2023-12-01'
};