<script lang="ts">
  type PollOption = {
    label: string;
    votes: number;
  };

  export let options: PollOption[] = [];
  export let totalVotes: number = 0;
  export let ariaLabel: string = 'Interactive Poll Results';

  const calculatePercentage = (votes: number) => {
    return totalVotes ? (votes / totalVotes) * 100 : 0;
  };
</script>

<div class="poll-results" role="region" aria-label={ariaLabel}>
  {#each options as { label, votes }}
    <div class="poll-option">
      <span class="poll-label">{label}</span>
      <div class="poll-bar-container">
        <div
          class="poll-bar"
          style="width: {calculatePercentage(votes)}%;"
          aria-label={`Votes for ${label}: ${votes}`}
        ></div>
      </div>
      <span class="poll-votes">{votes} votes</span>
    </div>
  {/each}
  <div class="total-votes">Total Votes: {totalVotes}</div>
</div>

<style lang="css">
  @import './InteractivePollResults.css';
</style>