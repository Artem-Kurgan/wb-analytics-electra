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
