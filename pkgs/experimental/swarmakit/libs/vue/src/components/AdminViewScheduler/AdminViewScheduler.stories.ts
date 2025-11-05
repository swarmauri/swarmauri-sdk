import { Meta, StoryFn } from '@storybook/vue3';
import AdminViewScheduler from './AdminViewScheduler.vue';
import { Event } from '../../types/types'; // Ensure this path is correct

export default {
  title: 'Components/AdminViewScheduler',
  component: AdminViewScheduler,
  argTypes: {
    feedbackMessage: {
      control: 'text',
      description: 'A message to show feedback for any action',
    },
    addNewEvent: { action: 'addNewEvent' }, // Add action handlers for events
    editEvent: { action: 'editEvent' },
    deleteEvent: { action: 'deleteEvent' },
  },
} as Meta<typeof AdminViewScheduler>;

const Template: StoryFn<typeof AdminViewScheduler> = (args) => ({
  components: { AdminViewScheduler },
  setup() {
    return { args };
  },
  template: `
    <AdminViewScheduler
      v-bind="args"
      @addNewEvent="args.addNewEvent"
      @editEvent="args.editEvent"
      @deleteEvent="args.deleteEvent"
    />
  `,
});

export const Default = Template.bind({});
Default.args = {
  feedbackMessage: '',
};

export const WithEvents = Template.bind({});
WithEvents.args = {
  feedbackMessage: 'Events loaded successfully!',
  addNewEvent: (event: Event) => console.log('Event added:', event),
  editEvent: (event: Event) => console.log('Event edited:', event),
  deleteEvent: (eventId: number) => console.log('Event deleted:', eventId),
};

export const EventAdded = Template.bind({});
EventAdded.args = {
  feedbackMessage: 'Event added successfully!',
  addNewEvent: (event: Event) => console.log('Custom addNewEvent:', event),
};

export const EventEdited = Template.bind({});
EventEdited.args = {
  feedbackMessage: 'Event edited successfully!',
  editEvent: (event: Event) => console.log('Custom editEvent:', event),
};

export const EventDeleted = Template.bind({});
EventDeleted.args = {
  feedbackMessage: 'Event deleted successfully!',
  deleteEvent: (eventId: number) => console.log('Custom deleteEvent:', eventId),
};
