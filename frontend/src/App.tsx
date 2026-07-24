import { useMemo, useState } from 'react'
import { calculateProject, exportExcel } from './api'
import {
  type ApkConfiguration,
  type Manufacturer,
  type ProjectSummary,
  configToPayload,
  newConfiguration,
} from './types'
import { ConfigEditor } from './components/ConfigEditor'
import { ResultsPanel } from './components/ResultsPanel'
import './App.css'

function segmentLabel(s: string) {
  return s === 'LU' ? 'Линейный участок' : 'Перекрёсток'
}

function powerLabel(p: string) {
  return p === 'constant' ? 'Постоянное питание' : 'Освещение'
}

export default function App() {
  const [name, setName] = useState('Новый проект')
  const [manufacturer, setManufacturer] = useState<Manufacturer>('Hikvision')
  const [configs, setConfigs] = useState<ApkConfiguration[]>([
    newConfiguration({ label: 'ЛУ · Освещение', segment: 'LU', power_type: 'lighting', apk_count: 50 }),
    newConfiguration({ label: 'ЛУ · П.П.', segment: 'LU', power_type: 'constant', apk_count: 20 }),
  ])
  const [editingId, setEditingId] = useState<string | null>(configs[0]?.id ?? null)
  const [result, setResult] = useState<ProjectSummary | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const buildRequest = () => ({
    name,
    apk_version: '4.0',
    manufacturer,
    configurations: configs.map(configToPayload),
  })

  const editing = useMemo(
    () => configs.find((c) => c.id === editingId) ?? null,
    [configs, editingId],
  )

  const updateConfig = (updated: ApkConfiguration) => {
    setConfigs((prev) => prev.map((c) => (c.id === updated.id ? updated : c)))
  }

  const addConfig = () => {
    const cfg = newConfiguration({ label: 'Новая конфигурация' })
    setConfigs((prev) => [...prev, cfg])
    setEditingId(cfg.id)
  }

  const removeConfig = (id: string) => {
    setConfigs((prev) => prev.filter((c) => c.id !== id))
    if (editingId === id) setEditingId(null)
  }

  const handleCalculate = async () => {
    setLoading(true)
    setError(null)
    try {
      const summary = await calculateProject(buildRequest())
      setResult(summary)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <p className="eyebrow">Sergek · АПК v4.0</p>
          <h1>Калькулятор себестоимости</h1>
        </div>
        <div className="header-actions">
          <button className="btn primary" onClick={handleCalculate} disabled={loading || configs.length === 0}>
            {loading ? 'Считаем…' : 'Рассчитать'}
          </button>
          {result && (
            <button
              className="btn ghost"
              onClick={() => exportExcel(buildRequest(), name || 'spec')}
            >
              Excel
            </button>
          )}
        </div>
      </header>

      {error && <div className="banner error">{error}</div>}

      <div className="layout">
        <aside className="sidebar">
          <section className="panel">
            <h2>Проект</h2>
            <label>
              Название
              <input value={name} onChange={(e) => setName(e.target.value)} />
            </label>
            <label>
              Производитель
              <select
                value={manufacturer}
                onChange={(e) => setManufacturer(e.target.value as Manufacturer)}
              >
                <option value="Hikvision">Hikvision</option>
                <option value="Dahua">Dahua</option>
              </select>
            </label>
          </section>

          <section className="panel">
            <div className="panel-head">
              <h2>Конфигурации АПК</h2>
              <button className="btn ghost" onClick={addConfig}>+ Добавить</button>
            </div>
            <div className="config-list">
              {configs.map((cfg) => (
                <button
                  key={cfg.id}
                  className={`config-card ${editingId === cfg.id ? 'active' : ''}`}
                  onClick={() => setEditingId(cfg.id)}
                >
                  <div className="config-card-top">
                    <strong>{cfg.label || 'Без названия'}</strong>
                    <span
                      className="icon-btn"
                      role="button"
                      tabIndex={0}
                      onClick={(e) => { e.stopPropagation(); removeConfig(cfg.id) }}
                      onKeyDown={(e) => e.key === 'Enter' && removeConfig(cfg.id)}
                    >×</span>
                  </div>
                  <p>{segmentLabel(cfg.segment)} · {powerLabel(cfg.power_type)}</p>
                  <p className="muted">{cfg.apk_count} АПК</p>
                </button>
              ))}
            </div>
          </section>
        </aside>

        <main className="main">
          {editing ? (
            <ConfigEditor config={editing} onChange={updateConfig} />
          ) : (
            <div className="empty">Выберите или добавьте конфигурацию</div>
          )}
        </main>
      </div>

      {result && <ResultsPanel result={result} />}
    </div>
  )
}
