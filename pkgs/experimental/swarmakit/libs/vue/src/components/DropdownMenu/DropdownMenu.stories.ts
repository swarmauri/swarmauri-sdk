import { Meta, StoryFn } from '@storybook/vue3';
import DropdownMenu from './DropdownMenu.vue';

export default {
  title: 'component/Navigation/DropdownMenu',
  component: DropdownMenu,
  tags: ['autodocs'],
} as Meta<typeof DropdownMenu>;

const Template: StoryFn<typeof DropdownMenu> = (args) => ({
  components: { DropdownMenu },
  setup() {
    return { args };
  },
  template: '<DropdownMenu v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  menuItems: [
    { name: 'Home', link: '/home' },
    { name: 'About', link: '/about' },
    { name: 'Contact', link: '/contact' },
  ],
};

export const Expanded = Template.bind({});
Expanded.args = {
  menuItems: [
    { name: 'Home', link: '/home' },
    { name: 'About', link: '/about' },
    { name: 'Contact', link: '/contact' },
  ],
};
Expanded.play = async ({ canvasElement }) => {
  const button:HTMLElement = canvasElement.querySelector('.dropdown-toggle') as HTMLElement;
  if (button) {
    button.click();
  }
};

export const Collapsed = Template.bind({});
Collapsed.args = {
  menuItems: [
    { name: 'Home', link: '/home' },
    { name: 'About', link: '/about' },
    { name: 'Contact', link: '/contact' },
  ],
};

export const Hover = Template.bind({});
Hover.args = {
  menuItems: [
    { name: 'Home', link: '/home' },
    { name: 'About', link: '/about' },
    { name: 'Contact', link: '/contact' },
  ],
};
Hover.play = async ({ canvasElement }) => {
  const listItem = canvasElement.querySelector('.dropdown-list li a');
  if (listItem) {
    listItem.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
  }
};

export const Active = Template.bind({});
Active.args = {
  menuItems: [
    { name: 'Home', link: '/home' },
    { name: 'About', link: '/about' },
    { name: 'Contact', link: '/contact' },
  ],
};
Active.play = async ({ canvasElement }) => {
  const listItem = canvasElement.querySelector('.dropdown-list li a');
  if (listItem) {
    listItem.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
    listItem.classList.add('active');
  }
};