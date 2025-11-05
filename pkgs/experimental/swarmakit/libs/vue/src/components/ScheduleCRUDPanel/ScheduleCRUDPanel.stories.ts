import { Meta, StoryFn } from '@storybook/vue3';
import ScheduleCRUDPanel from './ScheduleCRUDPanel.vue';

export default {
  title: 'component/Scheduling/ScheduleCRUDPanel',
  component: ScheduleCRUDPanel,
  tags: ['autodocs']
} as Meta<typeof ScheduleCRUDPanel>;

const Template: StoryFn<typeof ScheduleCRUDPanel> = (args) => ({
  components: { ScheduleCRUDPanel },
  setup() {
    return { args };
  },
  template: '<ScheduleCRUDPanel v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {};

export const EventCreated = Template.bind({});
EventCreated.args = {
  feedbackMessageProp: 'Event "Meeting with Team" created successfully.'
};

export const EventUpdated = Template.bind({});
EventUpdated.args = {
  feedbackMessageProp: 'Event "Project Deadline" updated successfully.'
};

export const EventDeleted = Template.bind({});
EventDeleted.args = {
  feedbackMessageProp: 'Event "Client Call" deleted successfully.'
};