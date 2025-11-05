import Tabs from './Tabs.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta = {
  title: 'Components/Lists/Tabs',
  component: Tabs,
  tags: ['autodocs'],
  argTypes: {
    tabs: {
      control: { type: 'object' },
    },
    activeIndex: {
      control: { type: 'number' },
    },
  },
};

export default meta;

const Template: StoryFn = (args) => ({
  Component: Tabs,
  props: args,
});

const sampleTabs = [
  { label: 'Tab 1', content: 'Content for Tab 1' },
  { label: 'Tab 2', content: 'Content for Tab 2' },
  { label: 'Tab 3', content: 'Content for Tab 3', disabled: true },
];

export const Default = Template.bind({});
Default.args = {
  tabs: sampleTabs,
  activeIndex: 0,
};

export const Active = Template.bind({});
Active.args = {
  tabs: sampleTabs,
  activeIndex: 1,
};

export const Inactive = Template.bind({});
Inactive.args = {
  tabs: sampleTabs,
  activeIndex: 2,
};

export const Disabled = Template.bind({});
Disabled.args = {
  tabs: sampleTabs,
  activeIndex: 0,
};

export const Hover = Template.bind({});
Hover.args = {
  tabs: sampleTabs,
  activeIndex: 0,
};