<script>
  import { createEventDispatcher } from 'svelte'
  import { getOrCreateKnowledgeBase, uploadFileToVectorStore } from '../services/aiService.js'

  const dispatch = createEventDispatcher()

  const allowedExtensions = [
    'c',
    'cpp',
    'cs',
    'css',
    'doc',
    'docx',
    'go',
    'html',
    'java',
    'js',
    'json',
    'md',
    'pdf',
    'php',
    'pptx',
    'py',
    'rb',
    'sh',
    'tex',
    'ts',
    'txt'
  ]
  const allowedExtensionsText =
    '.c, .cpp, .cs, .css, .doc, .docx, .go, .html, .java, .js, .json, .md, .pdf, .php, .pptx, .py, .rb, .sh, .tex, .ts, .txt'

  let input = ''

  export let loading = false
  export let apiKey = ''
  export let knowledgeBaseId = ''

  let isUploadingFile = false
  let fileUploadMessage = ''
  let fileInputElement
  let isComposing = false

  function handleSend() {
    if (!apiKey || !apiKey.trim()) {
      dispatch('openSettings')
      return
    }

    if (input.trim() && !loading) {
      dispatch('sendMessage', input.trim())
      input = ''
    }
  }

  function handleKeydown(e) {
    // 日本語IMEの変換中(未確定)のEnterは送信にしない
    if (e.isComposing || isComposing) {
      return
    }

    if (e.key === 'Enter' && !e.shiftKey && !loading) {
      e.preventDefault()
      handleSend()
    }
  }

  async function handleFileChange(event) {
    fileUploadMessage = ''
    const files = Array.from(event.currentTarget.files || [])

    if (files.length === 0) {
      return
    }

    const invalidFiles = files.filter((file) => !isAllowedExtension(file.name))
    if (invalidFiles.length > 0) {
      fileUploadMessage = `このファイル形式はアップロードできません: ${invalidFiles
        .map((file) => file.name)
        .join(', ')}。対応形式: ${allowedExtensionsText}`
      if (fileInputElement) {
        fileInputElement.value = ''
      }
      return
    }

    if (!apiKey || !apiKey.trim()) {
      fileUploadMessage = 'ファイルをアップロードする前に API キーを設定してください。'
      dispatch('openSettings')
      if (fileInputElement) {
        fileInputElement.value = ''
      }
      return
    }

    try {
      isUploadingFile = true

      // Get or create knowledge_base
      let targetVectorStoreId = knowledgeBaseId
      if (!targetVectorStoreId || !targetVectorStoreId.trim()) {
        const knowledgeBase = await getOrCreateKnowledgeBase(apiKey)
        targetVectorStoreId = knowledgeBase.id
        dispatch('knowledgeBaseCreated', knowledgeBase.id)
      }

      const uploadResults = []
      for (const file of files) {
        try {
          await uploadFileToVectorStore(apiKey, targetVectorStoreId, file)
          uploadResults.push({ file, success: true })
        } catch (error) {
          uploadResults.push({ file, success: false, error: error.message })
        }
      }

      const success = uploadResults.filter((item) => item.success)
      const failed = uploadResults.filter((item) => !item.success)
      const total = uploadResults.length

      if (success.length === total) {
        fileUploadMessage = `${total}件のファイルをknowledge_baseに追加しました。`
      } else if (failed.length === total) {
        fileUploadMessage = `${total}件すべてのアップロードに失敗しました。`
      } else {
        fileUploadMessage = `${total}件中 ${success.length}件をknowledge_baseに追加、${failed.length}件でエラーが発生しました。`
      }

      if (failed.length > 0) {
        const failureSummary = failed
          .map((item) => `${item.file.name}${item.error ? `: ${item.error}` : ''}`)
          .join(', ')
        fileUploadMessage += ` 失敗したファイル: ${failureSummary}`
      }

      dispatch('filesUploaded')
    } catch (error) {
      fileUploadMessage = error.message || 'ファイルのアップロードに失敗しました。'
    } finally {
      isUploadingFile = false
      if (fileInputElement) {
        fileInputElement.value = ''
      }
    }
  }

  function isAllowedExtension(name) {
    const ext = getFileExtension(name)
    return allowedExtensions.includes(ext)
  }

  function getFileExtension(name) {
    if (!name || typeof name !== 'string') {
      return ''
    }
    const parts = name.split('.')
    if (parts.length < 2) {
      return ''
    }
    return parts.pop().toLowerCase()
  }

  function handleCompositionStart() {
    isComposing = true
  }

  function handleCompositionEnd() {
    isComposing = false
  }
</script>

<div class="bg-gray-900 px-2 sm:px-4 py-2 sm:py-3">
  <div class="flex flex-col gap-1 w-full max-w-4xl mx-auto">
    <div
      class="flex gap-2 sm:gap-3 w-full items-center bg-gray-800 rounded-full px-2 sm:px-3 py-1.5 sm:py-2"
    >
      <label
        class="flex items-center justify-center text-gray-200 cursor-pointer transition-colors flex-shrink-0 hover:text-white {isUploadingFile
          ? 'pointer-events-none'
          : ''}"
        title="Vector Store にファイルをアップロード"
      >
        <input
          type="file"
          multiple
          class="hidden"
          bind:this={fileInputElement}
          on:change={handleFileChange}
          accept=".c,.cpp,.cs,.css,.doc,.docx,.go,.html,.java,.js,.json,.md,.pdf,.php,.pptx,.py,.rb,.sh,.tex,.ts,.txt"
          disabled={isUploadingFile}
        />
        <svg
          class="w-4 h-4 sm:w-5 sm:h-5 {isUploadingFile ? 'animate-spin' : ''}"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          {#if isUploadingFile}
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          {:else}
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          {/if}
        </svg>
      </label>

      <textarea
        bind:value={input}
        on:keydown={handleKeydown}
        on:compositionstart={handleCompositionStart}
        on:compositionend={handleCompositionEnd}
        placeholder="質問をしてみましょう"
        class="flex-1 bg-transparent text-white px-1.5 sm:px-2 py-1 text-xs sm:text-sm resize-none focus:outline-none focus:ring-0 placeholder-gray-400"
        rows="1"
      />

      <button
        on:click={handleSend}
        disabled={!input.trim() || loading}
        class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-full px-3 sm:px-4 py-1.5 sm:py-2 font-medium transition-colors flex items-center justify-center gap-1 whitespace-nowrap flex-shrink-0 min-w-fit"
      >
        <span class="hidden sm:inline">送信</span>
        <span class="sm:hidden">送</span>
      </button>
    </div>

    {#if fileUploadMessage}
      <p class="text-[10px] sm:text-xs text-gray-400 px-1">
        {#if isUploadingFile}
          ⏳ {fileUploadMessage}
        {:else}
          {fileUploadMessage}
        {/if}
      </p>
    {/if}

    <p class="text-[10px] sm:text-xs text-gray-500 px-1 text-center mt-1">
      AI の回答は必ずしも正しいとは限りません。重要な情報は確認するようにしてください。
    </p>
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
