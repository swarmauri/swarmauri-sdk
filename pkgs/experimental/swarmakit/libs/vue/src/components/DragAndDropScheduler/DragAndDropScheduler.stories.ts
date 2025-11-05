import { Meta, StoryFn } from '@storybook/vue3';
import DragAndDropScheduler from './DragAndDropScheduler.vue';

export default {
  title: 'component/Scheduling/DragAndDropScheduler',
  component: DragAndDropScheduler,
  tags: ['autodocs']
} as Meta<typeof DragAndDropScheduler>;

const Template: StoryFn<typeof DragAndDropScheduler> = (args) => ({
  components: { DragAndDropScheduler },
  setup() {
    return { args };
  },
  template: '<DragAndDropScheduler v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {};

export const EventDragging = Template.bind({});
EventDragging.args = {
  events: [
    { id: 1, title: 'Meeting', position: 0, duration: 60, isDragging: true }
  ]
};

export const EventDropped = Template.bind({});
EventDropped.args = {
  events: [
    { id: 1, title: 'Meeting', position: 120, duration: 60, isDragging: false }
  ]
};

export const EventRescheduled = Template.bind({});
EventRescheduled.args = {
  events: [
    { id: 1, title: 'Meeting', position: 180, duration: 90, isDragging: false }
  ]
};