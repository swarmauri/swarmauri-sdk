import PaginationControl from './PaginationControl.vue';
import {Meta,StoryFn} from '@storybook/vue3';

export default {
  title: 'components/Data/PaginationControl',
  component: PaginationControl,
  tags: ['autodocs'],
} as Meta<typeof PaginationControl>;

const Template:StoryFn<typeof PaginationControl> = (args: any) => ({
  components: { PaginationControl },
  setup() {
    return { args };
  },
  template: '<PaginationControl v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  totalPages: 10,
  currentPage: 1,
  rowsPerPageOptions: [10, 20, 50, 100],
};

export const PageSelected = Template.bind({});
PageSelected.args = {
  ...Default.args,
  currentPage: 5,
};

export const FirstPage = Template.bind({});
FirstPage.args = {
  ...Default.args,
  currentPage: 1,
};

export const LastPage = Template.bind({});
LastPage.args = {
  ...Default.args,
  currentPage: 10,
};