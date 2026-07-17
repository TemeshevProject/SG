import type { ApkConfiguration, DirectionLanes, PowerType, SegmentType } from '../types'

interface Props {
  config: ApkConfiguration
  onChange: (cfg: ApkConfiguration) => void
}

function DirectionTable({
  title,
  directions,
  onChange,
}: {
  title: string
  directions: DirectionLanes[]
  onChange: (dirs: DirectionLanes[]) => void
}) {
  const setCount = (n: number) => {
    const next = Array.from({ length: n }, (_, i) => directions[i] ?? { lanes: 2 })
    onChange(next)
  }

  return (
    <div className="sub-block">
      <div className="row">
        <strong>{title}</strong>
        <label className="inline">
          Направлений
          <input
            type="number"
            min={1}
            max={8}
            value={directions.length}
            onChange={(e) => setCount(Number(e.target.value))}
          />
        </label>
      </div>
      <table className="lane-table">
        <thead>
          <tr>
            <th>№</th>
            <th>Кол-во полос</th>
          </tr>
        </thead>
        <tbody>
          {directions.map((d, i) => (
            <tr key={i}>
              <td>{i + 1}</td>
              <td>
                <input
                  type="number"
                  min={1}
                  max={12}
                  value={d.lanes}
                  onChange={(e) => {
                    const next = [...directions]
                    next[i] = { lanes: Number(e.target.value) }
                    onChange(next)
                  }}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function ConfigEditor({ config, onChange }: Props) {
  const patch = (partial: Partial<ApkConfiguration>) => onChange({ ...config, ...partial })
  const isConstant = config.power_type === 'constant'

  return (
    <div className="editor panel">
      <h2>Параметры конфигурации</h2>

      <div className="grid-2">
        <label>
          Название
          <input value={config.label} onChange={(e) => patch({ label: e.target.value })} />
        </label>
        <label>
          Кол-во АПК
          <input
            type="number"
            min={1}
            value={config.apk_count}
            onChange={(e) => patch({ apk_count: Number(e.target.value) })}
          />
        </label>
        <label>
          Вид участка
          <select
            value={config.segment}
            onChange={(e) => patch({ segment: e.target.value as SegmentType })}
          >
            <option value="LU">Линейный участок (ЛУ)</option>
            <option value="P">Перекрёсток (П)</option>
          </select>
        </label>
        <label>
          Питание
          <select
            value={config.power_type}
            onChange={(e) => patch({ power_type: e.target.value as PowerType })}
          >
            <option value="lighting">Освещение</option>
            <option value="constant">Постоянное питание</option>
          </select>
        </label>
      </div>

      {isConstant && (
        <div className="sub-block">
          <h3>Контроллеры Specto</h3>
          {config.segment === 'P' && (
            <p className="hint">Specto B для П: количество 1 или 2</p>
          )}
          <div className="checkbox-row">
            <label>
              <input
                type="checkbox"
                checked={config.specto_b.enabled}
                onChange={(e) =>
                  patch({
                    specto_b: {
                      ...config.specto_b,
                      enabled: e.target.checked,
                      quantity: e.target.checked ? Math.max(1, config.specto_b.quantity) : 0,
                    },
                  })
                }
              />
              Specto B
            </label>
            {config.specto_b.enabled && (
              <input
                type="number"
                min={config.segment === 'P' ? 1 : 0}
                max={config.segment === 'P' ? 2 : 99}
                value={config.specto_b.quantity}
                onChange={(e) =>
                  patch({ specto_b: { ...config.specto_b, quantity: Number(e.target.value) } })
                }
              />
            )}
          </div>
          <div className="checkbox-row">
            <label>
              <input
                type="checkbox"
                checked={config.specto_a.enabled}
                onChange={(e) =>
                  patch({
                    specto_a: {
                      ...config.specto_a,
                      enabled: e.target.checked,
                      quantity: e.target.checked ? Math.max(1, config.specto_a.quantity) : 0,
                    },
                  })
                }
              />
              Specto A
            </label>
            {config.specto_a.enabled && (
              <>
                <input
                  type="number"
                  min={1}
                  value={config.specto_a.quantity}
                  onChange={(e) =>
                    patch({ specto_a: { ...config.specto_a, quantity: Number(e.target.value) } })
                  }
                />
                <select
                  value={config.specto_a.voltage ?? '24V'}
                  onChange={(e) =>
                    patch({
                      specto_a: {
                        ...config.specto_a,
                        voltage: e.target.value as '24V' | '220V',
                      },
                    })
                  }
                >
                  <option value="24V">24В</option>
                  <option value="220V">220В</option>
                </select>
              </>
            )}
          </div>
        </div>
      )}

      <div className="sub-block">
        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={config.radar.enabled}
            onChange={(e) => patch({ radar: { ...config.radar, enabled: e.target.checked } })}
          />
          <strong>Радар доплера</strong>
        </label>
        {config.radar.enabled && (
          <DirectionTable
            title="Направления радара"
            directions={config.radar.directions}
            onChange={(directions) => patch({ radar: { ...config.radar, directions } })}
          />
        )}
      </div>

      <div className="sub-block">
        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={config.hr_camera.enabled}
            onChange={(e) => patch({ hr_camera: { ...config.hr_camera, enabled: e.target.checked } })}
          />
          <strong>Камера высокого разрешения</strong>
        </label>
        {config.hr_camera.enabled && (
          <DirectionTable
            title="Направления камеры ВР"
            directions={config.hr_camera.directions}
            onChange={(directions) => patch({ hr_camera: { ...config.hr_camera, directions } })}
          />
        )}
      </div>

      <div className="sub-block">
        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={config.lvm.enabled}
            onChange={(e) => patch({ lvm: { enabled: e.target.checked } })}
          />
          <strong>ЛВМ (локально-вычислительный модуль)</strong>
        </label>
      </div>
    </div>
  )
}
