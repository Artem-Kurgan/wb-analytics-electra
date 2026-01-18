import { Card, Form, Input, Button } from 'antd'

export default function Settings() {
  return (
    <Card title="Настройки" style={{ maxWidth: 600 }}>
      <Form layout="vertical">
        <Form.Item label="WB API Token">
          <Input type="password" placeholder="Введи токен WB" />
        </Form.Item>
        <Form.Item label="Расписание синков">
          <Input placeholder="Каждые N часов" />
        </Form.Item>
        <Button type="primary">Сохранить</Button>
      </Form>
    </Card>
  )
}
