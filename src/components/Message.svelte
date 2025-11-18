<script>
  import { renderMarkdown } from '../services/markdown.js'

  export let message
  export let isLoading = false

  $: isUser = message.sender === 'user'
  $: rowClass = isUser ? 'flex-row-reverse' : 'flex-row'
  $: renderedText = renderMarkdown(message?.text || '')
  $: bubbleClass = isUser
    ? 'inline-block max-w-full bg-gray-800 text-gray-50 border border-gray-700 rounded-3xl px-4 py-3 shadow-sm'
    : 'block w-full text-gray-100 rounded-3xl px-4 py-3'
  $: messageContainerClass = 'max-w-[100%] min-w-0 flex-shrink-0'
  $: showTypingAnimation = !isUser && isLoading && !message.text
  $: hasCitations = !isUser && message?.citations && message.citations.length > 0
</script>

<div class="flex {rowClass} gap-2 px-2 sm:px-4 py-2 sm:py-3 hover:bg-gray-800/50 transition-colors">
  <div class={messageContainerClass}>
    <div class="text-xs sm:text-sm leading-relaxed break-words">
      <div class={bubbleClass}>
        {#if showTypingAnimation}
          <div class="flex gap-1 items-center py-2 px-2">
            <div class="typing-dot"></div>
            <div class="typing-dot delay-1"></div>
            <div class="typing-dot delay-2"></div>
          </div>
        {:else}
          {@html renderedText}
        {/if}
      </div>
    </div>
    {#if hasCitations}
      <div class="mt-2 px-1">
        <div class="flex flex-wrap gap-1.5">
          {#each message.citations as citation, i}
            <div
              class="citation-card bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs relative"
            >
              <div class="flex items-baseline gap-1">
                <span class="text-blue-400">[{i + 1}]</span>
                <span class="text-blue-400">{citation.fileName}</span>
                {#if citation.chunkId !== null}
                  <span class="text-gray-400 text-[10px]">#{citation.chunkId}</span>
                {/if}
              </div>
              {#if citation.content}
                <!-- Hover tooltip with full content -->
                <div class="citation-tooltip">
                  <div class="flex items-baseline gap-2 text-xs font-semibold text-blue-300 mb-2 pb-2 border-b border-gray-600">
                    <span>{citation.fileName}</span>
                    {#if citation.chunkId !== null}
                      <span class="text-gray-400 text-[10px] font-normal">Chunk #{citation.chunkId}</span>
                    {/if}
                  </div>
                  <div class="text-xs text-gray-200 whitespace-pre-wrap">
                    {citation.content}
                  </div>
                </div>
              {/if}
            </div>
          {/each}
        </div>
      </div>
    {/if}
    {#if !isUser && !showTypingAnimation}
      <div class="flex gap-1 sm:gap-2 mt-2 px-1">
        <button class="action-button" title="コピー">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        </button>
        <button class="action-button" title="いいね">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
          </svg>
        </button>
        <button class="action-button" title="よくない">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
          </svg>
        </button>
        <button class="action-button" title="共有">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
        </button>
        <button class="action-button" title="再生成">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
        <button class="action-button" title="その他">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
          </svg>
        </button>
      </div>
    {/if}
  </div>
</div>

<style>
  .typing-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #9ca3af;
    animation: typing 1.4s infinite;
  }

  .typing-dot.delay-1 {
    animation-delay: 0.2s;
  }

  .typing-dot.delay-2 {
    animation-delay: 0.4s;
  }

  @keyframes typing {
    0%, 60%, 100% {
      opacity: 0.3;
      transform: translateY(0);
    }
    30% {
      opacity: 1;
      transform: translateY(-10px);
    }
  }

  .action-button {
    padding: 0.375rem;
    border-radius: 0.375rem;
    color: #9ca3af;
    background-color: transparent;
    transition: all 0.2s;
    cursor: pointer;
    border: none;
  }

  .action-button:hover {
    background-color: rgba(55, 65, 81, 0.5);
    color: #e5e7eb;
  }

  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .citation-card {
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .citation-card:hover {
    border-color: #60a5fa;
    background-color: rgba(31, 41, 55, 0.8);
  }

  .citation-tooltip {
    position: absolute;
    bottom: 100%;
    left: 0;
    right: 0;
    margin-bottom: 0.5rem;
    padding: 0.75rem;
    background-color: #1f2937;
    border: 1px solid #60a5fa;
    border-radius: 0.5rem;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    opacity: 0;
    visibility: hidden;
    transform: translateY(10px);
    transition: all 0.2s ease;
    z-index: 50;
    max-height: 300px;
    overflow-y: auto;
    min-width: 300px;
    max-width: 500px;
  }

  .citation-card:hover .citation-tooltip {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
  }

  /* Custom scrollbar for tooltip */
  .citation-tooltip::-webkit-scrollbar {
    width: 6px;
  }

  .citation-tooltip::-webkit-scrollbar-track {
    background: #374151;
    border-radius: 3px;
  }

  .citation-tooltip::-webkit-scrollbar-thumb {
    background: #60a5fa;
    border-radius: 3px;
  }

  .citation-tooltip::-webkit-scrollbar-thumb:hover {
    background: #3b82f6;
  }
</style>
