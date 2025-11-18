// Very small, dependency-free Markdown renderer for chat messages.
// Supports:
// - Headings (#, ##, ###)
// - Bold (**text**)
// - Italic (*text* or _text_)
// - Inline code (`code`)
// - Code blocks (```lang ... ```)
// - Links [text](url)
// - Bullet lists (- item, * item)
// - Horizontal rules (---, ***, ___)

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

export function renderMarkdown(raw) {
  if (!raw) return ''

  const text = String(raw)

  // First escape all HTML
  let html = escapeHtml(text)

  // Code blocks ``` ``` (multiline)
  html = html.replace(/```([\s\S]*?)```/g, (match, code) => {
    const escaped = code.replace(/^\n+|\n+$/g, '')
    return `<pre class="bg-gray-900 text-gray-100 rounded-lg p-3 text-xs sm:text-sm overflow-x-auto"><code>${escaped}</code></pre>`
  })

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code class="bg-gray-900/60 px-1 py-0.5 rounded text-xs sm:text-[0.9em]">$1</code>')

  // Headings (only at line start)
  html = html.replace(/^###\s+(.*)$/gm, '<h3 class="font-semibold text-sm sm:text-base mt-3 mb-1">$1</h3>')
  html = html.replace(/^##\s+(.*)$/gm, '<h2 class="font-semibold text-base sm:text-lg mt-4 mb-2">$1</h2>')
  html = html.replace(/^#\s+(.*)$/gm, '<h1 class="font-bold text-lg sm:text-xl mt-4 mb-2">$1</h1>')

  // Bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')

  // Italic
  html = html.replace(/(^|[^\*])\*([^*]+)\*(?!\*)/g, '$1<em>$2</em>')
  html = html.replace(/(^|[^_])_([^_]+)_(?!_)/g, '$1<em>$2</em>')

  // Links [text](url)
  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-blue-400 hover:text-blue-300 underline">$1</a>')

  // Unordered lists
  html = html.replace(/^(?:-|\*)\s+(.*)$/gm, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>\n?)+/g, match => `<ul class="list-disc list-inside my-1 space-y-0.5">${match}</ul>`)

  // Horizontal rules
  html = html.replace(/^(\-\-\-|\*\*\*|___)\s*$/gm, '<hr class="my-3 border-gray-600" />')

  // Paragraphs: split by double newline
  const parts = html.split(/\n{2,}/).map(block => block.trim()).filter(Boolean)
  html = parts
    .map(block => {
      if (block.startsWith('<h') || block.startsWith('<ul') || block.startsWith('<pre') || block.startsWith('<hr')) {
        return block
      }
      return `<p class="mb-1.5 last:mb-0">${block.replace(/\n/g, '<br />')}</p>`
    })
    .join('')

  return html
}
