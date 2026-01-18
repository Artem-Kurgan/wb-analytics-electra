import { Card, Tabs } from 'antd'

export default function Reports() {
  return (
    <Card title="Отчёты">
      <Tabs items={[
        { key: 'returns', label: 'Возвраты', children: <p>TODO: Данные по возвратам</p> },
        { key: 'storage', label: 'Хранение', children: <p>TODO: Платное хранение</p> },
        { key: 'regions', label: 'Регионы', children: <p>TODO: Продажи по регионам</p> }
      ]} />
    </Card>
  )
}
