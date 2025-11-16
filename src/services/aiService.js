/**
 * OpenAI API Service
 * Handles streaming responses from OpenAI API
 */

const API_URL = 'https://api.openai.com/v1/chat/completions'

export async function callOpenAIStreaming(apiKey, messages, onChunk, onError) {
  if (!apiKey || !apiKey.trim()) {
    onError('APIキーが設定されていません。設定から入力してください。')
    return
  }

  try {
    const payload = {
      model: 'gpt-4o-mini',
      messages: messages,
      stream: true,
      temperature: 0.7,
      max_tokens: 2000
    }

    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const errorData = await response.text()
      let errorMessage = `API エラー (${response.status})`
      try {
        const parsed = JSON.parse(errorData)
        if (parsed.error?.message) {
          errorMessage = parsed.error.message
        }
      } catch (e) {
        // Use default error message
      }
      onError(errorMessage)
      return
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')

      // Keep the last incomplete line in the buffer
      buffer = lines[lines.length - 1]

      for (let i = 0; i < lines.length - 1; i++) {
        const line = lines[i].trim()

        if (line === '' || line === ':') continue
        if (!line.startsWith('data: ')) continue

        const data = line.slice(6)

        if (data === '[DONE]') {
          return
        }

        try {
          const json = JSON.parse(data)
          const chunk = json.choices?.[0]?.delta?.content
          if (chunk) {
            onChunk(chunk)
          }
        } catch (e) {
          // Ignore parse errors for malformed chunks
        }
      }
    }

    // Process any remaining buffer
    if (buffer.trim() && buffer.trim().startsWith('data: ')) {
      const data = buffer.slice(6).trim()
      if (data !== '[DONE]') {
        try {
          const json = JSON.parse(data)
          const chunk = json.choices?.[0]?.delta?.content
          if (chunk) {
            onChunk(chunk)
          }
        } catch (e) {
          // Ignore parse errors
        }
      }
    }
  } catch (error) {
    onError(`エラーが発生しました: ${error.message}`)
  }
}

/**
 * Convert chat messages to OpenAI format
 */
export function formatMessagesForAPI(messages) {
  return messages
    .filter(msg => msg.sender === 'user' || msg.sender === 'assistant')
    .map(msg => ({
      role: msg.sender === 'user' ? 'user' : 'assistant',
      content: msg.text
    }))
}
