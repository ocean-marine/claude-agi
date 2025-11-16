<script>
  export let message

  $: isUser = message.sender === 'user'
  $: bgClass = isUser ? 'bg-blue-600' : 'bg-gray-700'
  $: textClass = isUser ? 'text-white' : 'text-gray-100'
  $: alignment = isUser ? 'flex-row-reverse' : 'flex-row'
</script>

<div class="flex {alignment} gap-4 px-4 py-4 hover:bg-gray-800/50 transition-colors">
  <div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center {bgClass}">
    <span class="text-xs {textClass}">
      {isUser ? '👤' : '🤖'}
    </span>
  </div>

  <div class="flex-1 max-w-3xl">
    <div class="flex {alignment} gap-2 mb-1">
      <span class="text-xs text-gray-400">
        {isUser ? 'You' : 'Assistant'}
      </span>
      <span class="text-xs text-gray-500">
        {message.timestamp.toLocaleTimeString()}
      </span>
    </div>
    <div class="text-gray-100 leading-relaxed">
      {message.text}
    </div>
  </div>
</div>
