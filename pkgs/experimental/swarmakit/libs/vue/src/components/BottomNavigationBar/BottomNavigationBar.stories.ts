import { Meta, StoryFn } from '@storybook/vue3';
import BottomNavigationBar from './BottomNavigationBar.vue';

export default {
  title: 'component/Navigation/BottomNavigationBar',
  component: BottomNavigationBar,
  tags: ['autodocs'],
} as Meta<typeof BottomNavigationBar>;

const Template: StoryFn<typeof BottomNavigationBar> = (args) => ({
  components: { BottomNavigationBar },
  setup() {
    return { args };
  },
  template: '<BottomNavigationBar v-bind="args" @update:items="args.items = $event" />',
});

export const Default = Template.bind({});
Default.args = {
  items: [
    { label: 'Home', selected: false, disabled: false },
    { label: 'Search', selected: false, disabled: false },
    { label: 'Profile', selected: false, disabled: false },
  ],
};

export const Selected = Template.bind({});
Selected.args = {
  items: [
    { label: 'Home', selected: true, disabled: false },
    { label: 'Search', selected: false, disabled: false },
    { label: 'Profile', selected: false, disabled: false },
  ],
};

export const Hover = Template.bind({});
Hover.args = {
  items: [
    { label: 'Home', selected: false, disabled: false },
    { label: 'Search', selected: false, disabled: false },
    { label: 'Profile', selected: false, disabled: false },
  ],
};

export const Disabled = Template.bind({});
Disabled.args = {
  items: [
    { label: 'Home', selected: false, disabled: true },
    { label: 'Search', selected: false, disabled: false },
    { label: 'Profile', selected: false, disabled: false },
  ],
};