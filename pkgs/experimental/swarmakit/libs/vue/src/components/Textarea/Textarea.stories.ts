import Textarea from './Textarea.vue';
import {Meta,StoryFn} from '@storybook/vue3'

export default {
  component: Textarea,
  title: 'component/Forms/Textarea',
  tags: ['autodocs'],
  argTypes: {
    placeholder: { control: { type: 'text' } },
    disabled: { control: { type: 'boolean' } },
  },
} as Meta <typeof Textarea>;

const Template:StoryFn<typeof Textarea> = (args) => ({
  components: { Textarea },
  setup() {
    return { args };
  },
  template: '<Textarea v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  placeholder: 'Enter text...',
  disabled: false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  placeholder: 'Enter text...',
  disabled: true,
};