import TimelineList from './TimelineList.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta = {
  title: 'Components/Lists/TimelineList',
  component: TimelineList,
  tags: ['autodocs'],
  argTypes: {
    events: {
      control: { type: 'object' },
    },
  },
};

export default meta;

const Template: StoryFn = (args) => ({
  Component: TimelineList,
  props: args,
});

const sampleEvents = [
  { title: 'Event 1', description: 'Description for Event 1', completed: true, active: false },
  { title: 'Event 2', description: 'Description for Event 2', completed: false, active: true },
  { title: 'Event 3', description: 'Description for Event 3', completed: false, active: false },
];

export const Default = Template.bind({});
Default.args = {
  events: sampleEvents,
};

export const Active = Template.bind({});
Active.args = {
  events: sampleEvents.map((event, i) => ({ ...event, active: i === 1 })),
};

export const Completed = Template.bind({});
Completed.args = {
  events: sampleEvents.map((event) => ({ ...event, completed: true })),
};

export const Hover = Template.bind({});
Hover.args = {
  events: sampleEvents,
};

export const Inactive = Template.bind({});
Inactive.args = {
  events: sampleEvents.map((event) => ({ ...event, active: false })),
};