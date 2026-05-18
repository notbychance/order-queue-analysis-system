import { describe, expect, it } from 'vitest'

import { historyFileService } from '@/services/historyFileService'
import { createQueueHistoryItem } from '@/test/factories'

describe('historyFileService', () => {
  it('builds export file with metadata and items', () => {
    const item = createQueueHistoryItem()
    const exportFile = historyFileService.buildExportFile([item])

    expect(exportFile.schemaVersion).toBe(1)
    expect(exportFile.source).toBe('queue-analysis-web')
    expect(Date.parse(exportFile.exportedAt)).not.toBeNaN()
    expect(exportFile.items).toEqual([item])
  })

  it('reads history from exported JSON file', async () => {
    const item = createQueueHistoryItem()
    const file = new File(
      [JSON.stringify({ schemaVersion: 1, source: 'queue-analysis-web', items: [item] })],
      'history.json',
      { type: 'application/json' },
    )

    await expect(historyFileService.readJsonFile(file)).resolves.toEqual([item])
  })

  it('reads history from plain array JSON file', async () => {
    const item = createQueueHistoryItem()
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

  it('rejects empty JSON files', async () => {
    const file = new File(['   '], 'history.json', { type: 'application/json' })

    await expect(historyFileService.readJsonFile(file)).rejects.toThrow('Файл истории пуст')
  })

  it('rejects invalid JSON', async () => {
    const file = new File(['{bad json'], 'history.json', { type: 'application/json' })

    await expect(historyFileService.readJsonFile(file)).rejects.toThrow(
      'Файл истории содержит некорректный JSON',
    )
  })

  it('rejects JSON without valid history items', async () => {
    const file = new File([JSON.stringify({ items: [{ id: '' }] })], 'history.json', {
      type: 'application/json',
    })

    await expect(historyFileService.readJsonFile(file)).rejects.toThrow(
      'В файле не найдено корректных записей истории',
    )
  })
})
