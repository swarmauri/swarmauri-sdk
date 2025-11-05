import { Meta, StoryFn } from '@storybook/vue3';
import DataGrid from './DataGrid.vue';

export default {
  title: 'component/Lists/DataGrid',
  component: DataGrid,
  tags: ['autodocs'],
} as Meta;

const Template: StoryFn<typeof DataGrid> = (args) => ({
  components: { DataGrid },
  setup() {
    return { args };
  },
  template: `
    <DataGrid v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  headers: ['Name', 'Age', 'Occupation'],
  data: [
    ['Alice', '30', 'Engineer'],
    ['Bob', '25', 'Designer'],
    ['Charlie', '35', 'Teacher'],
  ],
  paginationEnabled: false,
  searchEnabled: false,
  resizable: false,
};

export const Paginated = Template.bind({});
Paginated.args = {
  ...Default.args,
  paginationEnabled: true,
  itemsPerPage: 1,
};

export const Search = Template.bind({});
Search.args = {
  ...Default.args,
  searchEnabled: true,
};

export const Resizable = Template.bind({});
Resizable.args = {
  ...Default.args,
  resizable: true,
};