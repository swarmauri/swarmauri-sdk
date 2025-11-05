import { Meta, StoryFn } from '@storybook/vue3';
import EventReminderSystem from './EventReminderSystem.vue';

export default {
  title: 'component/Scheduling/EventReminderSystem',
  component: EventReminderSystem,
  tags: ['autodocs']
} as Meta<typeof EventReminderSystem>;

const Template: StoryFn<typeof EventReminderSystem> = (args) => ({
  components: { EventReminderSystem },
  setup() {
    return { args };
  },
  template: '<EventReminderSystem v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {};

export const ReminderSet = Template.bind({});
ReminderSet.args = {
  feedbackMessage: 'Reminder set for "Team Meeting" via Email.'
};

export const ReminderSent = Template.bind({});
ReminderSent.args = {
  feedbackMessage: 'Reminder for "Project Deadline" sent via SMS.'
};

export const ReminderCanceled = Template.bind({});
ReminderCanceled.args = {
  feedbackMessage: 'Reminder for "Client Call" canceled.'
};