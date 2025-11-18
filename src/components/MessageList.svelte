<script>
  import Message from './Message.svelte'
  import { afterUpdate } from 'svelte'

  export let messages = []
  export let isLoading = false

  let endElement

  afterUpdate(() => {
    if (endElement) {
      endElement.scrollIntoView({ behavior: 'auto', block: 'end' })
    }
  })
</script>

<div class="flex-1">
  <div class="w-full px-2 sm:px-4">
    {#each messages as message, index (message.id)}
      <Message
        {message}
        isLoading={isLoading && index === messages.length - 1 && message.sender === 'assistant'}
      />
    {/each}
    <div bind:this={endElement}></div>
  </div>
</div>
