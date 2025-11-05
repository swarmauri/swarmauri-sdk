import { Meta, StoryFn } from '@storybook/vue3';
import DegreeImageViewer from './360-DegreeImageViewer.vue';

export default {
  title: 'component/Media/360-DegreeImageViewer',
  component: DegreeImageViewer,
  tags: ['autodocs'],
  argTypes: {
    images: { control: 'object' },
    rotationSpeed: { control: 'number' },
  },
} as Meta<typeof DegreeImageViewer>; // Cast to unknown first, then Meta


const Template: StoryFn<typeof DegreeImageViewer> = (args) => ({
  components: { DegreeImageViewer },
  setup() {
    return { args };
  },
  template: '<DegreeImageViewer v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  images: Array.from({ length: 36 }, (_, index) => `path/to/image${index + 1}.jpg`),
  rotationSpeed: 100,
};

export const Rotating = Template.bind({});
Rotating.args = {
  ...Default.args,
  rotationSpeed: 50,
};

export const Paused = Template.bind({});
Paused.args = {
  ...Default.args,
};

export const ZoomInOut = Template.bind({});
ZoomInOut.args = {
  ...Default.args,
};

export const Loading = Template.bind({});
Loading.args = {
  ...Default.args,
  images: [],
};
