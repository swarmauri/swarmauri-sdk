import LayerPanel from './LayerPanel.vue';
import { Meta, StoryFn } from '@storybook/vue3';

export default {
  title: 'component/Drawing/LayerPanel',
  component: LayerPanel,
  tags: ['autodocs'],
} as Meta;

const Template: StoryFn = (args) => ({
  components: { LayerPanel },
  setup() {
    return { args };
  },
  template: '<LayerPanel v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {};

export const LayerAdded = Template.bind({});
LayerAdded.args = {
  layers: [
    { id: 1, name: 'Layer 1', opacity: 1, visible: true },
    { id: 2, name: 'Layer 2', opacity: 1, visible: true },
  ],
};

export const LayerRemoved = Template.bind({});
LayerRemoved.args = {
  layers: [
    { id: 1, name: 'Layer 1', opacity: 1, visible: true },
  ],
};

export const LayerRenamed = Template.bind({});
LayerRenamed.args = {
  layers: [
    { id: 1, name: 'Renamed Layer', opacity: 1, visible: true },
  ],
};