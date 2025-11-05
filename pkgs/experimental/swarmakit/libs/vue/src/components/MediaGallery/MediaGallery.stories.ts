import { Meta, StoryFn } from '@storybook/vue3';
import MediaGallery from './MediaGallery.vue';

export default {
  title: 'component/Media/MediaGallery',
  component: MediaGallery,
  tags: ['autodocs'],
  argTypes: {
    images: { control: 'object' },
  },
} as Meta<typeof MediaGallery>;

const Template: StoryFn<typeof MediaGallery> = (args) => ({
  components: { MediaGallery },
  setup() {
    return { args };
  },
  template: '<MediaGallery v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  images: [
    'https://via.placeholder.com/150',
    'https://via.placeholder.com/160',
    'https://via.placeholder.com/170',
    'https://via.placeholder.com/180',
  ],
};

export const Thumbnail = Template.bind({});
Thumbnail.args = {
  ...Default.args,
};

export const Expanded = Template.bind({});
Expanded.args = {
  ...Default.args,
};

export const Slideshow = Template.bind({});
Slideshow.args = {
  ...Default.args,
};

export const ZoomInOut = Template.bind({});
ZoomInOut.args = {
  ...Default.args,
};

export const NextPrevious = Template.bind({});
NextPrevious.args = {
  ...Default.args,
};