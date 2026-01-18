import { Card, Typography } from 'antd'

const { Title } = Typography

export default function Login() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f0f2f5' }}>
      <Card style={{ width: 400, textAlign: 'center' }}>
        <Title level={2}>⚡ Electra Analytics</Title>
        <Title level={4}>Wildberries Dashboard</Title>
        <p>TODO: Login form</p>
      </Card>
    </div>
  )
}
