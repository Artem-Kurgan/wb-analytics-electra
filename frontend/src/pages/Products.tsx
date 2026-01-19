import { useState, useEffect } from 'react'
import { Table, Card, Space, Button, Input, Select, Tag, Image, Statistic, Row, Col, Tooltip } from 'antd'
import { CopyOutlined, BarcodeOutlined, DownloadOutlined } from '@ant-design/icons'
import type { TableColumnsType } from 'antd'
import { productsAPI, type Product as APIProduct } from '../api/products'
import PeriodSelector from '../components/Dashboard/PeriodSelector'

interface Product {
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
  sizes?: any[]
}

export default function Products() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [searchText, setSearchText] = useState('')
  const [period, setPeriod] = useState('week')

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true)
      try {
        const data = await productsAPI.getProducts({ period })
        setProducts(data)
      } catch (error) {
        console.error('Failed to fetch products:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchProducts()
  }, [period])

  const calculateBuyoutPercent = (sales: number, orders: number) => {
    if (orders === 0) return 0
    return ((sales / orders) * 100).toFixed(1)
  }

  const calculateAverageCheck = (revenue: number, sales: number) => {
    if (sales === 0) return 0
    return (revenue / sales).toFixed(0)
  }

  const handleCopyBarcode = (barcode: string) => {
    navigator.clipboard.writeText(barcode)
    alert(`Скопировано: ${barcode}`)
  }

  const columns: TableColumnsType<Product> = [
    {
      title: 'Фото',
      dataIndex: 'image_url',
      width: 80,
      render: (image_url) => (
        image_url ? (
          <Image src={image_url} width={60} height={60} />
        ) : (
          <div style={{ width: 60, height: 60, background: '#f0f0f0', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 10 }}>
            Нет фото
          </div>
        )
      )
    },
    {
      title: 'Артикул WB',
      dataIndex: 'nm_id',
      width: 120,
      sorter: (a, b) => a.nm_id - b.nm_id,
      render: (nm_id) => <a href={`https://www.wildberries.ru/catalog/${nm_id}`} target="_blank" rel="noreferrer">{nm_id}</a>
    },
    {
      title: 'Артикул продавца',
      dataIndex: 'vendor_code',
      width: 130,
      sorter: (a, b) => a.vendor_code.localeCompare(b.vendor_code)
    },
    {
      title: 'Баркод',
      dataIndex: 'barcode',
      width: 150,
      render: (barcode, record) => (
        <Space size="small">
          <span style={{ fontFamily: 'monospace', fontSize: 12 }}>{barcode}</span>
          {record.sizes && record.sizes.length > 1 && (
            <Tooltip title={`Размеры: ${record.sizes.map((s: any) => s.techSize).join(', ')}`}>
              <Tag>+{record.sizes.length - 1}</Tag>
            </Tooltip>
          )}
          <Button type="text" size="small" icon={<CopyOutlined />} onClick={() => handleCopyBarcode(barcode)} />
        </Space>
      )
    },
    {
      title: 'Менеджер',
      dataIndex: 'manager',
      width: 100,
      render: (manager) => manager ? <Tag color="blue">{manager}</Tag> : '-'
    },
    {
      title: 'Заказы',
      dataIndex: 'orders',
      width: 90,
      sorter: (a, b) => b.orders - a.orders,
      defaultSortOrder: 'descend',
      render: (orders) => <span style={{ fontWeight: 'bold', color: '#1890ff' }}>{orders}</span>
    },
    {
      title: 'Выкупы',
      dataIndex: 'sales',
      width: 90,
      sorter: (a, b) => b.sales - a.sales,
      render: (sales) => <span style={{ fontWeight: 'bold', color: '#52c41a' }}>{sales}</span>
    },
    {
      title: '% Выкупа',
      width: 90,
      render: (_, record) => {
        const percent = calculateBuyoutPercent(record.sales, record.orders)
        const color = percent > 70 ? '#52c41a' : percent > 50 ? '#faad14' : '#ff4d4f'
        return <span style={{ color, fontWeight: 'bold' }}>{percent}%</span>
      },
      sorter: (a, b) => {
        const aPercent = parseFloat(calculateBuyoutPercent(a.sales, a.orders))
        const bPercent = parseFloat(calculateBuyoutPercent(b.sales, b.orders))
        return bPercent - aPercent
      }
    },
    {
      title: 'Выручка, ₽',
      dataIndex: 'revenue',
      width: 130,
      sorter: (a, b) => b.revenue - a.revenue,
      render: (revenue) => <span style={{ fontWeight: 'bold', color: '#1890ff' }}>₽{revenue}</span>
    },
    {
      title: 'Средний чек, ₽',
      width: 120,
      render: (_, record) => {
        const avgCheck = calculateAverageCheck(record.revenue, record.sales)
        return <span>₽{avgCheck}</span>
      }
    },
    {
      title: 'Остаток WB',
      dataIndex: 'stock_wb',
      width: 110,
      sorter: (a, b) => a.stock_wb - b.stock_wb,
      render: (stock) => (
        <span style={{ color: stock < 10 ? '#ff4d4f' : '#52c41a', fontWeight: 'bold', background: stock < 10 ? '#fff1f0' : 'transparent', padding: '4px 8px', borderRadius: 4 }}>
          {stock}
        </span>
      )
    },
    {
      title: 'Остаток склад',
      dataIndex: 'stock_own',
      width: 120,
      sorter: (a, b) => a.stock_own - b.stock_own,
      render: (stock) => (
        <span style={{ color: stock < 10 ? '#ff4d4f' : '#52c41a', fontWeight: 'bold' }}>
          {stock}
        </span>
      )
    },
    {
      title: 'Всего остаток',
      width: 130,
      render: (_, record) => {
        const total = record.stock_wb + record.stock_own
        return (
          <span style={{ color: total < 10 ? '#ff4d4f' : '#52c41a', fontWeight: 'bold', background: total < 10 ? '#fff1f0' : 'transparent', padding: '4px 8px', borderRadius: 4 }}>
            {total}
          </span>
        )
      },
      sorter: (a, b) => (a.stock_wb + a.stock_own) - (b.stock_wb + b.stock_own)
    }
  ]

  const filteredProducts = products.filter(p =>
    p.title.toLowerCase().includes(searchText.toLowerCase()) ||
    p.vendor_code.toLowerCase().includes(searchText.toLowerCase()) ||
    p.barcode.toLowerCase().includes(searchText.toLowerCase()) ||
    p.nm_id.toString().includes(searchText)
  )

  return (
    <div>
      <div style={{ marginBottom: 20, display: 'flex', justifyContent: 'flex-end' }}>
        <PeriodSelector value={period} onChange={setPeriod} />
      </div>

      <Card style={{ marginBottom: 20 }}>
        <Row gutter={16}>
          <Col xs={24} sm={12} md={6}>
            <Statistic title="Товаров" value={products.length} />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Statistic title="Сумма выручки" value={products.reduce((sum, p) => sum + p.revenue, 0)} prefix="₽" />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Statistic title="Всего заказов" value={products.reduce((sum, p) => sum + p.orders, 0)} />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Statistic title="Всего выкупов" value={products.reduce((sum, p) => sum + p.sales, 0)} />
          </Col>
        </Row>
      </Card>

      <Card title="Аналитика">
        <Space style={{ marginBottom: 16, display: 'flex', gap: 10 }}>
          <Input
            placeholder="Поиск по названию, артикулу, баркоду..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ maxWidth: 400 }}
          />
          <Button icon={<DownloadOutlined />}>Экспорт баркодов</Button>
        </Space>

        <Table<Product>
          columns={columns}
          dataSource={filteredProducts}
          loading={loading}
          rowKey="nm_id"
          pagination={{ pageSize: 20, showSizeChanger: true, showTotal: (total) => `Всего: ${total}` }}
          scroll={{ x: 1400 }}
          size="small"
        />
      </Card>
    </div>
  )
}
