/**
 * OpenAI API Service
 * Handles streaming and non-streaming responses from OpenAI APIs
 */

const RESPONSES_API_URL = 'https://api.openai.com/v1/responses'
const VECTOR_STORES_API_URL = 'https://api.openai.com/v1/vector_stores'
const FILES_API_URL = 'https://api.openai.com/v1/files'
const MODELS_API_URL = 'https://api.openai.com/v1/models'

/**
 * Health check: validate API key by calling the Models API.
 * Returns true if the response is not an error.
 */
export async function validateApiKey(apiKey) {
  if (!apiKey || !apiKey.trim()) {
    return false
  }

  try {
    const response = await fetch(MODELS_API_URL, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${apiKey}`
      }
    })

    if (!response.ok) {
      return false
    }

    const data = await response.json()

    if (data && data.error) {
      return false
    }

    return true
  } catch (error) {
    return false
  }
}

/**
 * Call OpenAI Responses API with streaming support and conversation history
 * @param {string} apiKey - OpenAI API key
 * @param {string} userMessage - User's message text
 * @param {string|null} previousResponseId - Previous response ID for conversation continuity
 * @param {function} onChunk - Callback for streaming chunks
 * @param {function} onError - Error callback
 * @param {function} onResponseId - Callback when response ID is available
 * @returns {Promise<void>}
 */
export async function callOpenAIResponses(apiKey, userMessage, previousResponseId, onChunk, onError, onResponseId) {
  if (!apiKey || !apiKey.trim()) {
    onError('APIキーが設定されていません。設定から入力してください。')
    return
  }

  try {
    const payload = {
      model: 'gpt-5.1',
      input: userMessage,
      stream: true,
      max_output_tokens: 2000
    }

    // Add previous_response_id if available for conversation continuity
    if (previousResponseId) {
      payload.previous_response_id = previousResponseId
    }

    const response = await fetch(RESPONSES_API_URL, {
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
    let currentResponseId = null

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
        if (!line.startsWith('event: ') && !line.startsWith('data: ')) continue

        if (line.startsWith('data: ')) {
          const data = line.slice(6)

          if (data === '[DONE]') {
            continue
          }

          try {
            const json = JSON.parse(data)

            // Capture response ID from the response.created event
            if (json.type === 'response.created' && json.response?.id) {
              currentResponseId = json.response.id
              if (onResponseId) {
                onResponseId(currentResponseId)
              }
            }

            // Handle content deltas (streaming text)
            if (json.type === 'content.delta' && json.delta?.text) {
              onChunk(json.delta.text)
            }

            // Alternative: handle output_text delta if structured differently
            if (json.type === 'response.output_item.delta' && json.delta?.content?.[0]?.text) {
              onChunk(json.delta.content[0].text)
            }
          } catch (e) {
            // Ignore parse errors for malformed chunks
            console.warn('Failed to parse streaming chunk:', e)
          }
        }
      }
    }

    // Process any remaining buffer
    if (buffer.trim() && buffer.trim().startsWith('data: ')) {
      const data = buffer.slice(6).trim()
      if (data !== '[DONE]') {
        try {
          const json = JSON.parse(data)
          if (json.type === 'content.delta' && json.delta?.text) {
            onChunk(json.delta.text)
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
 * Create a new vector store using the OpenAI API.
 * Returns the created vector store ID.
 */
export async function createVectorStore(apiKey, name, options = {}) {
  if (!apiKey || !apiKey.trim()) {
    throw new Error('APIキーが設定されていません。設定から入力してください。')
  }

  try {
    const payload = {}

    payload.name = name && name.trim() ? name.trim() : 'knowledge_base'

    if (options.description && options.description.trim()) {
      payload.description = options.description.trim()
    }

    if (options.expiresAfter) {
      payload.expires_after = options.expiresAfter
    }

    if (Array.isArray(options.fileIds) && options.fileIds.length > 0) {
      payload.file_ids = options.fileIds
    }

    if (options.metadata && typeof options.metadata === 'object') {
      payload.metadata = options.metadata
    }

    const response = await fetch(VECTOR_STORES_API_URL, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const errorText = await response.text()
      let errorMessage = `Vector Store 作成時に API エラーが発生しました (${response.status})`
      try {
        const parsed = JSON.parse(errorText)
        if (parsed.error?.message) {
          errorMessage = parsed.error.message
        }
      } catch (e) {
        // ignore parse error
      }
      throw new Error(errorMessage)
    }

    const data = await response.json()
    if (!data.id) {
      throw new Error('Vector Store ID を取得できませんでした。')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Vector Store 作成中にエラーが発生しました。')
  }
}

/**
 * Get or create the knowledge_base vector store
 * Returns the vector store object
 */
export async function getOrCreateKnowledgeBase(apiKey) {
  if (!apiKey || !apiKey.trim()) {
    throw new Error('APIキーが設定されていません。設定から入力してください。')
  }

  try {
    // List all vector stores
    const stores = await listVectorStores(apiKey, { limit: 100 })

    // Find knowledge_base
    const knowledgeBase = stores.find(store => store.name === 'knowledge_base')

    if (knowledgeBase) {
      return knowledgeBase
    }

    // Create new knowledge_base if not found
    return await createVectorStore(apiKey, 'knowledge_base')
  } catch (error) {
    throw new Error(error.message || 'knowledge_base の取得または作成中にエラーが発生しました。')
  }
}

/**
 * List vector stores with optional pagination.
 * Returns an array of vector store objects.
 */
export async function listVectorStores(apiKey, { limit = 50, after = null } = {}) {
  if (!apiKey || !apiKey.trim()) {
    throw new Error('APIキーが設定されていません。設定から入力してください。')
  }

  try {
    const url = new URL(VECTOR_STORES_API_URL)
    if (limit) {
      url.searchParams.set('limit', String(limit))
    }
    if (after) {
      url.searchParams.set('after', after)
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${apiKey}`
      }
    })

    if (!response.ok) {
      const errorText = await response.text()
      let errorMessage = `Vector Store 一覧取得時に API エラーが発生しました (${response.status})`
      try {
        const parsed = JSON.parse(errorText)
        if (parsed.error?.message) {
          errorMessage = parsed.error.message
        }
      } catch (e) {
        // ignore parse error
      }
      throw new Error(errorMessage)
    }

    const data = await response.json()
    if (Array.isArray(data.data)) {
      return data.data
    }
    return []
  } catch (error) {
    throw new Error(error.message || 'Vector Store 一覧取得中にエラーが発生しました。')
  }
}

