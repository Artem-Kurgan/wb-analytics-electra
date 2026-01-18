import { Layout, Menu } from 'antd'
import { Link } from 'react-router-dom'
import { DashboardOutlined, SettingOutlined } from '@ant-design/icons'

const { Sider } = Layout

export default function Sidebar() {
  return (
    <Sider width={200} style={{ background: '#fff' }}>
      <Menu
        mode="inline"
        defaultSelectedKeys={['1']}
        style={{ height: '100%', borderRight: 0 }}
        items={[
          {
            key: '1',
            icon: <DashboardOutlined />,
            label: <Link to="/dashboard">Dashboard</Link>,
          },
          {
            key: '2',
            icon: <SettingOutlined />,
            label: <Link to="/settings">Settings</Link>,
          },
        ]}
      />
    </Sider>
  )
}
