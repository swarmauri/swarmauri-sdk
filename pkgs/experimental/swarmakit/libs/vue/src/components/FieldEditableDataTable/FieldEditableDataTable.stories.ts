import FieldEditableDataTable from './FieldEditableDataTable.vue';
import {Meta,StoryFn} from '@storybook/vue3';

export default {
  title: 'components/Data/FieldEditableDataTable',
  component: FieldEditableDataTable,
  tags: ['autodocs'],
} as Meta;

const Template:StoryFn = (args: any) => ({
  components: { FieldEditableDataTable },
  setup() {
    return { args };
  },
  template: '<FieldEditableDataTable v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {};

export const FieldEditing = Template.bind({});
FieldEditing.args = { editingField: { rowId: '1', field: 'name' } };

export const FieldEdited = Template.bind({});
FieldEdited.args = { editingField: { rowId: '1', field: 'description' }, fieldValues: { description: 'Edited text' } };

export const FieldSaved = Template.bind({});
FieldSaved.args = {};

export const Error = Template.bind({});
Error.args = { error: 'Error saving data' };