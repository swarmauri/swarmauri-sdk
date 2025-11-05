import { Meta, StoryFn } from '@storybook/vue3';
import ExpandableList from './ExpandableList.vue';

export default {
  title: 'component/Lists/ExpandableList',
  component: ExpandableList,
  tags: ['autodocs'],
  argTypes: {
    items: { control: 'object' },
  },
} as Meta<typeof ExpandableList>;

const Template: StoryFn<typeof ExpandableList> = (args) => ({
  components: { ExpandableList },
  setup() {
    return { args };
  },
  template: `
    <ExpandableList v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  items: [
    { title: 'Item 1', content: 'Content for item 1' },
    { title: 'Item 2', content: 'Content for item 2' },
    { title: 'Item 3', content: 'Content for item 3' },
  ],
};

export const ItemExpanded = Template.bind({});
ItemExpanded.args = {
  ...Default.args,
};

export const ItemCollapsed = Template.bind({});
ItemCollapsed.args = {
  ...Default.args,
};

export const Hover = Template.bind({});
Hover.args = {
  ...Default.args,
};

export const Selected = Template.bind({});
Selected.args = {
  ...Default.args,
};