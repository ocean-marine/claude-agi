<script>
  import { createEventDispatcher } from 'svelte'

  const dispatch = createEventDispatcher()

  let input = ''

  export let loading = false

  function handleSend() {
    if (input.trim() && !loading) {
      dispatch('sendMessage', input)
      input = ''
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey && !loading) {
      e.preventDefault()
      handleSend()
    }
  }
</script>

<div class="border-t border-gray-700 bg-gray-800 px-2 sm:px-4 py-2 sm:py-3">
  <div class="flex gap-2 sm:gap-3 w-full">
    <textarea
      bind:value={input}
      on:keydown={handleKeydown}
      placeholder="メッセージを入力..."
      class="flex-1 bg-gray-700 text-white rounded-lg px-2 sm:px-3 py-2 text-xs sm:text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-400"
      rows="1"
    />
    <button
      on:click={handleSend}
      disabled={!input.trim() || loading}
      class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg px-2 sm:px-4 py-2 font-medium transition-colors flex items-center justify-center gap-1 whitespace-nowrap flex-shrink-0 min-w-fit"
    >
      <span class="hidden sm:inline">送信</span>
      <span class="sm:hidden">送</span>
      {#if loading}
        <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      {/if}
    </button>
  </div>
</div>

<style>
  textarea {
    max-height: 200px;
  }

  textarea::-webkit-scrollbar {
    width: 4px;
  }

  textarea::-webkit-scrollbar-track {
    background: transparent;
  }

  textarea::-webkit-scrollbar-thumb {
    background-color: rgb(75, 85, 99);
    border-radius: 2px;
  }
</style>
