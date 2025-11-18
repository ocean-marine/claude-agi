<script>
  import { onMount } from 'svelte'
  import ChatContainer from './components/ChatContainer.svelte'
  import Settings from './components/Settings.svelte'
  import { validateApiKey } from './services/aiService.js'

  let apiKey = ''
  let settingsRef
  let chatRef
  let lockSettings = false
  let apiKeyError = ''

  onMount(() => {
    const savedKey = localStorage.getItem('openai_api_key')

    if (!savedKey) {
      apiKey = ''
      lockSettings = true
      apiKeyError = ''
      if (settingsRef && typeof settingsRef.open === 'function') {
        settingsRef.open()
      }
      return
    }

    apiKey = savedKey
    lockSettings = false
    apiKeyError = ''

    ;(async () => {
      const isValid = await validateApiKey(savedKey)
      lockSettings = !isValid
      apiKeyError = isValid ? '' : 'APIキーが無効です。正しいキーを入力してください。'
      if (!isValid && settingsRef && typeof settingsRef.open === 'function') {
        settingsRef.open()
      }
    })()
  })

  async function handleApiKeySet(event) {
    const key = event.detail
    apiKey = key

    if (!key || !key.trim()) {
      lockSettings = true
      apiKeyError = ''
      if (settingsRef && typeof settingsRef.open === 'function') {
        settingsRef.open()
      }
      return
    }

    const isValid = await validateApiKey(key)
    lockSettings = !isValid
    apiKeyError = isValid ? '' : 'APIキーが無効です。正しいキーを入力してください。'

    if (isValid) {
      if (settingsRef && typeof settingsRef.close === 'function') {
        settingsRef.close()
      }
    } else if (settingsRef && typeof settingsRef.open === 'function') {
      settingsRef.open()
    }
  }

  function handleApiKeyRemoved() {
    apiKey = ''
    lockSettings = true
    apiKeyError = ''
    if (settingsRef && typeof settingsRef.open === 'function') {
      settingsRef.open()
    }
  }

  function handleOpenSettings() {
    if (settingsRef && typeof settingsRef.open === 'function') {
      settingsRef.open()
    }
  }
</script>

<div class="min-h-screen bg-gray-900 flex flex-col">
  <header
    class="fixed top-0 left-0 right-0 z-20 bg-gray-800 border-b border-gray-700 px-2 sm:px-4 py-2 flex justify-center"
  >
    <div class="w-full max-w-3xl flex items-center justify-between">
      <h1 class="text-white text-sm sm:text-base font-semibold">RAG Studio</h1>
      <Settings
        bind:this={settingsRef}
        {lockSettings}
        {apiKeyError}
        {apiKey}
        on:apiKeySet={handleApiKeySet}
        on:apiKeyRemoved={handleApiKeyRemoved}
      />
    </div>
  </header>

  <main class="flex-1 flex justify-center pt-12">
    <div class="w-full max-w-3xl bg-gray-900">
      <ChatContainer
        bind:this={chatRef}
        {apiKey}
        on:openSettings={handleOpenSettings}
      />
    </div>
  </main>
</div>

<style global>
  :global(body) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
</style>
