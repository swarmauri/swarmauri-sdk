import { Meta, StoryFn } from '@storybook/vue3';
import TimelineList from './TimelineList.vue';

export default {
  title: 'component/Lists/TimelineList',
  component: TimelineList,
  tags: ['autodocs'],
  argTypes: {
    items: { control: 'object' },
    activeIndex: { control: 'number' },
  },
} as Meta<typeof TimelineList>;

const Template: StoryFn<typeof TimelineList> = (args) => ({
  components: { TimelineList },
  setup() {
    return { args };
  },
  template: `
    <TimelineList v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  items: [
    { id: 1, label: 'Step 1' },
    { id: 2, label: 'Step 2' },
    { id: 3, label: 'Step 3' },
  ],
  activeIndex: 0,
};

export const Active = Template.bind({});
Active.args = {
  ...Default.args,
  activeIndex: 1,
};

export const Completed = Template.bind({});
Completed.args = {
  items: [
    { id: 1, label: 'Step 1', completed: true },
    { id: 2, label: 'Step 2', completed: true },
    { id: 3, label: 'Step 3' },
  ],
  activeIndex: 2,
};

export const Hover = Template.bind({});
Hover.args = {
  ...Default.args,
};

export const Inactive = Template.bind({});
Inactive.args = {
  items: [
    { id: 1, label: 'Step 1' },
    { id: 2, label: 'Step 2' },
    { id: 3, label: 'Step 3' },
  ],
  activeIndex: -1,
};