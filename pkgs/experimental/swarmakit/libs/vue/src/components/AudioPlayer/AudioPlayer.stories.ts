import { Meta, StoryFn } from '@storybook/vue3';
import AudioPlayer from './AudioPlayer.vue';

export default {
  title: 'component/Media/AudioPlayer',
  component: AudioPlayer,
  tags: ['autodocs'],
  argTypes: {
    src: { control: 'text' },
  },
} as Meta<typeof AudioPlayer>;

const Template: StoryFn<typeof AudioPlayer> = (args) => ({
  components: { AudioPlayer },
  setup() {
    return { args };
  },
  template: '<AudioPlayer v-bind="args" />',
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

export const Mute = Template.bind({});
Mute.args = {
  ...Default.args,
};

export const VolumeControl = Template.bind({});
VolumeControl.args = {
  ...Default.args,
};