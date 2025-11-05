import { Meta, StoryFn } from '@storybook/vue3';
import SortableTable from './SortableTable.vue';

export default {
  title: 'component/Lists/SortableTable',
  component: SortableTable,
  tags: ['autodocs'],
  argTypes: {
    columns: { control: 'object' },
    data: { control: 'object' },
  },
} as Meta<typeof SortableTable>;

const Template: StoryFn<typeof SortableTable> = (args) => ({
  components: { SortableTable },
  setup() {
    return { args };
  },
  template: `
    <SortableTable v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  columns: [
    { key: 'name', label: 'Name' },
    { key: 'age', label: 'Age' },
    { key: 'city', label: 'City' },
  ],
  data: [
    { id: 1, name: 'Alice', age: 30, city: 'New York' },
    { id: 2, name: 'Bob', age: 25, city: 'San Francisco' },
    { id: 3, name: 'Charlie', age: 35, city: 'Los Angeles' },
  ],
};

export const Sorting = Template.bind({});
Sorting.args = {
  ...Default.args,
};
Sorting.play = async ({ canvasElement }) => {
  const th = canvasElement.querySelector('th') as HTMLElement;
  if(th){
    th.click();
  }
};

export const Filtering = Template.bind({});
Filtering.args = {
  ...Default.args,
};
Filtering.play = async ({ canvasElement }) => {
  const input = canvasElement.querySelector('.filter-input') as HTMLInputElement;
  if(input){
    input.value = 'Alice';
    input.dispatchEvent(new Event('input')); 
  }
};

export const RowSelection = Template.bind({});
RowSelection.args = {
  ...Default.args,
};
RowSelection.play = async ({ canvasElement }) => {
  const row = canvasElement.querySelector('tbody tr:nth-child(1)') as HTMLElement;
  if(row){
    row.click();
  }
};