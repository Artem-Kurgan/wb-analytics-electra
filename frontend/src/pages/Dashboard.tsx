import { Row, Col, Card, Statistic } from 'antd'
import { ShoppingCartOutlined, DollarOutlined, RiseOutlined, UserOutlined } from '@ant-design/icons'

export default function Dashboard() {
  return (
    <div>
      <h1>Дашборд</h1>
      <Row gutter={16} style={{ marginBottom: 20 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Заказы"
              value={1234}
              prefix={<ShoppingCartOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Выручка"
              value={125450}
              prefix={<DollarOutlined />}
              suffix="₽"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Рост"
              value={25.8}
              suffix="%"
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Товары"
              value={48}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Последние продажи" style={{ marginBottom: 20 }}>
        <p>TODO: Таблица с последними продажами</p>
      </Card>

      <Card title="Статистика по дням">
        <p>TODO: График продаж</p>
      </Card>
    </div>
  )
}
