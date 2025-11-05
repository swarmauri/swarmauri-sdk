import { Meta, StoryFn } from '@storybook/vue3';
import FavoritesList from './FavoritesList.vue';

export default {
  title: 'component/Lists/FavoritesList',
  component: FavoritesList,
  tags: ['autodocs'],
  argTypes: {
    items: { control: 'object' },
  },
} as Meta<typeof FavoritesList>;

const Template: StoryFn<typeof FavoritesList> = (args) => ({
  components: { FavoritesList },
  setup() {
    return { args };
  },
  template: `
    <FavoritesList v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  items: [
    { title: 'Item 1', starred: false },
    { title: 'Item 2', starred: true },
    { title: 'Item 3', starred: false },
  ],
};

export const Starred = Template.bind({});
Starred.args = {
  items: [
    { title: 'Item 1', starred: true },
    { title: 'Item 2', starred: true },
    { title: 'Item 3', starred: true },
  ],
};

export const Unstarred = Template.bind({});
Unstarred.args = {
  items: [
    { title: 'Item 1', starred: false },
    { title: 'Item 2', starred: false },
    { title: 'Item 3', starred: false },
  ],
};

export const Hover = Template.bind({});
Hover.args = {
  ...Default.args,
};

export const Selected = Template.bind({});
Selected.args = {
  ...Default.args,
};