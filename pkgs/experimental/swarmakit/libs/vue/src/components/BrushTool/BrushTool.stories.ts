import BrushTool from './BrushTool.vue';
import { Meta, StoryFn } from '@storybook/vue3';

export default {
  title: 'component/Drawing/BrushTool',
  component: BrushTool,
  tags: ['autodocs'],
} as Meta;

const Template: StoryFn = (args) => ({
  components: { BrushTool },
  setup() {
    return { args };
  },
  template: '<BrushTool v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {};

export const Active = Template.bind({});
Active.args = {
  isActive: true,
};

export const Disabled = Template.bind({});
Disabled.args = {
  isActive: false,
};