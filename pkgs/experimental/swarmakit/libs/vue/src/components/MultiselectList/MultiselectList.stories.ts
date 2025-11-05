import { Meta, StoryFn } from '@storybook/vue3';
import MultiselectList from './MultiselectList.vue';

export default {
  title: 'component/Lists/MultiselectList',
  component: MultiselectList,
  tags: ['autodocs'],
  argTypes: {
    items: { control: 'object' },
  },
} as Meta<typeof MultiselectList>;

const Template: StoryFn<typeof MultiselectList> = (args) => ({
  components: { MultiselectList },
  setup() {
    return { args };
  },
  template: `
    <MultiselectList v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  items: [
    { value: '1', label: 'Item 1' },
    { value: '2', label: 'Item 2' },
    { value: '3', label: 'Item 3' }
  ],
};

export const ItemSelected = Template.bind({});
ItemSelected.args = {
  ...Default.args,
};
ItemSelected.play = async ({ canvasElement }) => {
  const item = canvasElement.querySelector('.list-item:nth-child(1)') as HTMLElement;
  if(item){
    item.click();
  }
};

export const ItemDeselected = Template.bind({});
ItemDeselected.args = {
  ...Default.args,
};
ItemDeselected.play = async ({ canvasElement }) => {
  const item = canvasElement.querySelector('.list-item:nth-child(1)') as HTMLElement;
  if(item){
    item.click();
    item.click();
  }
};

export const Disabled = Template.bind({});
Disabled.args = {
  items: [
    { value: '1', label: 'Item 1' },
    { value: '2', label: 'Item 2', disabled: true },
    { value: '3', label: 'Item 3' }
  ],
};

export const Hover = Template.bind({});
Hover.args = {
  ...Default.args,
};
Hover.play = async ({ canvasElement }) => {
  const item = canvasElement.querySelector('.list-item:nth-child(1)') as HTMLElement;
  item.dispatchEvent(new Event('mouseover'));
};