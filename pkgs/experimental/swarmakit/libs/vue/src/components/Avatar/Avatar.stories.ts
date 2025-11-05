import { Meta, StoryFn } from '@storybook/vue3';
import Avatar from './Avatar.vue';

export default {
  title: 'component/Miscellaneous/Avatar',
  component: Avatar,
  tags: ['autodocs'],
  argTypes: {
    imageSrc: { control: 'text' },
    initials: { control: 'text' },
    ariaLabel: { control: 'text' },
  },
} as Meta<typeof Avatar>;

const Template: StoryFn<typeof Avatar> = (args) => ({
  components: { Avatar },
  setup() {
    return { args };
  },
  template: '<Avatar v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  initials: 'JD',
  ariaLabel: 'Default Avatar',
};

export const WithImage = Template.bind({});
WithImage.args = {
  imageSrc: 'https://via.placeholder.com/150',
  ariaLabel: 'Avatar with Image',
};

export const WithoutImage = Template.bind({});
WithoutImage.args = {
  initials: 'JD',
  ariaLabel: 'Avatar without Image',
};

export const Grouped: StoryFn = () => ({
  components: { Avatar },
  template: `
    <div style="display: flex; gap: 10px;">
      <Avatar initials="AB" ariaLabel="Avatar 1" />
      <Avatar imageSrc="https://via.placeholder.com/150" ariaLabel="Avatar 2" />
      <Avatar initials="CD" ariaLabel="Avatar 3" />
    </div>
  `,
});