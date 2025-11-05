import { Meta, StoryFn } from '@storybook/vue3';
import PodcastPlayer from './PodcastPlayer.vue';

export default {
  title: 'component/Media/PodcastPlayer',
  component: PodcastPlayer,
  tags: ['autodocs'],
  argTypes: {
    episodes: { control: 'object' },
  },
} as Meta<typeof PodcastPlayer>;

const Template: StoryFn<typeof PodcastPlayer> = (args) => ({
  components: { PodcastPlayer },
  setup() {
    return { args };
  },
  template: '<PodcastPlayer v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  episodes: [
    { title: 'Episode 1: Introduction', url: '#' },
    { title: 'Episode 2: Deep Dive', url: '#' },
    { title: 'Episode 3: Expert Interview', url: '#' },
  ],
};

export const Playing = Template.bind({});
Playing.args = {
  ...Default.args,
};

export const Paused = Template.bind({});
Paused.args = {
  ...Default.args,
};

export const EpisodeList = Template.bind({});
EpisodeList.args = {
  ...Default.args,
};

export const Downloading = Template.bind({});
Downloading.args = {
  ...Default.args,
};