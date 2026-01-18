import { Table, Image, Tag, Button, Space, Typography, Tooltip, message } from 'antd'
import { LinkOutlined, CopyOutlined } from '@ant-design/icons'
import { ProductItem } from '../../types/dashboard'
import { formatCurrency, formatNumber, formatPercent } from '../../utils/formatters'
import type { ColumnsType } from 'antd/es/table'

const { Text, Link } = Typography

interface ProductsTableProps {
  products: ProductItem[]
  loading: boolean
  pagination: {
    current: number
    pageSize: number
    total: number
    onChange: (page: number, pageSize: number) => void
  }
}

export default function ProductsTable({ products, loading, pagination }: ProductsTableProps) {
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    message.success('Скопировано')
  }

  const getBuyoutRateColor = (rate: number) => {
    if (rate >= 70) return 'success'
    if (rate >= 50) return 'warning'
    return 'error'
  }

  const renderTrend = (value: number, changePercent: number) => {
    const color = changePercent > 0 ? '#3f8600' : changePercent < 0 ? '#cf1322' : '#999'
    return (
      <Space direction="vertical" size={0}>
        <Text strong>{formatNumber(value)}</Text>
        <Text style={{ color, fontSize: 12 }}>
          {formatPercent(changePercent)}
        </Text>
      </Space>
    )
  }

  const columns: ColumnsType<ProductItem> = [
    {
      title: 'Фото',
      dataIndex: 'image_url',
      key: 'image',
      width: 80,
      render: (url: string) => (
        <Image
          src={url}
          alt="Product"
          width={60}
          height={60}
          style={{ objectFit: 'cover', borderRadius: 4 }}
          fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mN8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        />
      )
    },
    {
      title: 'Артикул WB',
      dataIndex: 'nm_id',
      key: 'nm_id',
      width: 120,
      render: (nmId: number) => (
        <Link
          href={`https://www.wildberries.ru/catalog/${nmId}/detail.aspx`}
          target="_blank"
        >
          {nmId} <LinkOutlined />
        </Link>
      )
    },
    {
      title: 'Артикул продавца',
      dataIndex: 'vendor_code',
      key: 'vendor_code',
      width: 150
    },
    {
      title: 'Баркод',
      dataIndex: 'barcode',
      key: 'barcode',
      width: 140,
      render: (barcode: string) => (
        <Space>
          <Text copyable={{ text: barcode, tooltips: ['Копировать', 'Скопировано'] }}>
            {barcode}
          </Text>
        </Space>
      )
    },
    {
      title: 'Менеджер',
      dataIndex: 'manager',
      key: 'manager',
      width: 120,
      render: (manager: string) => manager ? <Tag color="blue">{manager}</Tag> : '-'
    },
    {
      title: 'Заказы',
      dataIndex: 'orders',
      key: 'orders',
      width: 120,
      sorter: true,
      render: (orders: number, record: ProductItem) => renderTrend(orders, record.orders_change_percent)
    },
    {
      title: 'Выкупы',
      dataIndex: 'buyouts',
      key: 'buyouts',
      width: 120,
      sorter: true,
      render: (buyouts: number, record: ProductItem) => renderTrend(buyouts, record.buyouts_change_percent)
    },
    {
      title: '% Выкупа',
      dataIndex: 'buyout_rate',
      key: 'buyout_rate',
      width: 100,
      sorter: true,
      render: (rate: number) => (
        <Tag color={getBuyoutRateColor(rate)}>
          {rate.toFixed(1)}%
        </Tag>
      )
    },
    {
      title: 'Выручка',
      dataIndex: 'revenue',
      key: 'revenue',
      width: 150,
      sorter: true,
      render: (revenue: number, record: ProductItem) => (
        <Space direction="vertical" size={0}>
          <Text strong>{formatCurrency(revenue)}</Text>
          <Text style={{ color: record.revenue_change_percent > 0 ? '#3f8600' : '#cf1322', fontSize: 12 }}>
            {formatPercent(record.revenue_change_percent)}
          </Text>
        </Space>
      )
    },
    {
      title: 'Средний чек',
      dataIndex: 'avg_check',
      key: 'avg_check',
      width: 120,
      render: (check: number) => formatCurrency(check)
    },
    {
      title: 'Остаток WB',
      dataIndex: 'stock_wb',
      key: 'stock_wb',
      width: 100,
      sorter: true
    },
    {
      title: 'Остаток Склад',
      dataIndex: 'stock_own',
      key: 'stock_own',
      width: 120,
      sorter: true
    },
    {
      title: 'Всего остаток',
      dataIndex: 'total_stock',
      key: 'total_stock',
      width: 120,
      sorter: true,
      render: (total: number) => (
        <Text strong style={{ color: total < 10 ? '#cf1322' : '#000' }}>
          {total}
          {total < 10 && ' (Мало)'}
        </Text>
      )
    }
  ]

  return (
    <Table
      columns={columns}
      dataSource={products}
      rowKey="nm_id"
      loading={loading}
      pagination={pagination}
    />
  )
}
