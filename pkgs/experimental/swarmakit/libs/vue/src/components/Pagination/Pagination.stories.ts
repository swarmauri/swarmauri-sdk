import { Meta, StoryFn } from '@storybook/vue3';
import Pagination from './Pagination.vue';

export default {
  title: 'component/Lists/Pagination',
  component: Pagination,
  tags: ['autodocs'],
  argTypes: {
    totalPages: { control: 'number' },
    currentPage: { control: 'number' },
  },
} as Meta<typeof Pagination>;

const Template: StoryFn<typeof Pagination> = (args) => ({
  components: { Pagination },
  setup() {
    return { args };
  },
  template: `
    <Pagination v-bind="args" @update:currentPage="args.currentPage = $event" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  totalPages: 5,
  currentPage: 1,
};

export const Active = Template.bind({});
Active.args = {
  ...Default.args,
  currentPage: 3,
};

export const Inactive = Template.bind({});
Inactive.args = {
  ...Default.args,
  currentPage: 1,
};

export const Hover = Template.bind({});
Hover.args = {
  ...Default.args,
};
Hover.play = async ({ canvasElement }) => {
  const item = canvasElement.querySelector('.pagination-item:nth-child(2)');
  if(item){
    item.dispatchEvent(new Event('mouseover'));
  }
};