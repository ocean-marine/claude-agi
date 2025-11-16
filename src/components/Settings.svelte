<script>
  import { createEventDispatcher } from 'svelte'

  const dispatch = createEventDispatcher()

  let apiKey = ''
  let showSettings = false
  let savedKey = ''

  function handleSaveApiKey() {
    if (apiKey.trim()) {
      localStorage.setItem('openai_api_key', apiKey)
      savedKey = apiKey
      dispatch('apiKeySet', apiKey)
      showSettings = false
    }
  }

  function handleRemoveApiKey() {
    localStorage.removeItem('openai_api_key')
    apiKey = ''
    savedKey = ''
    dispatch('apiKeyRemoved')
  }

  function loadSavedKey() {
    const saved = localStorage.getItem('openai_api_key')
    if (saved) {
      savedKey = saved
      apiKey = saved
    }
  }

  function toggleSettings() {
    if (!showSettings) {
      loadSavedKey()
    }
    showSettings = !showSettings
  }
</script>

<button
  on:click={toggleSettings}
  class="absolute top-2 right-2 sm:top-4 sm:right-4 bg-gray-700 hover:bg-gray-600 text-white rounded-lg px-2 sm:px-3 py-1 sm:py-2 text-xs sm:text-sm transition-colors flex items-center gap-1"
>
  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
  </svg>
  <span class="hidden sm:inline">設定</span>
</button>

{#if showSettings}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-gray-800 rounded-lg shadow-lg max-w-md w-full p-4 sm:p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-white text-lg sm:text-xl font-bold">設定</h2>
        <button
          on:click={toggleSettings}
          class="text-gray-400 hover:text-white transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <div class="space-y-4">
        <div>
          <label for="apiKey" class="block text-white text-sm font-medium mb-2">
            OpenAI API キー
          </label>
          <input
            id="apiKey"
            type="password"
            bind:value={apiKey}
            placeholder="sk-..."
            class="w-full bg-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-400"
          />
          <p class="text-gray-400 text-xs mt-1">
            <a
              href="https://platform.openai.com/api-keys"
              target="_blank"
              rel="noopener noreferrer"
              class="text-blue-400 hover:text-blue-300 underline"
            >
              API キーを取得
            </a>
          </p>
        </div>

        <div class="flex gap-2 sm:gap-3">
          <button
            on:click={handleSaveApiKey}
            disabled={!apiKey.trim()}
            class="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg px-3 py-2 font-medium transition-colors text-sm"
          >
            保存
          </button>
          {#if savedKey}
            <button
              on:click={handleRemoveApiKey}
              class="flex-1 bg-red-600 hover:bg-red-700 text-white rounded-lg px-3 py-2 font-medium transition-colors text-sm"
            >
              削除
            </button>
          {/if}
          <button
            on:click={toggleSettings}
            class="flex-1 bg-gray-700 hover:bg-gray-600 text-white rounded-lg px-3 py-2 font-medium transition-colors text-sm"
          >
            閉じる
          </button>
        </div>

        {#if savedKey}
          <div class="bg-green-900 border border-green-700 rounded-lg p-3">
            <p class="text-green-200 text-xs sm:text-sm">
              ✓ API キーが保存されています
            </p>
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}
