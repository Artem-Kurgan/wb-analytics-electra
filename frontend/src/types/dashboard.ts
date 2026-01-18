export interface KPIResponse {
  total_revenue: number
  revenue_change_percent: number
  total_orders: number
  orders_change_percent: number
  total_buyouts: number
  avg_buyout_rate: number
  avg_check: number
  low_stock_count: number
}

export interface ProductItem {
  nm_id: number
  vendor_code: string
  barcode: string
  title: string
  manager: string
  image_url: string
  orders: number
  orders_change_percent: number
  buyouts: number
  buyouts_change_percent: number
  buyout_rate: number
  revenue: number
  revenue_change_percent: number
  avg_check: number
  stock_wb: number
  stock_own: number
  total_stock: number
}

export interface ProductListResponse {
  items: ProductItem[]
  total: number
  page: number
  limit: number
}

export interface ChartDataResponse {
  data: Array<{ name: string; value: number }>
}
