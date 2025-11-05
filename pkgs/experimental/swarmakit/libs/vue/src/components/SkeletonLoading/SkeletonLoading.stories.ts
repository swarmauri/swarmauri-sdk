import { Meta, StoryFn } from '@storybook/vue3';
import SkeletonLoading from './SkeletonLoading.vue';

export default {
  title: 'component/Miscellaneous/SkeletonLoading',
  component: SkeletonLoading,
  tags: ['autodocs'],
} as Meta<typeof SkeletonLoading>;

const Template: StoryFn<typeof SkeletonLoading> = (args) => ({
  components: { SkeletonLoading },
  setup() {
    return { args };
  },
  template: '<SkeletonLoading v-bind="args">Content loaded</SkeletonLoading>',
});

export const Default = Template.bind({});
Default.args = { loading: false };

export const Loading = Template.bind({});
Loading.args = { loading: true };

export const Active = Template.bind({});
Active.args = { loading: false };