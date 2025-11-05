import IconButton from './IconButton.vue';
import { Meta, StoryFn } from '@storybook/vue3';

export default {
  title: 'component/Buttons/IconButton',
  component: IconButton,
  tags: ['autodocs'],
  argTypes: {
    disabled: { control: 'boolean' },
  },
} as Meta<typeof IconButton>;

const Template: StoryFn<typeof IconButton> = (args) => ({
  components: { IconButton },
  setup() {
    return { args };
  },
  template: '<IconButton v-bind="args"><span class="icon">⭐</span></IconButton>',
});

export const Default = Template.bind({});
Default.args = {
  disabled: false,
};

export const Active = Template.bind({});
Active.args = {
  disabled: false,
};

export const Hover = Template.bind({});
Hover.args = {
  disabled: false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  disabled: true,
};