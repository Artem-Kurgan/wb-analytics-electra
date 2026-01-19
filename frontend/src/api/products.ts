import client from './client'

interface Size {
  techSize: string
  wbSize: string
  barcode: string
}

export interface Product {
  nm_id: number
  vendor_code: string
  barcode: string
  title: string
  image_url: string | null
  manager: string | null
  orders: number
  sales: number
  revenue: number
  stock_wb: number
  stock_own: number
  sizes?: Size[]
}

export interface ProductsParams {
  cabinet_id?: number
  manager?: string
  period?: string
}

export const productsAPI = {
  getProducts: async (params?: ProductsParams): Promise<Product[]> => {
    const response = await client.get('/v1/products/', { params })
    return response.data
  },
}
