import { Meta, StoryFn } from '@storybook/vue3';
import EventDetailsDialog from './EventDetailsDialog.vue';

export default {
  title: 'component/Scheduling/EventDetailsDialog',
  component: EventDetailsDialog,
  tags: ['autodocs']
} as Meta<typeof EventDetailsDialog>;

const Template: StoryFn<typeof EventDetailsDialog> = (args) => ({
  components: { EventDetailsDialog },
  setup() {
    return { args };
  },
  template: '<EventDetailsDialog v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  event: {
    title: 'Team Meeting',
    description: 'Discuss project timelines and deliverables.',
    participants: ['Alice', 'Bob', 'Charlie'],
    location: 'Conference Room A',
    time: '10:00 AM - 11:00 AM'
  },
  isOpen: true,
  isLoading: false,
  error: ''
};

export const Open = Template.bind({});
Open.args = {
  ...Default.args,
  isOpen: true
};

export const Closed = Template.bind({});
Closed.args = {
  ...Default.args,
  isOpen: false
};

export const Loading = Template.bind({});
Loading.args = {
  ...Default.args,
  isLoading: true
};

export const Error = Template.bind({});
Error.args = {
  ...Default.args,
  error: 'Failed to load event details.'
};