import DataExportButton from './DataExportButton.vue';
import { Meta,StoryFn } from '@storybook/vue3'

export default {
  title: 'components/Data/DataExportButton',
  component: DataExportButton,
  tags: ['autodocs'],
} as Meta;

const Template:StoryFn = (args: any) => ({
  components: { DataExportButton },
  setup() {
    return { args };
  },
  template: '<DataExportButton v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  availableFormats: ['csv', 'excel', 'pdf'],
  dataAvailable: true,
};

export const Exporting = Template.bind({});
Exporting.args = {
  ...Default.args,
  dataAvailable: true,
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Default.args,
  dataAvailable: false,
};