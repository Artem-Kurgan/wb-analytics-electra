import { Layout, Button, Dropdown, Avatar, Space, Typography } from 'antd'
import { UserOutlined, LogoutOutlined, SettingOutlined } from '@ant-design/icons'
import { useAuthStore } from '../../store/authStore'
import { useNavigate } from 'react-router-dom'
import type { MenuProps } from 'antd'

const { Header: AntHeader } = Layout
const { Text } = Typography

export default function Header() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const items: MenuProps['items'] = [
    {
      key: 'settings',
      label: 'Настройки',
      icon: <SettingOutlined />,
      onClick: () => navigate('/settings')
    },
    {
      type: 'divider'
    },
    {
      key: 'logout',
      label: 'Выйти',
      icon: <LogoutOutlined />,
      danger: true,
      onClick: handleLogout
    }
  ]

  return (
    <AntHeader style={{
      background: '#fff',
      padding: '0 24px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      borderBottom: '1px solid #f0f0f0'
    }}>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Text strong style={{ fontSize: 18 }}>⚡ Electra Analytics</Text>
      </div>

      <Dropdown menu={{ items }} placement="bottomRight">
        <Space style={{ cursor: 'pointer' }}>
          <Avatar icon={<UserOutlined />} />
          <div>
            <div style={{ fontWeight: 500 }}>{user?.name}</div>
            <div style={{ fontSize: 12, color: '#999' }}>
              {user?.role === 'admin' ? 'Администратор' : user?.role === 'leader' ? 'Руководитель' : 'Менеджер'}
            </div>
          </div>
        </Space>
      </Dropdown>
import { Layout, Typography } from 'antd'

const { Header: AntHeader } = Layout
const { Title } = Typography

export default function Header() {
  return (
    <AntHeader style={{ background: '#fff', padding: '0 20px', display: 'flex', alignItems: 'center' }}>
      <Title level={4} style={{ margin: 0 }}>Electra Analytics</Title>
    </AntHeader>
  )
}
