<script>
  import MessageList from './MessageList.svelte'
  import ChatInput from './ChatInput.svelte'
  import { onMount } from 'svelte'

  let messages = []

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
          text: 'こんにちは！何かお手伝いできることはありますか？',
          sender: 'assistant',
          timestamp: new Date()
        }
      ]
    }
  })

  function handleSendMessage(event) {
    const userMessage = {
      id: Date.now(),
      text: event.detail,
      sender: 'user',
      timestamp: new Date()
    }

    messages = [...messages, userMessage]

    // Simulate assistant response
    setTimeout(() => {
      const responses = [
        'それはいいアイデアですね！',
        'なるほど、理解しました。',
        'もっと詳しく教えていただけますか？',
        'そうですね、確認させてください。',
        '他にご質問があればお聞きします。'
      ]

      const randomResponse = responses[Math.floor(Math.random() * responses.length)]

      const assistantMessage = {
        id: Date.now() + 1,
        text: randomResponse,
        sender: 'assistant',
        timestamp: new Date()
      }

      messages = [...messages, assistantMessage]
      saveMessages()
    }, 500)

    saveMessages()
  }

  function saveMessages() {
    localStorage.setItem('chat_messages', JSON.stringify(messages))
  }
</script>

<div class="flex flex-col h-full">
  <div class="bg-gray-800 border-b border-gray-700 px-3 sm:px-4 py-2 sm:py-3">
    <h1 class="text-white text-base sm:text-lg font-semibold">Chat Assistant</h1>
  </div>

  <MessageList {messages} />

  <ChatInput on:sendMessage={handleSendMessage} />
</div>
