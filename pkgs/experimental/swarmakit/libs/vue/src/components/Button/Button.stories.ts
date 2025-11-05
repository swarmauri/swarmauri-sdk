import Button from './Button.vue';
import { Meta, StoryFn } from '@storybook/vue3';

export default {
  title: 'component/Buttons/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    type: { control: { type: 'select', options: ['primary', 'secondary'] } },
    disabled: { control: 'boolean' },
  },
} as Meta<typeof Button>;

const Template: StoryFn<typeof Button> = (args) => ({
  components: { Button },
  setup() {
    return { args };
  },
  template: '<Button v-bind="args">Button</Button>',
});

export const Default = Template.bind({});
Default.args = {
  type: 'primary',
  disabled: false,
};

export const Primary = Template.bind({});
Primary.args = {
  type: 'primary',
  disabled: false,
};

export const Secondary = Template.bind({});
Secondary.args = {
  type: 'secondary',
  disabled: false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  type: 'primary',
  disabled: true,
};

export const Hover = Template.bind({});
Hover.args = {
  type: 'primary',
  disabled: false,
};

export const Active = Template.bind({});
Active.args = {
  type: 'primary',
  disabled: false,
};