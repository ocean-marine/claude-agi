<script>
  import MessageList from './MessageList.svelte'
  import ChatInput from './ChatInput.svelte'
  import Settings from './Settings.svelte'
  import { onMount } from 'svelte'
  import { callOpenAIStreaming, formatMessagesForAPI } from '../services/aiService.js'

  let messages = []
  let isLoading = false
  let apiKey = ''

  onMount(() => {
    // Load messages from localStorage
    const saved = localStorage.getItem('chat_messages')
    if (saved) {
      messages = JSON.parse(saved)
    } else {
      // Initial greeting message
      messages = [
        {
          id: 1,
          text: 'こんにちは！APIキーを設定して、AIによる返答を利用してください。',
          sender: 'assistant',
          timestamp: new Date()
        }
      ]
    }

    // Load API key from localStorage
    const savedKey = localStorage.getItem('openai_api_key')
    if (savedKey) {
      apiKey = savedKey
    }
  })

  async function handleSendMessage(event) {
    const userMessage = {
      id: Date.now(),
      text: event.detail,
      sender: 'user',
      timestamp: new Date()
    }

    messages = [...messages, userMessage]
    saveMessages()
    isLoading = true

    // Create a placeholder for assistant message
    const assistantMessageId = Date.now() + 1
    const assistantMessage = {
      id: assistantMessageId,
      text: '',
      sender: 'assistant',
      timestamp: new Date()
    }

    messages = [...messages, assistantMessage]
    saveMessages()

    // Call OpenAI API with streaming
    const apiMessages = formatMessagesForAPI(messages.slice(0, -1))

    await callOpenAIStreaming(
      apiKey,
      apiMessages,
      (chunk) => {
        // Update the assistant message with new chunk
        messages = messages.map(msg =>
          msg.id === assistantMessageId
            ? { ...msg, text: msg.text + chunk }
            : msg
        )
        saveMessages()
      },
      (error) => {
        // Replace the assistant message with error message
        messages = messages.map(msg =>
          msg.id === assistantMessageId
            ? { ...msg, text: `❌ ${error}` }
            : msg
        )
        saveMessages()
      }
    )

    isLoading = false
  }

  function handleApiKeySet(event) {
    apiKey = event.detail
  }

  function handleApiKeyRemoved() {
    apiKey = ''
  }

  function saveMessages() {
    localStorage.setItem('chat_messages', JSON.stringify(messages))
  }
</script>

<div class="flex flex-col h-full w-full relative">
  <div class="bg-gray-800 border-b border-gray-700 px-2 sm:px-4 py-2">
    <h1 class="text-white text-sm sm:text-base font-semibold">Chat Assistant</h1>
  </div>

  <Settings on:apiKeySet={handleApiKeySet} on:apiKeyRemoved={handleApiKeyRemoved} />

  <MessageList {messages} />

  <ChatInput on:sendMessage={handleSendMessage} loading={isLoading} />
</div>
