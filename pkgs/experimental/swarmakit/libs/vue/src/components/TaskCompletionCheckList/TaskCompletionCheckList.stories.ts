import { Meta, StoryFn } from '@storybook/vue3';
import TaskCompletionCheckList from './TaskCompletionCheckList.vue';

export default {
  title: 'component/Indicators/TaskCompletionCheckList',
  component: TaskCompletionCheckList,
  tags: ['autodocs'],
  argTypes: {
    tasks: {
      control: 'object',
    },
  },
} as Meta<typeof TaskCompletionCheckList>;

const Template: StoryFn<typeof TaskCompletionCheckList> = (args) => ({
  components: { TaskCompletionCheckList },
  setup() {
    return { args };
  },
  template: `<TaskCompletionCheckList v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  tasks: [
    { label: 'Task 1', status: 'unchecked' },
    { label: 'Task 2', status: 'partiallyComplete' },
    { label: 'Task 3', status: 'checked' },
  ],
};

export const Checked = Template.bind({});
Checked.args = {
  tasks: [
    { label: 'Task 1', status: 'checked' },
    { label: 'Task 2', status: 'checked' },
    { label: 'Task 3', status: 'checked' },
  ],
};

export const Unchecked = Template.bind({});
Unchecked.args = {
  tasks: [
    { label: 'Task 1', status: 'unchecked' },
    { label: 'Task 2', status: 'unchecked' },
    { label: 'Task 3', status: 'unchecked' },
  ],
};

export const PartiallyComplete = Template.bind({});
PartiallyComplete.args = {
  tasks: [
    { label: 'Task 1', status: 'partiallyComplete' },
    { label: 'Task 2', status: 'partiallyComplete' },
    { label: 'Task 3', status: 'partiallyComplete' },
  ],
};