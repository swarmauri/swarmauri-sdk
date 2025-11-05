import FillTool from './FillTool.vue';
import { Meta, StoryFn } from '@storybook/vue3';

export default {
  title: 'component/Drawing/FillTool',
  component: FillTool,
  tags: ['autodocs'],
} as Meta;

const Template: StoryFn = (args) => ({
  components: { FillTool },
  setup() {
    return { args };
  },
  template: '<FillTool v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  isActive: false,
  isDisabled: false,
  tolerance: 50,
};

export const Active = Template.bind({});
Active.args = {
  isActive: true,
  isDisabled: false,
  tolerance: 50,
};

export const Disabled = Template.bind({});
Disabled.args = {
  isActive: false,
  isDisabled: true,
  tolerance: 50,
};