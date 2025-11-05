import FileUpload from './FileUpload.vue';
import {Meta,StoryFn} from '@storybook/vue3'

export default {
  component: FileUpload,
  title: 'component/Forms/FileUpload',
  tags: ['autodocs'],
  argTypes: {
    multiple: {
      control: { type: 'boolean' },
    },
  },
}as Meta;

const Template:StoryFn = (args) => ({
  components: { FileUpload },
  setup() {
    return { args };
  },
  template: '<FileUpload v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  multiple: false,
};

export const SingleFile = Template.bind({});
SingleFile.args = {
  multiple: false,
};

export const MultipleFiles = Template.bind({});
MultipleFiles.args = {
  multiple: true,
};

export const DragAndDrop = Template.bind({});
DragAndDrop.args = {
  multiple: false,
};

export const Progress = Template.bind({});
Progress.args = {
  multiple: false,
};