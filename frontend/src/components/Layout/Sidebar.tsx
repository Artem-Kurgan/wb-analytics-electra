import { Layout, Menu } from 'antd'
import { DashboardOutlined, ShoppingOutlined, BarChartOutlined, SettingOutlined } from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'

const { Sider } = Layout

export default function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()

  const items = [
    { key: '/dashboard', icon: <DashboardOutlined />, label: 'Дашборд' },
    { key: '/products', icon: <ShoppingOutlined />, label: 'Аналитика' },
    { key: '/reports', icon: <BarChartOutlined />, label: 'Отчёты' },
    { key: '/settings', icon: <SettingOutlined />, label: 'Настройки' }
  ]

  return (
    <Sider width={200} style={{ background: '#001529' }}>
      <div style={{ padding: '20px', color: '#fff', fontSize: 16, fontWeight: 'bold', textAlign: 'center' }}>
        ⚡ Electra
      </div>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        items={items}
        onClick={(e) => navigate(e.key)}
        style={{ background: '#001529' }}
      />
    </Sider>
  )
}
