<script>
  import MessageList from './MessageList.svelte'
  import ChatInput from './ChatInput.svelte'
  import { createEventDispatcher } from 'svelte'
  import { callOpenAIResponses, callOpenAIFileSearch, getOrCreateKnowledgeBase } from '../services/aiService.js'

  export let apiKey = ''

  const dispatch = createEventDispatcher()

  let messages = []
  let isLoading = false
  let knowledgeBaseId = ''
  let lastResponseId = null // Track the last response ID for conversation continuity
  let fileUploadNotices = []

  // Initialize knowledge_base when apiKey changes
  $: if (apiKey && apiKey.trim() && !knowledgeBaseId) {
    initializeKnowledgeBase()
  }

  async function initializeKnowledgeBase() {
    if (!apiKey || !apiKey.trim()) {
      return
    }

    try {
      const knowledgeBase = await getOrCreateKnowledgeBase(apiKey)
      knowledgeBaseId = knowledgeBase.id
      console.log('Knowledge base initialized:', knowledgeBaseId)
    } catch (error) {
      console.error('Failed to initialize knowledge_base:', error)
    }
  }

  async function handleSendMessage(event) {
    const userMessage = { id: Date.now(), text: event.detail, sender: 'user', timestamp: new Date() }
    const assistantMessageId = userMessage.id + 1
    const assistantMessage = {
      id: assistantMessageId,
      text: '',
      sender: 'assistant',
      timestamp: new Date(),
      responseId: null,
      citations: []
    }

    messages = [...messages, userMessage, assistantMessage]
    isLoading = true

    const updateAssistant = (updater) => {
      messages = messages.map((msg) =>
        msg.id === assistantMessageId ? (typeof updater === 'function' ? updater(msg) : { ...msg, ...updater }) : msg
      )
    }
    const appendChunk = (chunk) => updateAssistant((msg) => ({ ...msg, text: msg.text + chunk }))
    const setError = (error) => updateAssistant({ text: `❌ ${error}` })
    const captureResponseId = (responseId) => {
      lastResponseId = responseId
      updateAssistant({ responseId })
    }

    const useFileSearch = !!(knowledgeBaseId && knowledgeBaseId.trim().length > 0)

    if (useFileSearch) {
      await callOpenAIFileSearch(
        apiKey,
        userMessage.text,
        knowledgeBaseId,
        lastResponseId,
        appendChunk,
        setError,
        captureResponseId,
        (citations) => updateAssistant({ citations })
      )
    } else {
      await callOpenAIResponses(apiKey, userMessage.text, lastResponseId, appendChunk, setError, captureResponseId)
    }

    isLoading = false
  }

  function handleKnowledgeBaseCreated(event) {
    knowledgeBaseId = event.detail
  }

  function handleFilesUploaded() {
    dispatch('filesUploaded')
  }

  function handleOpenSettings() {
    dispatch('openSettings')
  }

  function handleFileUploadNotice(event) {
    const detail = event.detail

    if (!detail) {
      fileUploadNotices = []
      return
    }

    fileUploadNotices = [...fileUploadNotices, detail]
  }
</script>

  <div class="flex flex-col w-full relative min-h-[calc(100vh-3rem)]">
  <div class="flex-1 pb-24">
    <MessageList {messages} {isLoading} fileNotices={fileUploadNotices} />
  </div>

  <div class="sticky bottom-0 left-0 right-0 bg-gray-900">
    <ChatInput
      on:sendMessage={handleSendMessage}
      on:knowledgeBaseCreated={handleKnowledgeBaseCreated}
      on:filesUploaded={handleFilesUploaded}
      on:openSettings={handleOpenSettings}
      on:fileUploadNotice={handleFileUploadNotice}
      loading={isLoading}
      {apiKey}
      {knowledgeBaseId}
    />
  </div>
</div>
