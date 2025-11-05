import { Meta, StoryFn } from '@storybook/vue3';
import CardFooter from './CardFooter.vue';

export default {
  title: 'Component/Card Elements/CardFooter',
  component: CardFooter,
  tags: ['autodocs'],
  argTypes: {
    alignment: {
      control: { type: 'select', options: ['flex-start', 'center', 'flex-end'] },
    },
  },
} as Meta;

const Template: StoryFn = (args) => ({
  components: { CardFooter },
  setup() {
    return { args };
  },
  template: '<CardFooter v-bind="args"><slot></slot></CardFooter>',
});

export const Default = Template.bind({});
Default.args = {
  alignment: 'flex-start',
};

export const WithButtons = Template.bind({});
WithButtons.args = {
  alignment: 'center',
};
WithButtons.decorators = [
  () => ({
    template: `<CardFooter alignment="center"><button>Action 1</button><button>Action 2</button></CardFooter>`,
  }),
];

export const WithLinks = Template.bind({});
WithLinks.args = {
  alignment: 'flex-end',
};
WithLinks.decorators = [
  () => ({
    template: `<CardFooter alignment="flex-end"><a href="#">Link 1</a><a href="#">Link 2</a></CardFooter>`,
  }),
];

export const Hovered = Template.bind({});
Hovered.args = {
  alignment: 'center',
};
Hovered.decorators = [
  () => ({
    template: `<CardFooter alignment="center"><button>Hover Action</button><a href="#">Hover Link</a></CardFooter>`,
  }),
];