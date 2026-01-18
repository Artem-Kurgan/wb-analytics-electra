import client from './client'
import { KPIResponse, ProductListResponse, ChartDataResponse } from '../types/dashboard'

export const dashboardAPI = {
  getKPI: async (period: string, cabinetId?: number): Promise<KPIResponse> => {
    const params: any = { period }
    if (cabinetId) params.cabinet_id = cabinetId

    const response = await client.get<KPIResponse>('/v1/dashboard/kpi', { params })
    return response.data
  },

  getProducts: async (params: {
    period: string
    cabinet_id?: number
    sort_by?: string
    order?: string
    page?: number
    limit?: number
  }): Promise<ProductListResponse> => {
    const response = await client.get<ProductListResponse>('/v1/dashboard/products', { params })
    return response.data
  },

  getSalesByCabinet: async (period: string): Promise<ChartDataResponse> => {
    const response = await client.get<ChartDataResponse>('/v1/dashboard/charts/sales-by-cabinet', {
      params: { period }
    })
    return response.data
  },

  syncCabinet: async (cabinetId: number): Promise<{ task_id: string }> => {
    const response = await client.post(`/v1/dashboard/sync/${cabinetId}`)
    return response.data
  }
// TODO: Dashboard API endpoints
export const dashboardApi = {
  // getStats, etc.
}
