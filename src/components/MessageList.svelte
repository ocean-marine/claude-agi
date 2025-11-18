<script>
  import Message from './Message.svelte'
  import { afterUpdate } from 'svelte'

  export let messages = []
  export let isLoading = false
  export let fileNotices = []

  let endElement
  let noticeGroups = []

  const variantClasses = {
    success: 'text-green-300 border-green-500/20 bg-emerald-500/10',
    error: 'text-red-300 border-red-500/20 bg-rose-500/10',
    warning: 'text-amber-300 border-amber-500/20 bg-amber-500/5',
    info: 'text-gray-300 border-gray-500/30 bg-gray-800/40'
  }

  function getNoticeClasses(variant) {
    return variantClasses[variant] || variantClasses.info
  }

  function toTimestamp(value) {
    if (!value) {
      return 0
    }
    const time = new Date(value).getTime()
    return Number.isFinite(time) ? time : 0
  }

  function calculateNoticeInsertIndex(messagesList, notice) {
    if (!notice) {
      return -1
    }

    const noticeTime = toTimestamp(notice.timestamp)

    for (let i = 0; i < messagesList.length; i += 1) {
      const messageTime = toTimestamp(messagesList[i].timestamp)
      if (noticeTime <= messageTime) {
        return i
      }
    }

    return messagesList.length
  }

  function buildNoticeGroups(messagesList, notices) {
    if (!Array.isArray(notices) || notices.length === 0) {
      return Array.from({ length: messagesList.length + 1 }, () => [])
    }

    const groups = Array.from({ length: messagesList.length + 1 }, () => [])

    for (const notice of notices) {
      const index = calculateNoticeInsertIndex(messagesList, notice)
      if (index >= 0) {
        groups[index].push(notice)
      }
    }

    return groups
  }

  function sortNotices(list) {
    return [...(list || [])].sort((a, b) => {
      const timeDiff = toTimestamp(a?.timestamp) - toTimestamp(b?.timestamp)
      if (timeDiff !== 0) {
        return timeDiff
      }
      return (a?.id || 0) - (b?.id || 0)
    })
  }

  function getNoticeKey(notice, suffix = '') {
    if (notice?.id !== undefined && notice?.id !== null) {
      return `notice-${notice.id}`
    }
    return `notice-${suffix}-${toTimestamp(notice?.timestamp)}`
  }

  $: sortedNotices = sortNotices(fileNotices)
  $: noticeGroups = buildNoticeGroups(messages, sortedNotices)

  afterUpdate(() => {
    if (endElement) {
      endElement.scrollIntoView({ behavior: 'auto', block: 'end' })
    }
  })
</script>

<div class="flex-1">
  <div class="w-full px-2 sm:px-4">
    {#each messages as message, index (message.id)}
      {#if noticeGroups[index]?.length}
        {#each noticeGroups[index] as notice (getNoticeKey(notice, 'before-' + index))}
          <div
            class={`mt-4 mb-2 text-[11px] sm:text-xs px-3 py-2 rounded-lg border ${getNoticeClasses(
              notice.variant
            )} text-center transition-opacity duration-200`}
          >
            {notice.message}
          </div>
        {/each}
      {/if}
      <Message
        {message}
        isLoading={isLoading && index === messages.length - 1 && message.sender === 'assistant'}
      />
    {/each}
    {#if noticeGroups[messages.length]?.length}
      {#each noticeGroups[messages.length] as notice (getNoticeKey(notice, 'tail'))}
        <div
          class={`mt-4 mb-2 text-[11px] sm:text-xs px-3 py-2 rounded-lg border ${getNoticeClasses(
            notice.variant
          )} text-center transition-opacity duration-200`}
        >
          {notice.message}
        </div>
      {/each}
    {/if}
    <div bind:this={endElement}></div>
  </div>
</div>
