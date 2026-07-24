export type SegmentType = 'LU' | 'P'
export type PowerType = 'constant' | 'lighting'
export type Manufacturer = 'Hikvision' | 'Dahua'
export type SpectoVoltage = '24V' | '220V'

export interface DirectionLanes {
  lanes: number
}

export interface RadarConfig {
  enabled: boolean
  directions: DirectionLanes[]
}

export interface HrCameraConfig {
  enabled: boolean
  directions: DirectionLanes[]
}

export interface SpectoConfig {
  enabled: boolean
  quantity: number
  voltage: SpectoVoltage | null
}

export interface LvmConfig {
  enabled: boolean
}

export interface ApkConfiguration {
  id: string
  label: string
  segment: SegmentType
  power_type: PowerType
  apk_count: number
  specto_a: SpectoConfig
  specto_b: SpectoConfig
  radar: RadarConfig
  hr_camera: HrCameraConfig
  lvm: LvmConfig
}

export interface ProjectRequest {
  name: string
  apk_version: string
  manufacturer: Manufacturer
  configurations: Omit<ApkConfiguration, 'id'>[]
}

export interface ConsolidatedItem {
  row: number
  module: string | null
  description: string
  name: string
  unit: string
  total_qty: number
  unit_price_kzt: number | null
  total_price_kzt: number | null
  breakdown: Array<{
    config_label: string
    segment: string
    power_type: string
    apk_count: number
    qty_per_apk: number
    total_qty: number
  }>
}

export interface ProjectSummary {
  name: string
  apk_version: string
  manufacturer: string
  configurations: Array<{
    label: string
    segment: string
    power_type: string
    apk_count: number
    line_count: number
    subtotal_kzt: number | null
  }>
  line_items: unknown[]
  consolidated: ConsolidatedItem[]
  total_cost_kzt: number | null
  missing_prices: number
}

export function newConfiguration(partial?: Partial<ApkConfiguration>): ApkConfiguration {
  return {
    id: crypto.randomUUID(),
    label: '',
    segment: 'LU',
    power_type: 'lighting',
    apk_count: 1,
    specto_a: { enabled: false, quantity: 0, voltage: '24V' },
    specto_b: { enabled: false, quantity: 0, voltage: null },
    radar: { enabled: false, directions: [{ lanes: 2 }] },
    hr_camera: { enabled: true, directions: [{ lanes: 2 }] },
    lvm: { enabled: true },
    ...partial,
  }
}

export function configToPayload(cfg: ApkConfiguration) {
  const { id: _, ...rest } = cfg
  return rest
}
