import SortableTable from './SortableTable.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';
import type { TableColumn, TableRow } from './SortableTable.svelte';

const meta: Meta<SortableTable> = {
  title: 'Components/Lists/SortableTable',
  component: SortableTable,
  tags: ['autodocs'],
  argTypes: {
    columns: {
      control: { type: 'object' },
    },
    rows: {
      control: { type: 'object' },
    },
  },
};

export default meta;

const Template: StoryFn = (args) => ({
  Component: SortableTable,
  props: args,
});

const sampleColumns: TableColumn[] = [
  { key: 'id', label: 'ID', sortable: true },
  { key: 'name', label: 'Name', sortable: true },
  { key: 'age', label: 'Age', sortable: true },
];

const sampleRows: TableRow[] = [
  { id: 1, name: 'Alice', age: 30 },
  { id: 2, name: 'Bob', age: 25 },
  { id: 3, name: 'Charlie', age: 35 },
];

export const Default = Template.bind({});
Default.args = {
  columns: sampleColumns,
  rows: sampleRows,
};

export const Sorting = Template.bind({});
Sorting.args = {
  columns: sampleColumns,
  rows: sampleRows,
};

export const Filtering = Template.bind({});
Filtering.args = {
  columns: sampleColumns,
  rows: sampleRows,
};

export const RowSelection = Template.bind({});
RowSelection.args = {
  columns: sampleColumns,
  rows: sampleRows,
};