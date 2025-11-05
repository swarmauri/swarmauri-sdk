import { Meta, StoryFn } from '@storybook/vue3';
import Toast from './Toast.vue';

export default {
  title: 'component/Indicators/Toast',
  component: Toast,
  tags: ['autodocs'],
  argTypes: {
    message: {
      control: 'text',
    },
    type: {
      control: { type: 'select', options: ['success', 'error', 'warning', 'info'] },
    },
  },
} as Meta<typeof Toast>;

const Template: StoryFn<typeof Toast> = (args) => ({
  components: { Toast },
  setup() {
    return { args };
  },
  template: `<Toast v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  message: 'This is a default toast message.',
  type: 'info',
};

export const Success = Template.bind({});
Success.args = {
  message: 'This is a success toast message.',
  type: 'success',
};

export const Error = Template.bind({});
Error.args = {
  message: 'This is an error toast message.',
  type: 'error',
};

export const Warning = Template.bind({});
Warning.args = {
  message: 'This is a warning toast message.',
  type: 'warning',
};

export const Info = Template.bind({});
Info.args = {
  message: 'This is an info toast message.',
  type: 'info',
};

export const Dismissed = Template.bind({});
Dismissed.args = {
  message: 'This toast is dismissed.',
  type: 'info',
};