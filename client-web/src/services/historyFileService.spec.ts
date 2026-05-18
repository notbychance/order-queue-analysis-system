import { describe, expect, it } from 'vitest'

import { historyFileService } from './historyFileService'
import { createQueueHistoryItem } from '@/test/factories'

describe('historyFileService', () => {
  it('builds export payload for local history', () => {
    const item = createQueueHistoryItem()
    const payload = historyFileService.buildExportFile([item])

    expect(payload.schemaVersion).toBe(1)
    expect(payload.source).toBe('queue-analysis-web')
    expect(payload.items).toEqual([item])
    expect(Date.parse(payload.exportedAt)).not.toBeNaN()
  })

  it('reads valid history from JSON file with items wrapper', async () => {
    const item = createQueueHistoryItem()
    const file = new File([JSON.stringify({ items: [item] })], 'history.json', {
      type: 'application/json',
    })

    await expect(historyFileService.readJsonFile(file)).resolves.toEqual([item])
  })

  it('reads valid history from plain array JSON file', async () => {
    const item = createQueueHistoryItem({ id: 'history-array-item' })
    const file = new File([JSON.stringify([item])], 'history.json', {
      type: 'application/json',
    })

    await expect(historyFileService.readJsonFile(file)).resolves.toEqual([item])
  })

  it('rejects non-json files', async () => {
    const file = new File(['[]'], 'history.txt', { type: 'text/plain' })

    await expect(historyFileService.readJsonFile(file)).rejects.toThrow(
      'Можно импортировать только JSON-файл истории',
    )
  })

  it('rejects empty json files', async () => {
    const file = new File(['  '], 'history.json', { type: 'application/json' })

    await expect(historyFileService.readJsonFile(file)).rejects.toThrow('Файл истории пуст')
  })

  it('rejects invalid json', async () => {
    const file = new File(['{bad json'], 'history.json', { type: 'application/json' })

    await expect(historyFileService.readJsonFile(file)).rejects.toThrow(
      'Файл истории содержит некорректный JSON',
    )
  })

  it('rejects json without valid history items', async () => {
    const file = new File([JSON.stringify({ items: [{ id: '' }] })], 'history.json', {
      type: 'application/json',
    })

    await expect(historyFileService.readJsonFile(file)).rejects.toThrow(
      'В файле не найдено корректных записей истории',
    )
  })
})
