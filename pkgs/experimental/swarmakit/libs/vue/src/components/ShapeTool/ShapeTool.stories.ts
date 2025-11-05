import ShapeTool from './ShapeTool.vue';
import { Meta, StoryFn } from '@storybook/vue3';

export default {
  title: 'component/Drawing/ShapeTool',
  component: ShapeTool,
  tags: ['autodocs'],
} as Meta;

const Template: StoryFn = (args) => ({
  components: { ShapeTool },
  setup() {
    return { args };
  },
  template: '<ShapeTool v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {};

export const Active = Template.bind({});
Active.args = {
  isActive: true,
};

export const ShapeSelected = Template.bind({});
ShapeSelected.args = {
  isActive: true,
  selectedShape: 'circle',
};

export const ShapeDrawn = Template.bind({});
ShapeDrawn.args = {
  isActive: true,
  selectedShape: 'rectangle',
  size: 80,
  fillColor: '#ff0000',
  borderColor: '#00ff00',
  thickness: 5,
};