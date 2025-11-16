<script>
  export let message

  $: isUser = message.sender === 'user'
  $: bgClass = isUser ? 'bg-blue-600' : 'bg-gray-700'
  $: textClass = isUser ? 'text-white' : 'text-gray-100'
  $: alignment = isUser ? 'flex-row-reverse' : 'flex-row'
</script>

<div class="flex {alignment} gap-2 px-2 sm:px-4 py-2 sm:py-3 hover:bg-gray-800/50 transition-colors">
  <div class="flex-shrink-0 w-6 h-6 sm:w-8 sm:h-8 rounded-full flex items-center justify-center {bgClass}">
    <span class="text-xs {textClass}">
      {isUser ? '👤' : '🤖'}
    </span>
  </div>

  <div class="flex-1 min-w-0">
    <div class="flex {alignment} gap-1 mb-0.5 sm:mb-1">
      <span class="text-xs text-gray-400 whitespace-nowrap">
        {isUser ? 'You' : 'Assistant'}
      </span>
      <span class="text-xs text-gray-500 whitespace-nowrap">
        {message.timestamp.toLocaleTimeString()}
      </span>
    </div>
    <div class="text-xs sm:text-sm text-gray-100 leading-relaxed break-words">
      {message.text}
    </div>
  </div>
</div>
