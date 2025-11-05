import ShapeLibrary from './ShapeLibrary.vue';
import { Meta, StoryFn } from '@storybook/vue3';

export default {
  title: 'component/Drawing/ShapeLibrary',
  component: ShapeLibrary,
  tags: ['autodocs'],
} as Meta;

const Template: StoryFn = (args) => ({
  components: { ShapeLibrary },
  setup() {
    return { args };
  },
  template: '<ShapeLibrary v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  searchQuery: '',
};

export const ShapeSelected = Template.bind({});
ShapeSelected.args = {
  searchQuery: 'Circle',
};

export const ShapeInserted = Template.bind({});
ShapeInserted.args = {
  searchQuery: '',
};