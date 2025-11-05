import { Meta, StoryFn } from '@storybook/vue3';
import AudioPlayerAdvanced from './AudioPlayerAdvanced.vue';

export default {
  title: 'component/Media/AudioPlayerAdvanced',
  component: AudioPlayerAdvanced,
  tags: ['autodocs'],
  argTypes: {
    src: { control: 'text' },
  },
} as Meta<typeof AudioPlayerAdvanced>;

const Template: StoryFn<typeof AudioPlayerAdvanced> = (args) => ({
  components: { AudioPlayerAdvanced },
  setup() {
    return { args };
  },
  template: '<AudioPlayerAdvanced v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  src: 'path/to/audio.mp3',
};

export const Play = Template.bind({});
Play.args = {
  ...Default.args,
};

export const Pause = Template.bind({});
Pause.args = {
  ...Default.args,
};

export const Seek = Template.bind({});
Seek.args = {
  ...Default.args,
};

export const Mute = Template.bind({});
Mute.args = {
  ...Default.args,
};

export const VolumeControl = Template.bind({});
VolumeControl.args = {
  ...Default.args,
};

export const SpeedControl = Template.bind({});
SpeedControl.args = {
  ...Default.args,
};