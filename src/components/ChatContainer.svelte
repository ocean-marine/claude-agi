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
  let lastResponseId = null // Track the last response ID for conversation continuity (null for first message)
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
    const userMessage = {
      id: Date.now(),
      text: event.detail,
      sender: 'user',
      timestamp: new Date()
    }

    messages = [...messages, userMessage]
    isLoading = true

    // Create a placeholder for assistant message
    const assistantMessageId = Date.now() + 1
    const assistantMessage = {
      id: assistantMessageId,
      text: '',
      sender: 'assistant',
      timestamp: new Date(),
      responseId: null,
      citations: []
    }

    messages = [...messages, assistantMessage]

    const useFileSearch = !!(knowledgeBaseId && knowledgeBaseId.trim().length > 0)

    if (useFileSearch) {
      await callOpenAIFileSearch(
        apiKey,
        userMessage.text,
        knowledgeBaseId,
        lastResponseId,
        (chunk) => {
          messages = messages.map(msg =>
            msg.id === assistantMessageId
              ? { ...msg, text: msg.text + chunk }
              : msg
          )
        },
        (error) => {
          messages = messages.map(msg =>
            msg.id === assistantMessageId
              ? { ...msg, text: `❌ ${error}` }
              : msg
          )
        },
        (responseId) => {
          lastResponseId = responseId
          messages = messages.map(msg =>
            msg.id === assistantMessageId ? { ...msg, responseId } : msg
          )
        },
        (citations) => {
          messages = messages.map(msg =>
            msg.id === assistantMessageId ? { ...msg, citations } : msg
          )
        }
      )
    } else {
      // Call OpenAI Responses API with streaming and conversation history
      await callOpenAIResponses(
        apiKey,
        userMessage.text,
        lastResponseId, // Pass the previous response ID for conversation continuity
        (chunk) => {
          messages = messages.map(msg =>
            msg.id === assistantMessageId
              ? { ...msg, text: msg.text + chunk }
              : msg
          )
        },
        (error) => {
          messages = messages.map(msg =>
            msg.id === assistantMessageId
              ? { ...msg, text: `❌ ${error}` }
              : msg
          )
        },
        (responseId) => {
          // Store the new response ID for the next message in conversation
          lastResponseId = responseId
          messages = messages.map(msg =>
            msg.id === assistantMessageId ? { ...msg, responseId } : msg
          )
        }
      )
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
