import { Meta, StoryFn } from '@storybook/vue3';
import ScrollableList from './ScrollableList.vue';

export default {
  title: 'component/Lists/ScrollableList',
  component: ScrollableList,
  tags: ['autodocs'],
  argTypes: {
    items: { control: 'object' },
    disabled: { control: 'boolean' },
  },
} as Meta<typeof ScrollableList>;

const Template: StoryFn<typeof ScrollableList> = (args) => ({
  components: { ScrollableList },
  setup() {
    return { args };
  },
  template: `
    <ScrollableList v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  items: Array.from({ length: 20 }, (_, i) => ({ id: i, label: `Item ${i + 1}` })),
  disabled: false,
};

export const Scrolling = Template.bind({});
Scrolling.args = {
  ...Default.args,
};

export const EndOfList = Template.bind({});
EndOfList.args = {
  ...Default.args,
};

export const Hover = Template.bind({});
Hover.args = {
  ...Default.args,
};
Hover.play = async ({ canvasElement }) => {
  const item = canvasElement.querySelector('.scrollable-list-item:nth-child(2)');
  if(item){
    item.dispatchEvent(new Event('mouseover'));
  }
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Default.args,
  disabled: true,
};