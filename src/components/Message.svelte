<script>
  export let message

  $: isUser = message.sender === 'user'
  $: bgClass = isUser ? 'bg-blue-600' : 'bg-gray-700'
  $: textClass = isUser ? 'text-white' : 'text-gray-100'
  $: alignment = isUser ? 'flex-row-reverse' : 'flex-row'
</script>

<div class="flex {alignment} gap-2 sm:gap-3 px-2 sm:px-4 py-3 sm:py-4 hover:bg-gray-800/50 transition-colors">
  <div class="flex-shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center {bgClass}">
    <span class="text-xs {textClass}">
      {isUser ? '👤' : '🤖'}
    </span>
  </div>

  <div class="flex-1 max-w-xs sm:max-w-md md:max-w-2xl lg:max-w-3xl">
    <div class="flex {alignment} gap-1 sm:gap-2 mb-1">
      <span class="text-xs text-gray-400 whitespace-nowrap">
        {isUser ? 'You' : 'Assistant'}
      </span>
      <span class="text-xs text-gray-500 whitespace-nowrap">
        {message.timestamp.toLocaleTimeString()}
      </span>
    </div>
    <div class="text-sm sm:text-base text-gray-100 leading-relaxed break-words">
      {message.text}
    </div>
  </div>
</div>
