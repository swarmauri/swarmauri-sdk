import ZoomTool from './ZoomTool.vue';
import { Meta, StoryFn } from '@storybook/vue3';

export default {
  title: 'component/Drawing/ZoomTool',
  component: ZoomTool,
  tags: ['autodocs'],
} as Meta;

const Template: StoryFn = (args) => ({
  components: { ZoomTool },
  setup() {
    return { args };
  },
  template: '<ZoomTool v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  zoomLevel: 100,
};

export const ZoomIn = Template.bind({});
ZoomIn.args = {
  zoomLevel: 150,
};

export const ZoomOut = Template.bind({});
ZoomOut.args = {
  zoomLevel: 50,
};

export const FitToScreen = Template.bind({});
FitToScreen.args = {
  zoomLevel: 100,
};

export const Reset = Template.bind({});
Reset.args = {
  zoomLevel: 100,
};