/**
 * Upload a file and attach it to a vector store.
 * Returns the uploaded file ID.
 */
export async function uploadFileToVectorStore(apiKey, vectorStoreId, file) {
  if (!apiKey || !apiKey.trim()) {
    throw new Error('APIキーが設定されていません。設定から入力してください。')
  }

  if (!vectorStoreId || !vectorStoreId.trim()) {
    throw new Error('Vector Store ID が設定されていません。先に Vector Store を作成または設定してください。')
  }

  if (!file) {
    throw new Error('アップロードするファイルが選択されていません。')
  }

  // 1. Upload file to Files API
  let fileId
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('purpose', 'assistants')

    const fileResponse = await fetch(FILES_API_URL, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`
        // Content-Type is set automatically for FormData
      },
      body: formData
    })

    if (!fileResponse.ok) {
      const errorText = await fileResponse.text()
      let errorMessage = `ファイルアップロード時に API エラーが発生しました (${fileResponse.status})`
      try {
        const parsed = JSON.parse(errorText)
        if (parsed.error?.message) {
          errorMessage = parsed.error.message
        }
      } catch (e) {
        // ignore parse error
      }
      throw new Error(errorMessage)
    }

    const fileData = await fileResponse.json()
    if (!fileData.id) {
      throw new Error('アップロードしたファイルの ID を取得できませんでした。')
    }
    fileId = fileData.id
  } catch (error) {
    throw new Error(error.message || 'ファイルアップロード中にエラーが発生しました。')
  }

  // 2. Attach file to vector store
  try {
    const attachResponse = await fetch(
      `${VECTOR_STORES_API_URL}/${encodeURIComponent(vectorStoreId)}/files`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ file_id: fileId })
      }
    )

    if (!attachResponse.ok) {
      const errorText = await attachResponse.text()
      let errorMessage = `Vector Store へのファイル追加時に API エラーが発生しました (${attachResponse.status})`
      try {
        const parsed = JSON.parse(errorText)
        if (parsed.error?.message) {
          errorMessage = parsed.error.message
        }
      } catch (e) {
        // ignore parse error
      }
      throw new Error(errorMessage)
    }

    return fileId
  } catch (error) {
    throw new Error(error.message || 'Vector Store へのファイル追加中にエラーが発生しました。')
  }
}

/**
 * Retrieve details of an existing vector store.
 * Returns the vector store object.
 */
export async function getVectorStore(apiKey, vectorStoreId) {
  if (!apiKey || !apiKey.trim()) {
    throw new Error('APIキーが設定されていません。設定から入力してください。')
  }

  if (!vectorStoreId || !vectorStoreId.trim()) {
    throw new Error('Vector Store ID が設定されていません。')
  }

  try {
    const response = await fetch(
      `${VECTOR_STORES_API_URL}/${encodeURIComponent(vectorStoreId)}`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${apiKey}`
        }
      }
    )

    if (!response.ok) {
      const errorText = await response.text()
      let errorMessage = `Vector Store 取得時に API エラーが発生しました (${response.status})`
      try {
        const parsed = JSON.parse(errorText)
        if (parsed.error?.message) {
          errorMessage = parsed.error.message
        }
      } catch (e) {
        // ignore parse error
      }
      throw new Error(errorMessage)
    }

    const data = await response.json()
    return data
  } catch (error) {
    throw new Error(error.message || 'Vector Store 取得中にエラーが発生しました。')
  }
}

