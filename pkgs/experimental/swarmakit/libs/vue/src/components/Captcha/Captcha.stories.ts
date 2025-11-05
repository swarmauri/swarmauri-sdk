import Captcha from './Captcha.vue';
import { Meta, StoryFn } from '@storybook/vue3';

export default {
  component: Captcha,
  title: 'component/Forms/Captcha',
  tags: ['autodocs'],
  argTypes: {
    captchaText: {
      control: { type: 'text' },
    },
  },
} as Meta;

const Template:StoryFn = (args) => ({
  components: { Captcha },
  setup() {
    return { args };
  },
  template: '<Captcha v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  captchaText: 'Please solve the captcha',
};

export const Solved = Template.bind({});
Solved.args = {
  captchaText: '✔ Solved',
};

export const Error = Template.bind({});
Error.args = {
  captchaText: 'Error: Incorrect solution',
};