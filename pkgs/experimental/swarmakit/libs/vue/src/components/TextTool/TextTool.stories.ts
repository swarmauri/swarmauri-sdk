import TextTool from './TextTool.vue';
import { Meta, StoryFn } from '@storybook/vue3';

export default {
  title: 'component/Drawing/TextTool',
  component: TextTool,
  tags: ['autodocs'],
} as Meta;

const Template: StoryFn = (args) => ({
  components: { TextTool },
  setup() {
    return { args };
  },
  template: '<TextTool v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  isActive: false,
  fontStyle: 'Arial',
  fontSize: 16,
  fontColor: '#000000',
  alignment: 'left',
};

export const Active = Template.bind({});
Active.args = {
  isActive: true,
  fontStyle: 'Arial',
  fontSize: 16,
  fontColor: '#000000',
  alignment: 'left',
};

export const TextAdded = Template.bind({});
TextAdded.args = {
  isActive: true,
  fontStyle: 'Verdana',
  fontSize: 18,
  fontColor: '#FF5733',
  alignment: 'center',
};

export const TextEdited = Template.bind({});
TextEdited.args = {
  isActive: true,
  fontStyle: 'Times New Roman',
  fontSize: 20,
  fontColor: '#3333FF',
  alignment: 'right',
};