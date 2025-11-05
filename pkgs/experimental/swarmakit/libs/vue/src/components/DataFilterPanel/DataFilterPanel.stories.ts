import DataFilterPanel from './DataFilterPanel.vue';
import { Meta, StoryFn} from '@storybook/vue3'

export default {
  title: 'components/Data/DataFilterPanel',
  component: DataFilterPanel,
  tags: ['autodocs'],
} as Meta

const Template:StoryFn = (args: any) => ({
  components: { DataFilterPanel },
  setup() {
    return { args };
  },
  template: '<DataFilterPanel v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  filters: [
    { type: 'text', label: 'Name', value: '' },
    { type: 'dropdown', label: 'Category', options: ['Category 1', 'Category 2'], value: '' },
    { type: 'date', label: 'Date', value: null },
  ],
  disabled: false,
};

export const FilterApplied = Template.bind({});
FilterApplied.args = {
  ...Default.args,
  filters: [
    { type: 'text', label: 'Name', value: 'John' },
    { type: 'dropdown', label: 'Category', options: ['Category 1', 'Category 2'], value: 'Category 1' },
    { type: 'date', label: 'Date', value: new Date().toISOString().split('T')[0] },
  ],
};

export const FilterCleared = Template.bind({});
FilterCleared.args = {
  ...Default.args,
  filters: [
    { type: 'text', label: 'Name', value: '' },
    { type: 'dropdown', label: 'Category', options: ['Category 1', 'Category 2'], value: '' },
    { type: 'date', label: 'Date', value: null },
  ],
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Default.args,
  disabled: true,
};