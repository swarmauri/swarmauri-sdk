import { Meta, StoryFn } from '@storybook/vue3';
import NumberedList from './NumberedList.vue';

export default {
  title: 'component/Lists/NumberedList',
  component: NumberedList,
  tags: ['autodocs'],
  argTypes: {
    items: { control: 'object' },
  },
} as Meta<typeof NumberedList>;

const Template: StoryFn<typeof NumberedList> = (args) => ({
  components: { NumberedList },
  setup() {
    return { args };
  },
  template: `
    <NumberedList v-bind="args" />
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

export const Selected = Template.bind({});
Selected.args = {
  ...Default.args,
};
Selected.play = async ({ canvasElement }) => {
  const item = canvasElement.querySelector('.list-item:nth-child(1)') as HTMLElement;
  if(item){
    item.click();
  }
};

export const Hover = Template.bind({});
Hover.args = {
  ...Default.args,
};
Hover.play = async ({ canvasElement }) => {
  const item = canvasElement.querySelector('.list-item:nth-child(1)') as HTMLElement;
  if(item){
    item.dispatchEvent(new Event('mouseover'));
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