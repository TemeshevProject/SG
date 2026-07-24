import type { ProjectSummary } from '../types'

function fmt(n: number | null | undefined) {
  if (n == null) return '—'
  return new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 }).format(n) + ' ₸'
}

interface Props {
  result: ProjectSummary
}

export function ResultsPanel({ result }: Props) {
  return (
    <section className="results panel">
      <div className="results-head">
        <div>
          <h2>Результат: {result.name}</h2>
          <p className="muted">
            {result.manufacturer} · {result.consolidated.length} позиций
            {result.missing_prices > 0 && ` · без цены: ${result.missing_prices}`}
          </p>
        </div>
        <div className="total-box">
          <span>Себестоимость</span>
          <strong>{fmt(result.total_cost_kzt)}</strong>
        </div>
      </div>

      <div className="config-totals">
        {result.configurations.map((c) => (
          <div key={c.label} className="config-total-card">
            <strong>{c.label}</strong>
            <span>{c.apk_count} АПК · {c.line_count} поз.</span>
            <span>{fmt(c.subtotal_kzt)}</span>
          </div>
        ))}
      </div>

      <div className="table-wrap">
        <table className="results-table">
          <thead>
            <tr>
              <th>№</th>
              <th>Описание</th>
              <th>Наименование</th>
              <th>Ед.</th>
              <th>Кол-во</th>
              <th>Цена</th>
              <th>Сумма</th>
            </tr>
          </thead>
          <tbody>
            {result.consolidated.map((row) => (
              <tr key={row.name} className={row.unit_price_kzt == null ? 'no-price' : ''}>
                <td>{row.row}</td>
                <td>{row.description}</td>
                <td>{row.name}</td>
                <td>{row.unit}</td>
                <td>{row.total_qty}</td>
                <td>{fmt(row.unit_price_kzt)}</td>
                <td>{fmt(row.total_price_kzt)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
