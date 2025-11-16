<script>
  import Message from './Message.svelte'
  import { afterUpdate } from 'svelte'

  export let messages = []

  let scrollContainer

  afterUpdate(() => {
    if (scrollContainer) {
      scrollContainer.scrollTop = scrollContainer.scrollHeight
    }
  })
</script>

<div class="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800" bind:this={scrollContainer}>
  <div class="max-w-4xl mx-auto">
    {#each messages as message (message.id)}
      <Message {message} />
    {/each}
  </div>
</div>

<style>
  :global(.scrollbar-thin) {
    scrollbar-width: thin;
  }

  :global(.scrollbar-thumb-gray-600::-webkit-scrollbar-thumb) {
    background-color: rgb(75, 85, 99);
    border-radius: 6px;
  }

  :global(.scrollbar-track-gray-800::-webkit-scrollbar-track) {
    background-color: rgb(31, 41, 55);
  }
</style>
