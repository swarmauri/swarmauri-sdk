import { Meta, StoryFn } from '@storybook/vue3';
import PinnedList from './PinnedList.vue';

export default {
  title: 'component/Lists/PinnedList',
  component: PinnedList,
  tags: ['autodocs'],
  argTypes: {
    items: { control: 'object' },
    selectedItem: { control: 'number' },
  },
} as Meta<typeof PinnedList>;

const Template: StoryFn<typeof PinnedList> = (args) => ({
  components: { PinnedList },
  setup() {
    return { args };
  },
  template: `
    <PinnedList v-bind="args" @update:selectedItem="args.selectedItem = $event" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  items: [
    { id: 1, label: 'Item 1', pinned: false },
    { id: 2, label: 'Item 2', pinned: true },
    { id: 3, label: 'Item 3', pinned: false },
  ],
  selectedItem: 1,
};

export const Pinned = Template.bind({});
Pinned.args = {
  ...Default.args,
  items: [
    { id: 1, label: 'Item 1', pinned: true },
    { id: 2, label: 'Item 2', pinned: true },
    { id: 3, label: 'Item 3', pinned: false },
  ],
};

export const Unpinned = Template.bind({});
Unpinned.args = {
  ...Default.args,
  items: [
    { id: 1, label: 'Item 1', pinned: false },
    { id: 2, label: 'Item 2', pinned: false },
    { id: 3, label: 'Item 3', pinned: false },
  ],
};

export const Hover = Template.bind({});
Hover.args = {
  ...Default.args,
};
Hover.play = async ({ canvasElement }) => {
  const item = canvasElement.querySelector('.pinned-list-item:nth-child(2)');
  if(item){
    item.dispatchEvent(new Event('mouseover'));
  }
};

export const Selected = Template.bind({});
Selected.args = {
  ...Default.args,
  selectedItem: 2,
};