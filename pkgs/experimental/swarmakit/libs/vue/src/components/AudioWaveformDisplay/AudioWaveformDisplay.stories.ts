import { Meta, StoryFn } from '@storybook/vue3';
import AudioWaveformDisplay from './AudioWaveformDisplay.vue';

export default {
  title: 'component/Media/AudioWaveformDisplay',
  component: AudioWaveformDisplay,
  tags: ['autodocs'],
  argTypes: {
    src: { control: 'text' },
  },
} as Meta<typeof AudioWaveformDisplay>;

const Template: StoryFn<typeof AudioWaveformDisplay> = (args) => ({
  components: { AudioWaveformDisplay },
  setup() {
    return { args };
  },
  template: '<AudioWaveformDisplay v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  src: 'path/to/audio.mp3',
};

export const Playing = Template.bind({});
Playing.args = {
  ...Default.args,
};

export const Paused = Template.bind({});
Paused.args = {
  ...Default.args,
};

export const Loading = Template.bind({});
Loading.args = {
  ...Default.args,
};

export const Scrubbing = Template.bind({});
Scrubbing.args = {
  ...Default.args,
};