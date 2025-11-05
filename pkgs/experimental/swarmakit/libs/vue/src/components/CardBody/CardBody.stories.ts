import { Meta, StoryFn } from '@storybook/vue3';
import CardBody from './CardBody.vue';

export default {
  title: 'Component/Card Elements/CardBody',
  component: CardBody,
  tags: ['autodocs'],
  argTypes: {
    expanded: { control: 'boolean' },
    collapsible: { control: 'boolean' },
  },
} as Meta;

const Template: StoryFn = (args) => ({
  components: { CardBody },
  setup() {
    return { args };
  },
  template: '<CardBody v-bind="args"><p>This is the main content of the card.</p></CardBody>',
});

export const Default = Template.bind({});
Default.args = {
  expanded: true,
  collapsible: false,
};

export const Collapsed = Template.bind({});
Collapsed.args = {
  expanded: false,
  collapsible: true,
};

export const Expanded = Template.bind({});
Expanded.args = {
  expanded: true,
  collapsible: true,
};

export const Overflow = Template.bind({});
Overflow.args = {
  expanded: true,
  collapsible: false,
};
Overflow.decorators = [
  () => ({
    template: `<div style="width: 200px; height: 100px; overflow: hidden;"><CardBody><p>This is a very long content that should demonstrate the overflow functionality of the card body. It contains a lot of text to ensure that it overflows.</p></CardBody></div>`,
  }),
];