/**
 * List files attached to a vector store.
 * Returns an array of vector store file objects.
 */
export async function listVectorStoreFiles(apiKey, vectorStoreId, limit = 20) {
  if (!apiKey || !apiKey.trim()) {
    throw new Error('APIキーが設定されていません。設定から入力してください。')
  }

  if (!vectorStoreId || !vectorStoreId.trim()) {
    throw new Error('Vector Store ID が設定されていません。')
  }

  try {
    const url = new URL(
      `${VECTOR_STORES_API_URL}/${encodeURIComponent(vectorStoreId)}/files`
    )
    url.searchParams.set('limit', String(limit))

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${apiKey}`
      }
    })

    if (!response.ok) {
      const errorText = await response.text()
      let errorMessage = `Vector Store ファイル一覧取得時に API エラーが発生しました (${response.status})`
      try {
        const parsed = JSON.parse(errorText)
        if (parsed.error?.message) {
          errorMessage = parsed.error.message
        }
      } catch (e) {
        // ignore parse error
      }
      throw new Error(errorMessage)
    }

    const data = await response.json()
    if (Array.isArray(data.data)) {
      return data.data
    }
    return []
  } catch (error) {
    throw new Error(error.message || 'Vector Store ファイル一覧取得中にエラーが発生しました。')
  }
}

/**
 * Retrieve file metadata (e.g. filename) from Files API.
 * Returns the file object.
 */
export async function getFileMetadata(apiKey, fileId) {
  if (!apiKey || !apiKey.trim()) {
    throw new Error('APIキーが設定されていません。設定から入力してください。')
  }

  if (!fileId || !fileId.trim()) {
    throw new Error('ファイル ID が指定されていません。')
  }

  try {
    const response = await fetch(
      `${FILES_API_URL}/${encodeURIComponent(fileId)}`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${apiKey}`
        }
      }
    )

    if (!response.ok) {
      const errorText = await response.text()
      let errorMessage = `ファイル情報取得時に API エラーが発生しました (${response.status})`
      try {
        const parsed = JSON.parse(errorText)
        if (parsed.error?.message) {
          errorMessage = parsed.error.message
        }
      } catch (e) {
        // ignore parse error
      }
      throw new Error(errorMessage)
    }

    const data = await response.json()
    return data
  } catch (error) {
    throw new Error(error.message || 'ファイル情報取得中にエラーが発生しました。')
  }
}

/**
 * Delete a file from a vector store.
 * Returns true if deletion succeeded.
 */
export async function deleteVectorStoreFile(apiKey, vectorStoreId, fileId) {
  if (!apiKey || !apiKey.trim()) {
    throw new Error('APIキーが設定されていません。設定から入力してください。')
  }

  if (!vectorStoreId || !vectorStoreId.trim()) {
    throw new Error('Vector Store ID が設定されていません。')
  }

  if (!fileId || !fileId.trim()) {
    throw new Error('削除するファイル ID が指定されていません。')
  }

  try {
    const response = await fetch(
      `${VECTOR_STORES_API_URL}/${encodeURIComponent(
        vectorStoreId
      )}/files/${encodeURIComponent(fileId)}`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
      }
    )

    if (!response.ok) {
      const errorText = await response.text()
      let errorMessage = `Vector Store ファイル削除時に API エラーが発生しました (${response.status})`
      try {
        const parsed = JSON.parse(errorText)
        if (parsed.error?.message) {
          errorMessage = parsed.error.message
        }
      } catch (e) {
        // ignore parse error
      }
      throw new Error(errorMessage)
    }

    const data = await response.json()
    return !!data.deleted
  } catch (error) {
    throw new Error(error.message || 'Vector Store ファイル削除中にエラーが発生しました。')
  }
}

/**
 * Delete an entire vector store.
 * Returns true if deletion succeeded.
 */
export async function deleteVectorStore(apiKey, vectorStoreId) {
  if (!apiKey || !apiKey.trim()) {
    throw new Error('APIキーが設定されていません。設定から入力してください。')
  }

  if (!vectorStoreId || !vectorStoreId.trim()) {
    throw new Error('Vector Store ID が設定されていません。')
  }

  try {
    const response = await fetch(
      `${VECTOR_STORES_API_URL}/${encodeURIComponent(vectorStoreId)}`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
      }
    )

    if (!response.ok) {
      const errorText = await response.text()
      let errorMessage = `Vector Store 削除時に API エラーが発生しました (${response.status})`
      try {
        const parsed = JSON.parse(errorText)
        if (parsed.error?.message) {
          errorMessage = parsed.error.message
        }
      } catch (e) {
        // ignore parse error
      }
      throw new Error(errorMessage)
    }

    const data = await response.json()
    return !!data.deleted
  } catch (error) {
    throw new Error(error.message || 'Vector Store 削除中にエラーが発生しました。')
  }
}

