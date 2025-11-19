<script>
  import { createEventDispatcher } from 'svelte'
  import {
    findKnowledgeBase,
    listVectorStoreFiles,
    getFileMetadata,
    deleteVectorStoreFile
  } from '../services/aiService.js'

  const dispatch = createEventDispatcher()

  export let lockSettings = false
  export let apiKeyError = ''
  export let apiKey = ''

  let internalApiKey = ''
  let showSettings = false
  let savedKey = ''
  let activeTab = 'files'

  let knowledgeBaseId = ''
  let files = []
  let isLoadingFiles = false
  let filesError = ''
  let deletingFileId = ''

  function handleSaveApiKey() {
    if (internalApiKey.trim()) {
      localStorage.setItem('openai_api_key', internalApiKey)
      savedKey = internalApiKey
      dispatch('apiKeySet', internalApiKey)
    }
  }

  function handleRemoveApiKey() {
    localStorage.removeItem('openai_api_key')
    internalApiKey = ''
    savedKey = ''
    dispatch('apiKeyRemoved')
  }

  function loadSavedKey() {
    const saved = localStorage.getItem('openai_api_key')
    if (saved) {
      savedKey = saved
      internalApiKey = saved
    }
  }

  export function open() {
    loadSavedKey()
    activeTab = 'files'
    showSettings = true
    // 初回表示時でもファイル一覧を取得しておく
    loadKnowledgeBaseFiles()
  }

  export function close() {
    if (lockSettings) {
      return
    }
    showSettings = false
  }

  function toggleSettings() {
    if (showSettings) {
      close()
    } else {
      open()
    }
  }

  async function handleSelectTab(tab) {
    activeTab = tab
    if (tab === 'files') {
      await loadKnowledgeBaseFiles()
    }
  }

  async function loadKnowledgeBaseFiles() {
    const key = savedKey || apiKey
    if (!key || !key.trim()) {
      filesError = 'APIキーが設定されていません。先に API 設定タブで設定してください。'
      return
    }

    isLoadingFiles = true
    filesError = ''

    try {
      // Try to load existing knowledge_base without creating a new one
      const knowledgeBase = await findKnowledgeBase(key)

      if (!knowledgeBase) {
        knowledgeBaseId = ''
        files = []
        filesError = 'knowledge_baseはまだ作成されていません。ファイルをアップロードすると自動で作成されます。'
        return
      }

      knowledgeBaseId = knowledgeBase.id

      // Load files
      const fileList = await listVectorStoreFiles(key, knowledgeBaseId, 50)

      // Enhance with metadata
      const enhancedFiles = await Promise.all(
        fileList.map(async (file) => {
          try {
            const meta = await getFileMetadata(key, file.id)
            return {
              ...file,
              filename: meta.filename || null
            }
          } catch (error) {
            return file
          }
        })
      )

      files = enhancedFiles
    } catch (error) {
      filesError = error.message || 'ファイル一覧の取得に失敗しました。'
    } finally {
      isLoadingFiles = false
    }
  }

  async function handleDeleteFile(fileId) {
    if (!fileId) {
      return
    }

    const confirmed = window.confirm('このファイルをknowledge_baseから削除しますか？')
    if (!confirmed) {
      return
    }

    const key = savedKey || apiKey
    deletingFileId = fileId

    try {
      await deleteVectorStoreFile(key, knowledgeBaseId, fileId)
      files = files.filter(file => file.id !== fileId)
    } catch (error) {
      filesError = error.message || 'ファイルの削除に失敗しました。'
    } finally {
      deletingFileId = ''
    }
  }

  function formatUnixTime(timestamp) {
    if (!timestamp) {
      return ''
    }
    try {
      const date = new Date(timestamp * 1000)
      return date.toLocaleString()
    } catch (e) {
      return ''
    }
  }
</script>

<button
  on:click={toggleSettings}
  class="text-gray-300 hover:text-white rounded-full p-1 sm:p-1.5 transition-colors flex items-center justify-center text-xl leading-none"
  aria-label="設定"
>
  <span>···</span>
</button>

{#if showSettings}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-gray-800 rounded-lg shadow-lg max-w-md w-full p-4 sm:p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-white text-lg sm:text-xl font-bold">設定</h2>
        {#if !lockSettings}
          <button
            on:click={toggleSettings}
            class="text-gray-400 hover:text-white transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        {/if}
      </div>

      <div>
        <div class="flex border-b border-gray-700 mb-4 text-sm">
          <button
            class={`px-3 py-1.5 rounded-t ${
              activeTab === 'files'
                ? 'bg-gray-800 text-white border-b-2 border-blue-500'
                : 'text-gray-400 hover:text-white'
            }`}
            on:click={() => handleSelectTab('files')}
          >
            ファイル管理
          </button>
          <button
            class={`px-3 py-1.5 mr-2 rounded-t ${
              activeTab === 'api'
                ? 'bg-gray-800 text-white border-b-2 border-blue-500'
                : 'text-gray-400 hover:text-white'
            }`}
            on:click={() => handleSelectTab('api')}
          >
            API 設定
          </button>
        </div>

        {#if activeTab === 'api'}
          <div class="space-y-4">
            <div>
              <label for="apiKey" class="block text-white text-sm font-medium mb-2">
                OpenAI API キー
              </label>
              <div class="flex gap-2 sm:gap-3">
                <input
                  id="apiKey"
                  type="password"
                  bind:value={internalApiKey}
                  placeholder="sk-..."
                  class="flex-1 bg-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-400"
                />
                <button
                  on:click={handleSaveApiKey}
                  disabled={!internalApiKey.trim()}
                  class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg px-3 py-2 font-medium transition-colors text-sm"
                >
                  保存
                </button>
              </div>
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
              {#if apiKeyError}
                <p class="text-red-400 text-xs mt-1">
                  {apiKeyError}
                </p>
              {/if}
            </div>

            {#if savedKey}
              <div class="flex gap-2 sm:gap-3">
                <button
                  on:click={handleRemoveApiKey}
                  class="flex-1 bg-red-600 hover:bg-red-700 text-white rounded-lg px-3 py-2 font-medium transition-colors text-sm"
                >
                  APIキー削除
                </button>
              </div>
            {/if}
          </div>
        {:else if activeTab === 'files'}
          <div class="space-y-4 text-sm">
            <div class="text-xs text-gray-300">
              knowledge_baseに登録されているファイルの一覧です。
            </div>

            {#if filesError}
              <p class="text-xs text-red-400">{filesError}</p>
            {/if}

            {#if isLoadingFiles}
              <p class="text-xs text-gray-400">読み込み中...</p>
            {:else if files.length === 0}
              <p class="text-xs text-gray-500">ファイルは登録されていません。</p>
            {:else}
              <div class="space-y-2 max-h-96 overflow-y-auto pr-1">
                {#each files as file}
                  <div class="flex items-start justify-between gap-2 bg-gray-700 rounded px-3 py-2">
                    <div class="flex-1 min-w-0">
                      {#if file.filename}
                        <div class="text-xs text-gray-100 truncate">{file.filename}</div>
                      {/if}
                      {#if file.created_at}
                        <div class="text-[10px] text-gray-400">{formatUnixTime(file.created_at)}</div>
                      {/if}
                    </div>
                    <button
                      on:click={() => handleDeleteFile(file.id)}
                      disabled={deletingFileId === file.id}
                      class="text-[10px] bg-gray-800 hover:bg-red-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded px-2 py-1"
                    >
                      {#if deletingFileId === file.id}
                        削除中
                      {:else}
                        削除
                      {/if}
                    </button>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}
