import type { ProjectRequest, ProjectSummary } from './types'

export async function calculateProject(req: ProjectRequest): Promise<ProjectSummary> {
  const res = await fetch('/api/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Ошибка расчёта')
  }
  return res.json()
}

export async function exportExcel(req: ProjectRequest, filename: string) {
  const res = await fetch('/api/export/excel', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) throw new Error('Ошибка экспорта')
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${filename}.xlsx`
  a.click()
  URL.revokeObjectURL(url)
}