/**
 * Call OpenAI Responses API with File Search tool (non-streaming)
 * Uses a Vector Store ID to let the model search your files.
 * @param {string} apiKey
 * @param {string} message
 * @param {string} vectorStoreId
 * @param {string|null} previousResponseId
 * @param {function} onChunk - callback for response text
 * @param {function} onError - error callback
 * @param {function} [onResponseId] - optional callback with response.id
 * @param {function} [onCitations] - optional callback with citations array
 */
export async function callOpenAIFileSearch(
  apiKey,
  message,
  vectorStoreId,
  previousResponseId,
  onChunk,
  onError,
  onResponseId,
  onCitations
) {
  if (!apiKey || !apiKey.trim()) {
    onError('APIキーが設定されていません。設定から入力してください。')
    return
  }

  if (!vectorStoreId || !vectorStoreId.trim()) {
    onError('Vector Store ID が設定されていません。設定から入力してください。')
    return
  }

  try {
    const payload = {
      // File Search は Responses API 用のモデル gpt-5.1 を利用
      model: 'gpt-5.1',
      input: message,
      instructions: `あなたは高精度なRAG（Retrieval-Augmented Generation）リサーチアシスタントです。

## 基本原則
1. **検索結果に基づく回答**
   - File Search ツールで取得した情報のみを根拠に回答してください
   - 検索結果に含まれない情報については推測や補足を行わないでください
   - 引用情報は自動的にメッセージの下部に表示されるため、本文中で個別に列挙する必要はありません

2. **回答の構造**
   - 簡潔で明確な回答を心がけてください
   - 構成: 結論 → 詳細説明 → 関連情報
   - Markdown形式で読みやすく整形してください（見出し、リスト、コードブロックなど）

3. **品質管理**
   - 検索結果が質問に対して不十分な場合は、その旨を正直に伝えてください
   - 必要に応じて、追加で検索すべきキーワードや資料を提案してください
   - 複数の検索結果がある場合は、情報を統合して矛盾がないか確認してください

4. **言語と形式**
   - 回答は日本語で行ってください
   - 専門用語は必要に応じて説明を加えてください
   - コードや技術的な内容は適切なフォーマットで表示してください`,
      reasoning: {
        effort: 'none'
      },
      tool_choice: 'auto',
      tools: [
        {
          type: 'file_search',
          vector_store_ids: [vectorStoreId],
          // 取得する検索結果数を制限（公式ドキュメントに合わせたオプション）
          max_num_results: 10
        }
      ],
      // 検索結果の詳細（引用情報）を取得
      include: ['file_search_call.results']
    }

    if (previousResponseId) {
      payload.previous_response_id = previousResponseId
    }

    const response = await fetch(RESPONSES_API_URL, {
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

    const data = await response.json()

    if (onResponseId && data && typeof data.id === 'string') {
      onResponseId(data.id)
    }

    // Try to extract assistant text from Responses API structure
    let text = ''
    let citations = []

    if (typeof data.output_text === 'string') {
      text = data.output_text
    } else if (Array.isArray(data.output) && data.output.length > 0) {
      // file_search_call と message の2つ以上の output が返るケースに対応
      const messageItem = data.output.find(item => item.type === 'message')
      const fileSearchItem = data.output.find(item => item.type === 'file_search_call')

      // Extract citations from file_search_call
      if (fileSearchItem && Array.isArray(fileSearchItem.results)) {
        citations = fileSearchItem.results.map(result => ({
          fileId: result.file_id || '',
          fileName: result.file_name || result.filename || 'Unknown File',
          content: result.content || result.text || '',
          score: result.score || 0,
          chunkId: result.chunk_id || null
        }))
      }

      if (messageItem && Array.isArray(messageItem.content)) {
        for (const content of messageItem.content) {
          // 公式サンプルでは type: "output_text", text: "..." という構造
          if (typeof content.text === 'string') {
            text += content.text
          } else if (
            content.type === 'output_text' &&
            typeof content.output_text === 'string'
          ) {
            text += content.output_text
          }
        }
      }
    }

    if (!text) {
      onError('レスポンスからテキストを取得できませんでした。')
      return
    }

    // Send citations if callback is provided
    if (onCitations && citations.length > 0) {
      onCitations(citations)
    }

    onChunk(text)
  } catch (error) {
    onError(`エラーが発生しました: ${error.message}`)
  }
}
