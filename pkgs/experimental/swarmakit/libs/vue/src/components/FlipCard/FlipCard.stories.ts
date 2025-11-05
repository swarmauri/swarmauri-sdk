import FlipCard from './FlipCard.vue';
import {Meta,StoryFn} from '@storybook/vue3'

export default {
  title: 'component/Cards/FlipCard',
  component: FlipCard,
  tags: ['autodocs'],
  argTypes: {
    disabled: { control: 'boolean' },
  },
} as Meta;

const Template:StoryFn = (args) => ({
  components: { FlipCard },
  setup() {
    return { args };
  },
  template: `
    <FlipCard v-bind="args">
      <template #front>Front Content</template>
      <template #back>Back Content</template>
    </FlipCard>
  `,
});

export const Default = Template.bind({});
Default.args = {
  disabled: false,
};

export const Front = Template.bind({});
Front.args = {
  disabled: false,
};

export const Back = Template.bind({});
Back.args = {
  disabled: false,
};

export const Flipped = Template.bind({});
Flipped.args = {
  disabled: false,
};

export const Hovered = Template.bind({});
Hovered.args = {
  disabled: false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  disabled: true,
};