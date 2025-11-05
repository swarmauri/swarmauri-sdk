import { Meta, StoryFn } from '@storybook/vue3';
import GroupedList from './GroupedList.vue';

export default {
  title: 'component/Lists/GroupedList',
  component: GroupedList,
  tags: ['autodocs'],
  argTypes: {
    groups: { control: 'object' },
  },
} as Meta<typeof GroupedList>;

const Template: StoryFn<typeof GroupedList> = (args) => ({
  components: { GroupedList },
  setup() {
    return { args };
  },
  template: `
    <GroupedList v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  groups: [
    { name: 'Fruits', items: ['Apple', 'Banana', 'Cherry'] },
    { name: 'Vegetables', items: ['Carrot', 'Lettuce', 'Spinach'] },
  ],
};

export const GroupExpanded = Template.bind({});
GroupExpanded.args = {
  ...Default.args,
};
GroupExpanded.play = async ({ canvasElement }) => {
  const headers = canvasElement.querySelectorAll('.group-header') as NodeListOf<HTMLElement>;
  headers.forEach(header => header.click());
};

export const GroupCollapsed = Template.bind({});
GroupCollapsed.args = {
  ...Default.args,
};
GroupCollapsed.play = async ({ canvasElement }) => {
  const headers = canvasElement.querySelectorAll('.group-header') as NodeListOf<HTMLElement>;
  headers.forEach(header => header.click());
  headers.forEach(header => header.click());
};

export const ItemHover = Template.bind({});
ItemHover.args = {
  ...Default.args,
};

export const ItemSelected = Template.bind({});
ItemSelected.args = {
  ...Default.args,
};
ItemSelected.play = async ({ canvasElement }) => {
  const items = canvasElement.querySelectorAll('.list-item') as NodeListOf<HTMLElement>;
  items[0].click();
};