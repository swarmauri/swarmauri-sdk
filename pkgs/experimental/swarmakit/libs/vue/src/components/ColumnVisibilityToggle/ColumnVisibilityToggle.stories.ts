import ColumnVisibilityToggle from './ColumnVisibilityToggle.vue';
import { Meta , StoryFn} from '@storybook/vue3'

export default {
  title: 'components/Data/ColumnVisibilityToggle',
  component: ColumnVisibilityToggle,
  tags: ['autodocs'],
} as Meta

const Template:StoryFn = (args: any) => ({
  components: { ColumnVisibilityToggle },
  setup() {
    return { args };
  },
  template: '<ColumnVisibilityToggle v-bind="args" @update:columns="args.onUpdateColumns" />',
});

export const Default = Template.bind({});
Default.args = {
  columns: [
    { name: 'Name', visible: true },
    { name: 'Age', visible: true },
    { name: 'Email', visible: true },
  ],
  onUpdateColumns: (updatedColumns: any) => {
    console.log(updatedColumns);
  },
};

export const ColumnHidden = Template.bind({});
ColumnHidden.args = {
  columns: [
    { name: 'Name', visible: true },
    { name: 'Age', visible: false },
    { name: 'Email', visible: true },
  ],
  onUpdateColumns: (updatedColumns: any) => {
    console.log(updatedColumns);
  },
};

export const ColumnVisible = Template.bind({});
ColumnVisible.args = {
  columns: [
    { name: 'Name', visible: true },
    { name: 'Age', visible: true },
    { name: 'Email', visible: true },
  ],
  onUpdateColumns: (updatedColumns: any) => {
    console.log(updatedColumns);
  },
};