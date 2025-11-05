import { Meta, StoryFn } from '@storybook/vue3';
import Accordion from './Accordion.vue';

export default {
  title: 'component/Lists/Accordion',
  component: Accordion,
  tags: ['autodocs'],
  argTypes: {
    defaultOpen: {
      control: 'boolean',
    },
  },
} as Meta<typeof Accordion>;

const Template: StoryFn<typeof Accordion> = (args) => ({
  components: { Accordion },
  setup() {
    return { args };
  },
  template: `
    <Accordion v-bind="args">
      <template #header>
        Accordion Header
      </template>
      <template #content>
        Accordion Content
      </template>
    </Accordion>
  `,
});

export const Default = Template.bind({});
Default.args = {
  defaultOpen: false,
};

export const Open = Template.bind({});
Open.args = {
  defaultOpen: true,
};

export const Closed = Template.bind({});
Closed.args = {
  defaultOpen: false,
};

export const Hover = Template.bind({});
Hover.args = {
  defaultOpen: false,
};