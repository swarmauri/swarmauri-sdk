import { Meta, StoryFn } from '@storybook/vue3';
import TreeviewList from './TreeviewList.vue';

export default {
  title: 'component/Lists/TreeviewList',
  component: TreeviewList,
  tags: ['autodocs'],
  argTypes: {
    nodes: { control: 'object' },
  },
} as Meta<typeof TreeviewList>;

const Template: StoryFn<typeof TreeviewList> = (args) => ({
  components: { TreeviewList },
  setup() {
    return { args };
  },
  template: `
    <TreeviewList v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  nodes: [
    { id: 1, label: 'Node 1', expanded: false },
    { id: 2, label: 'Node 2', expanded: false },
    { id: 3, label: 'Node 3', expanded: true, children: [
      { id: 4, label: 'Child Node 1' },
      { id: 5, label: 'Child Node 2' }
    ]},
  ],
};

export const NodeExpanded = Template.bind({});
NodeExpanded.args = {
  nodes: [
    { id: 1, label: 'Node 1', expanded: true, children: [
      { id: 2, label: 'Child Node 1' },
      { id: 3, label: 'Child Node 2' }
    ]},
  ],
};

export const NodeCollapsed = Template.bind({});
NodeCollapsed.args = {
  nodes: [
    { id: 1, label: 'Node 1', expanded: false },
  ],
};

export const Hover = Template.bind({});
Hover.args = {
  ...Default.args,
};

export const Selected = Template.bind({});
Selected.args = {
  nodes: [
    { id: 1, label: 'Node 1', selected: true },
    { id: 2, label: 'Node 2' },
  ],
};