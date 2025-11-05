import { Meta, StoryFn } from '@storybook/vue3';
import Breadcrumbs from './Breadcrumbs.vue';

export default {
  title: 'component/Navigation/Breadcrumbs',
  component: Breadcrumbs,
  tags: ['autodocs'],
} as Meta<typeof Breadcrumbs>;

const Template: StoryFn<typeof Breadcrumbs> = (args) => ({
  components: { Breadcrumbs },
  setup() {
    return { args };
  },
  template: '<Breadcrumbs v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  breadcrumbs: [
    { name: 'Home', link: '/' },
    { name: 'Category', link: '/category' },
    { name: 'Current Page' },
  ],
  activeIndex: 2,
};

export const Truncated = Template.bind({});
Truncated.args = {
  breadcrumbs: [
    { name: 'Home', link: '/' },
    { name: '...', link: '/truncated' },
    { name: 'Current Page' },
  ],
  activeIndex: 2,
};

export const Active = Template.bind({});
Active.args = {
  breadcrumbs: [
    { name: 'Home', link: '/' },
    { name: 'Category', link: '/category' },
    { name: 'Current Page' },
  ],
  activeIndex: 1,
};