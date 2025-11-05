import { Meta, StoryFn } from '@storybook/vue3';
import SortableList from './SortableList.vue';

export default {
  title: 'component/Lists/SortableList',
  component: SortableList,
  tags: ['autodocs'],
  argTypes: {
    items: { control: 'object' },
    disabled: { control: 'boolean' },
  },
} as Meta<typeof SortableList>;

const Template: StoryFn<typeof SortableList> = (args) => ({
  components: { SortableList },
  setup() {
    return { args };
  },
  template: `
    <SortableList v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  items: [
    { id: 1, label: 'Item 1' },
    { id: 2, label: 'Item 2' },
    { id: 3, label: 'Item 3' },
  ],
  disabled: false,
};

export const Dragging = Template.bind({});
Dragging.args = {
  ...Default.args,
};
Dragging.play = async ({ canvasElement }) => {
  const item = canvasElement.querySelector('li') as HTMLElement;
  if(item){
    item.dispatchEvent(new DragEvent('dragstart'));
  }
};

export const Sorted = Template.bind({});
Sorted.args = {
  items: [
    { id: 3, label: 'Item 3' },
    { id: 1, label: 'Item 1' },
    { id: 2, label: 'Item 2' },
  ],
  disabled: false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Default.args,
  disabled: true,
};