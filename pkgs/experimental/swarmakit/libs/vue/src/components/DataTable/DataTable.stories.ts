import DataTable from './DataTable.vue';
import {Meta,StoryFn} from '@storybook/vue3'

export default {
  title: 'components/Data/DataTable',
  component: DataTable,
  tags: ['autodocs'],
}as Meta;

const Template:StoryFn = (args: any) => ({
  components: { DataTable },
  setup() {
    return { args };
  },
  template: '<DataTable v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  columns: [
    { key: 'name', label: 'Name', sortable: true },
    { key: 'age', label: 'Age', sortable: true },
    { key: 'email', label: 'Email', sortable: false },
  ],
  rows: [
    { id: 1, name: 'John Doe', age: 28, email: 'john@example.com' },
    { id: 2, name: 'Jane Smith', age: 34, email: 'jane@example.com' },
    { id: 3, name: 'Sam Johnson', age: 45, email: 'sam@example.com' },
  ],
  loading: false,
  pagination: false,
};

export const Loading = Template.bind({});
Loading.args = {
  ...Default.args,
  loading: true,
};

export const Paginated = Template.bind({});
Paginated.args = {
  ...Default.args,
  pagination: true,
  itemsPerPage: 1,
};

export const Sorted = Template.bind({});
Sorted.args = {
  ...Default.args,
  rows: [
    { id: 1, name: 'Zara Smith', age: 28, email: 'zara@example.com' },
    { id: 2, name: 'Aaron Doe', age: 34, email: 'aaron@example.com' },
    { id: 3, name: 'Liam Johnson', age: 45, email: 'liam@example.com' },
  ],
};

export const Filtered = Template.bind({});
Filtered.args = {
  ...Default.args,
  rows: [
    { id: 1, name: 'John Doe', age: 28, email: 'john@example.com' },
  ],
};

export const RowSelected = Template.bind({});
RowSelected.args = {
  ...Default.args,
  rows: [
    { id: 1, name: 'John Doe', age: 28, email: 'john@example.com', selected: true },
    { id: 2, name: 'Jane Smith', age: 34, email: 'jane@example.com' },
  ],
};