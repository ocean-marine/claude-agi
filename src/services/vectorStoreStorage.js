const CONFIG_KEY = 'openai_vector_store_configs'
const SELECTED_KEY = 'openai_selected_vector_store_id'
const LEGACY_SINGLE_KEY = 'openai_vector_store_id'
const ACTIVE_TEMP_KEY = 'openai_active_temp_vector_store'
const TEMP_LIST_KEY = 'openai_temporary_vector_stores'

function isBrowser() {
  return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined'
}

function readJSON(key, fallback) {
  if (!isBrowser()) {
    return fallback
  }
  try {
    const raw = window.localStorage.getItem(key)
    if (!raw) {
      return fallback
    }
    return JSON.parse(raw)
  } catch (error) {
    console.warn('Failed to parse localStorage item', key, error)
    return fallback
  }
}

function writeJSON(key, value) {
  if (!isBrowser()) {
    return
  }
  try {
    window.localStorage.setItem(key, JSON.stringify(value))
  } catch (error) {
    console.warn('Failed to set localStorage item', key, error)
  }
}

function maybeMigrateLegacyVectorStore() {
  if (!isBrowser()) {
    return
  }

  const legacyId = window.localStorage.getItem(LEGACY_SINGLE_KEY)
  if (!legacyId) {
    return
  }

  const configs = readJSON(CONFIG_KEY, [])
  const exists = configs.some((item) => item.id === legacyId)
  if (!exists) {
    configs.push({ id: legacyId, label: 'Vector Store' })
    writeJSON(CONFIG_KEY, configs)
  }

  // Clean up legacy key so we do not migrate again
  window.localStorage.removeItem(LEGACY_SINGLE_KEY)
}

export function getVectorStoreConfigs() {
  if (!isBrowser()) {
    return []
  }

  maybeMigrateLegacyVectorStore()
  const configs = readJSON(CONFIG_KEY, [])
  if (!Array.isArray(configs)) {
    return []
  }
  // Remove malformed entries
  const sanitized = configs.filter((item) => item && typeof item.id === 'string' && item.id.trim())
  if (sanitized.length !== configs.length) {
    writeJSON(CONFIG_KEY, sanitized)
  }
  return sanitized
}

export function saveVectorStoreConfigs(configs) {
  writeJSON(CONFIG_KEY, configs)
}

export function addVectorStoreConfig(config) {
  const configs = getVectorStoreConfigs()
  const exists = configs.some((item) => item.id === config.id)
  if (exists) {
    return configs
  }
  const next = [...configs, { id: config.id, label: config.label || config.id }]
  saveVectorStoreConfigs(next)
  return next
}

export function removeVectorStoreConfig(id) {
  const configs = getVectorStoreConfigs().filter((item) => item.id !== id)
  saveVectorStoreConfigs(configs)
  return configs
}

export function getSelectedManualVectorStoreId() {
  if (!isBrowser()) {
    return null
  }
  return window.localStorage.getItem(SELECTED_KEY)
}

export function setSelectedManualVectorStoreId(id) {
  if (!isBrowser()) {
    return
  }
  if (!id) {
    window.localStorage.removeItem(SELECTED_KEY)
    return
  }
  window.localStorage.setItem(SELECTED_KEY, id)
}

export function getActiveTemporaryVectorStore() {
  const temp = readJSON(ACTIVE_TEMP_KEY, null)
  if (!temp || !temp.id) {
    return null
  }
  return temp
}

export function setActiveTemporaryVectorStore(temp) {
  if (!temp || !temp.id) {
    clearActiveTemporaryVectorStore()
    return
  }
  writeJSON(ACTIVE_TEMP_KEY, temp)
  addTemporaryVectorStore(temp)
}

export function clearActiveTemporaryVectorStore() {
  if (!isBrowser()) {
    return
  }
  window.localStorage.removeItem(ACTIVE_TEMP_KEY)
}

export function getTemporaryVectorStores() {
  const list = readJSON(TEMP_LIST_KEY, [])
  if (!Array.isArray(list)) {
    return []
  }
  return list.filter((item) => item && typeof item.id === 'string')
}

export function saveTemporaryVectorStores(list) {
  writeJSON(TEMP_LIST_KEY, list)
}

export function addTemporaryVectorStore(store) {
  const list = getTemporaryVectorStores()
  if (list.some((item) => item.id === store.id)) {
    // update metadata
    const next = list.map((item) => (item.id === store.id ? { ...item, ...store } : item))
    saveTemporaryVectorStores(next)
    return next
  }
  const next = [...list, store]
  saveTemporaryVectorStores(next)
  return next
}

export function removeTemporaryVectorStore(id) {
  const list = getTemporaryVectorStores().filter((item) => item.id !== id)
  saveTemporaryVectorStores(list)
  return list
}
