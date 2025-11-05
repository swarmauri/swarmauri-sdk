import { Meta, StoryFn } from '@storybook/vue3';
import Tabs from './Tabs.vue';

export default {
  title: 'component/Lists/Tabs',
  component: Tabs,
  tags: ['autodocs'],
  argTypes: {
    tabs: { control: 'object' },
    initialActiveIndex: { control: 'number' },
  },
} as Meta<typeof Tabs>;

const Template: StoryFn<typeof Tabs> = (args) => ({
  components: { Tabs },
  setup() {
    return { args };
  },
  template: `
    <Tabs v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  tabs: [
    { id: 1, label: 'Tab 1' },
    { id: 2, label: 'Tab 2' },
    { id: 3, label: 'Tab 3' },
  ],
  initialActiveIndex: 0,
};

export const Active = Template.bind({});
Active.args = {
  ...Default.args,
  initialActiveIndex: 1,
};

export const Inactive = Template.bind({});
Inactive.args = {
  ...Default.args,
  initialActiveIndex: -1,
};

export const Disabled = Template.bind({});
Disabled.args = {
  tabs: [
    { id: 1, label: 'Tab 1', disabled: true },
    { id: 2, label: 'Tab 2' },
    { id: 3, label: 'Tab 3' },
  ],
  initialActiveIndex: 1,
};

export const Hover = Template.bind({});
Hover.args = {
  ...Default.args,
};