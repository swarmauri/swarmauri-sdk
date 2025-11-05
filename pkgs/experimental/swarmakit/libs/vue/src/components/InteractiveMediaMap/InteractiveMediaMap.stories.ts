import { Meta, StoryFn } from '@storybook/vue3';
import InteractiveMediaMap from './InteractiveMediaMap.vue';

export default {
  title: 'component/Media/InteractiveMediaMap',
  component: InteractiveMediaMap,
  tags: ['autodocs'],
  argTypes: {
    mapSrc: { control: 'text' },
    markers: { control: 'object' },
  },
} as Meta<typeof InteractiveMediaMap>;

const Template: StoryFn<typeof InteractiveMediaMap> = (args) => ({
  components: { InteractiveMediaMap },
  setup() {
    return { args };
  },
  template: '<InteractiveMediaMap v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  mapSrc: 'https://via.placeholder.com/800x600?text=Map',
  markers: [
    { x: 20, y: 30, info: 'Marker 1' },
    { x: 50, y: 50, info: 'Marker 2' },
  ],
};

export const ZoomedIn = Template.bind({});
ZoomedIn.args = {
  ...Default.args,
};

export const MarkerSelected = Template.bind({});
MarkerSelected.args = {
  ...Default.args,
};

export const Loading = Template.bind({});
Loading.args = {
  ...Default.args,
  mapSrc: '',
};