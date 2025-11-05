import { Meta, StoryFn } from '@storybook/vue3';
import LoadMoreButtonInList from './LoadMoreButtonInList.vue';

export default {
  title: 'component/Lists/LoadMoreButtonInList',
  component: LoadMoreButtonInList,
  tags: ['autodocs'],
  argTypes: {
    items: { control: 'object' },
    batchSize: { control: 'number' },
  },
} as Meta<typeof LoadMoreButtonInList>;

const Template: StoryFn<typeof LoadMoreButtonInList> = (args) => ({
  components: { LoadMoreButtonInList },
  setup() {
    return { args };
  },
  template: `
    <LoadMoreButtonInList v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  items: Array.from({ length: 20 }, (_, i) => `Item ${i + 1}`),
  batchSize: 5,
};

export const Loading = Template.bind({});
Loading.args = {
  ...Default.args,
};
Loading.play = async ({ canvasElement }) => {
  const button = canvasElement.querySelector('.load-more-button') as HTMLElement;
  button.click();
};

export const EndOfList = Template.bind({});
EndOfList.args = {
  items: Array.from({ length: 5 }, (_, i) => `Item ${i + 1}`),
  batchSize: 5,
};
EndOfList.play = async ({ canvasElement }) => {
  const button = canvasElement.querySelector('.load-more-button') as HTMLElement;
  button.click();
};