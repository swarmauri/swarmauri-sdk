import TreeviewList from './TreeviewList.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta = {
  title: 'Components/Lists/TreeviewList',
  component: TreeviewList,
  tags: ['autodocs'],
  argTypes: {
    nodes: {
      control: { type: 'object' },
    },
  },
};

export default meta;

const Template: StoryFn = (args) => ({
  Component: TreeviewList,
  props: args,
});

const sampleNodes = [
  { label: 'Node 1', expanded: true, selected: false, children: [
    { label: 'Child 1.1', expanded: false, selected: false },
    { label: 'Child 1.2', expanded: false, selected: false }
  ]},
  { label: 'Node 2', expanded: false, selected: false, children: [
    { label: 'Child 2.1', expanded: false, selected: false }
  ]},
  { label: 'Node 3', expanded: false, selected: false }
];

export const Default = Template.bind({});
Default.args = {
  nodes: sampleNodes,
};

export const NodeExpanded = Template.bind({});
NodeExpanded.args = {
  nodes: sampleNodes.map((node, i) => ({ ...node, expanded: i === 0 })),
};

export const NodeCollapsed = Template.bind({});
NodeCollapsed.args = {
  nodes: sampleNodes.map((node) => ({ ...node, expanded: false })),
};

export const Hover = Template.bind({});
Hover.args = {
  nodes: sampleNodes,
};

export const Selected = Template.bind({});
Selected.args = {
  nodes: sampleNodes.map((node, i) => ({ ...node, selected: i === 1 })),
};