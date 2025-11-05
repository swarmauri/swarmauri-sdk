import { Meta, StoryFn } from '@storybook/vue3';
import CardbasedList from './CardbasedList.vue';

export default {
  title: 'component/Lists/CardbasedList',
  component: CardbasedList,
  tags: ['autodocs'],
  argTypes: {
    cards: {
      control: 'object',
    },
  },
} as Meta<typeof CardbasedList>;

const Template: StoryFn<typeof CardbasedList> = (args) => ({
  components: { CardbasedList },
  setup() {
    return { args };
  },
  template: `
    <CardbasedList v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  cards: [
    { title: 'Card 1', description: 'Description for card 1', disabled: false },
    { title: 'Card 2', description: 'Description for card 2', disabled: false },
    { title: 'Card 3', description: 'Description for card 3', disabled: false },
  ],
};

export const Hover = Template.bind({});
Hover.args = {
  cards: [
    { title: 'Hover over this card', description: 'Description for card', disabled: false },
  ],
};

export const Selected = Template.bind({});
Selected.args = {
  cards: [
    { title: 'Selected Card', description: 'Description for selected card', disabled: false },
  ],
};

export const Disabled = Template.bind({});
Disabled.args = {
  cards: [
    { title: 'Disabled Card', description: 'Description for disabled card', disabled: true },
  ],
};