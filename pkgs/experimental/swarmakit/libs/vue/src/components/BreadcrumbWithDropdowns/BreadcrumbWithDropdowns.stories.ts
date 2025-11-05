import { Meta, StoryFn } from '@storybook/vue3';
import BreadcrumbWithDropdowns from './BreadcrumbWithDropdowns.vue';

export default {
  title: 'component/Navigation/BreadcrumbWithDropdowns',
  component: BreadcrumbWithDropdowns,
  tags: ['autodocs'],
} as Meta<typeof BreadcrumbWithDropdowns>;

const Template: StoryFn<typeof BreadcrumbWithDropdowns> = (args) => ({
  components: { BreadcrumbWithDropdowns },
  setup() {
    return { args };
  },
  template: '<BreadcrumbWithDropdowns v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  breadcrumbs: [
    { name: 'Home', link: '/' },
    { name: 'Category', dropdown: [{ name: 'Subcategory 1', link: '/subcategory1' }, { name: 'Subcategory 2', link: '/subcategory2' }] },
    { name: 'Current Page' },
  ],
};

export const DropdownOpen = Template.bind({});
DropdownOpen.args = {
  breadcrumbs: [
    { name: 'Home', link: '/' },
    { name: 'Category', dropdown: [{ name: 'Subcategory 1', link: '/subcategory1' }, { name: 'Subcategory 2', link: '/subcategory2' }] },
    { name: 'Current Page' },
  ],
};

export const DropdownClosed = Template.bind({});
DropdownClosed.args = {
  breadcrumbs: [
    { name: 'Home', link: '/' },
    { name: 'Category', dropdown: [{ name: 'Subcategory 1', link: '/subcategory1' }, { name: 'Subcategory 2', link: '/subcategory2' }] },
    { name: 'Current Page' },
  ],
};