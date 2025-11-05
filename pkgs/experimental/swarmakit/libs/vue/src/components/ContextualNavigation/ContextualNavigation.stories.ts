import { Meta, StoryFn } from '@storybook/vue3';
import ContextualNavigation from './ContextualNavigation.vue';

export default {
  title: 'component/Navigation/ContextualNavigation',
  component: ContextualNavigation,
  tags: ['autodocs'],
} as Meta<typeof ContextualNavigation>;

const Template: StoryFn<typeof ContextualNavigation> = (args) => ({
  components: { ContextualNavigation },
  setup() {
    return { args };
  },
  template: '<ContextualNavigation v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  menuItems: [
    { name: 'Profile', link: '/profile' },
    { name: 'Settings', link: '/settings' },
    { name: 'Logout', link: '/logout' },
  ],
};

export const ContextTriggered = Template.bind({});
ContextTriggered.args = {
  menuItems: [
    { name: 'Profile', link: '/profile' },
    { name: 'Settings', link: '/settings' },
    { name: 'Logout', link: '/logout' },
  ],
};
ContextTriggered.play = async ({ canvasElement }) => {
  const button = canvasElement.querySelector('.contextual-toggle') as HTMLButtonElement;
  if (button) {
    button.click();
  }
};

export const Dismissed = Template.bind({});
Dismissed.args = {
  menuItems: [
    { name: 'Profile', link: '/profile' },
    { name: 'Settings', link: '/settings' },
    { name: 'Logout', link: '/logout' },
  ],
};