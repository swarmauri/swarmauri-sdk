import TaskCompletionCheckList from './TaskCompletionCheckList.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<TaskCompletionCheckList> = {
  title: 'component/Indicators/TaskCompletionCheckList',
  component: TaskCompletionCheckList,
  tags: ['autodocs'],
  argTypes: {
    tasks: { control: 'object' }
  },
  parameters: {
    layout: 'centered',
    viewport: {
      viewports: {
        smallMobile: { name: 'Small Mobile', styles: { width: '320px', height: '568px' } },
        largeMobile: { name: 'Large Mobile', styles: { width: '414px', height: '896px' } },
        tablet: { name: 'Tablet', styles: { width: '768px', height: '1024px' } },
        desktop: { name: 'Desktop', styles: { width: '1024px', height: '768px' } },
      }
    }
  }
};

export default meta;

const Template:StoryFn<TaskCompletionCheckList> = (args) => ({
  Component:TaskCompletionCheckList,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  tasks: [
    { id: 1, label: 'Task 1', completed: false },
    { id: 2, label: 'Task 2', completed: false },
    { id: 3, label: 'Task 3', completed: false }
  ]
};

export const Checked = Template.bind({});
Checked.args = {
  tasks: [
    { id: 1, label: 'Task 1', completed: true },
    { id: 2, label: 'Task 2', completed: true },
    { id: 3, label: 'Task 3', completed: true }
  ]
};

export const Unchecked = Template.bind({});
Unchecked.args = {
  tasks: [
    { id: 1, label: 'Task 1', completed: false },
    { id: 2, label: 'Task 2', completed: false },
    { id: 3, label: 'Task 3', completed: false }
  ]
};

export const PartiallyComplete = Template.bind({});
PartiallyComplete.args = {
  tasks: [
    { id: 1, label: 'Task 1', completed: true },
    { id: 2, label: 'Task 2', completed: false },
    { id: 3, label: 'Task 3', completed: true }
  ]
};