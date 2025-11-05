import { Meta, StoryFn } from '@storybook/vue3';
import FilterableList from './FilterableList.vue';

export default {
  title: 'component/Lists/FilterableList',
  component: FilterableList,
  tags: ['autodocs'],
  argTypes: {
    items: { control: 'object' },
  },
} as Meta<typeof FilterableList>;

const Template: StoryFn<typeof FilterableList> = (args) => ({
  components: { FilterableList },
  setup() {
    return { args };
  },
  template: `
    <FilterableList v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  items: ['Apple', 'Banana', 'Cherry', 'Date', 'Elderberry'],
};

export const FilterApplied = Template.bind({});
FilterApplied.args = {
  ...Default.args,
};
FilterApplied.play = async ({ canvasElement }) => {
  const input = canvasElement.querySelector('input');
  if(input){
    input.value = 'Banana';
    input.dispatchEvent(new Event('input'));
  }
};

export const NoResults = Template.bind({});
NoResults.args = {
  ...Default.args,
};
NoResults.play = async ({ canvasElement }) => {
  const input = canvasElement.querySelector('input');
  if(input){
    input.value = 'Zucchini';
    input.dispatchEvent(new Event('input'));
  }
};

export const ClearFilter = Template.bind({});
ClearFilter.args = {
  ...Default.args,
};
ClearFilter.play = async ({ canvasElement }) => {
  const input = canvasElement.querySelector('input');
  if(input){
    input.value = 'Banana';
    input.dispatchEvent(new Event('input'));
  }
  const button = canvasElement.querySelector('button') as HTMLElement;
  button.click();
};