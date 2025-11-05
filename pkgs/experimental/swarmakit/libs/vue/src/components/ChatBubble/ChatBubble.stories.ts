import { Meta, StoryFn } from '@storybook/vue3';
import ChatBubble from './ChatBubble.vue';

export default {
  title: 'component/Miscellaneous/ChatBubble',
  component: ChatBubble,
  tags: ['autodocs'],
  argTypes: {
    read: { control: 'boolean' },
    unread: { control: 'boolean' },
    active: { control: 'boolean' },
  },
} as Meta<typeof ChatBubble>;

const Template: StoryFn<typeof ChatBubble> = (args) => ({
  components: { ChatBubble },
  setup() {
    return { args };
  },
  template: '<ChatBubble v-bind="args">This is a chat message.</ChatBubble>',
});

export const Default = Template.bind({});
Default.args = {
  read: false,
  unread: false,
  active: false,
};

export const Read = Template.bind({});
Read.args = {
  read: true,
  unread: false,
  active: false,
};

export const Unread = Template.bind({});
Unread.args = {
  read: false,
  unread: true,
  active: false,
};

export const Hover = Template.bind({});
Hover.args = {
  read: false,
  unread: false,
  active: false,
};

export const Active = Template.bind({});
Active.args = {
  read: false,
  unread: false,
  active: true,
};