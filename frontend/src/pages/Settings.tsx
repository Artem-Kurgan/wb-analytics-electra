import { useState } from 'react'
import { Card, Tabs, Table, Button, Form, Input, Select, Modal, Space, Checkbox, Tag, Popconfirm, message } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SyncOutlined } from '@ant-design/icons'
import type { TabsProps, TableColumnsType } from 'antd'

interface Cabinet {
  id: number
  name: string
  api_token: string
  is_active: boolean
  last_sync?: string
  sync_status?: 'success' | 'failed' | 'pending'
}

interface User {
  id: number
  name: string
  email: string
  role: 'admin' | 'leader' | 'manager'
  allowed_tags?: string
  created_at: string
}

export default function Settings() {
  const [cabinets, setCabinets] = useState<Cabinet[]>([
    { id: 1, name: 'ИП Иванов И.И.', api_token: 'eyJ...', is_active: true, last_sync: '2026-01-19 08:15', sync_status: 'success' },
    { id: 2, name: 'ИП Петров П.П.', api_token: 'abc...', is_active: true, last_sync: '2026-01-19 07:45', sync_status: 'success' }
  ])

  const [users, setUsers] = useState<User[]>([
    { id: 1, name: 'Администратор', email: 'admin@electra.com', role: 'admin', created_at: '2026-01-18' },
    { id: 2, name: 'Юля', email: 'julia@electra.com', role: 'leader', created_at: '2026-01-19' },
    { id: 3, name: 'Саша', email: 'sasha@electra.com', role: 'manager', allowed_tags: 'склад,логистика', created_at: '2026-01-19' }
  ])

  const [cabinetModalVisible, setCabinetModalVisible] = useState(false)
  const [userModalVisible, setUserModalVisible] = useState(false)
  const [editingCabinet, setEditingCabinet] = useState<Cabinet | null>(null)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [form] = Form.useForm()

  // === КАБИНЕТЫ ===
  const cabinetColumns: TableColumnsType<Cabinet> = [
    { title: 'Название ИП', dataIndex: 'name', key: 'name' },
    {
      title: 'API Токен',
      dataIndex: 'api_token',
      key: 'api_token',
      render: (token: string) => `${token}` 
    },
    {
      title: 'Статус синхронизации',
      key: 'status',
      render: (_, record) => (
        <Space direction="vertical" size={0}>
          <Tag color={record.sync_status === 'success' ? 'green' : record.sync_status === 'failed' ? 'red' : 'orange'}>
            {record.sync_status === 'success' && '✓ Успешно'}
            {record.sync_status === 'failed' && '✗ Ошибка'}
            {record.sync_status === 'pending' && '⟳ В процессе'}
          </Tag>
          <small>{record.last_sync}</small>
        </Space>
      )
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_, record) => (
        <Space size="small">
          <Button type="primary" size="small" icon={<SyncOutlined />} onClick={() => handleSync(record.id)}>
            Синхро
          </Button>
          <Button size="small" icon={<EditOutlined />} onClick={() => editCabinet(record)}>
            Редакт
          </Button>
          <Popconfirm title="Удалить?" onConfirm={() => deleteCabinet(record.id)}>
            <Button danger size="small" icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )
    }
  ]

  const userColumns: TableColumnsType<User> = [
    { title: 'Имя', dataIndex: 'name', key: 'name' },
    { title: 'Email', dataIndex: 'email', key: 'email' },
    {
      title: 'Роль',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => <Tag color={role === 'admin' ? 'red' : role === 'leader' ? 'blue' : 'orange'}>{role.toUpperCase()}</Tag>
    },
    {
      title: 'Теги',
      dataIndex: 'allowed_tags',
      key: 'allowed_tags',
      render: (tags: string) => tags ? tags.split(',').map(t => <Tag key={t}>{t.trim()}</Tag>) : '-'
    },
    { title: 'Дата создания', dataIndex: 'created_at', key: 'created_at' },
    {
      title: 'Действия',
      key: 'actions',
      render: (_, record) => (
        <Space size="small">
          <Button size="small" icon={<EditOutlined />} onClick={() => editUser(record)} />
          <Popconfirm title="Удалить?" onConfirm={() => deleteUser(record.id)}>
            <Button danger size="small" icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )
    }
  ]

  const handleSync = (id: number) => {
    message.success(`Кабинет ${id} синхронизирован`)
  }

  const editCabinet = (cabinet: Cabinet) => {
    setEditingCabinet(cabinet)
    form.setFieldsValue({ name: cabinet.name, api_token: cabinet.api_token })
    setCabinetModalVisible(true)
  }

  const deleteCabinet = (id: number) => {
    setCabinets(cabinets.filter(c => c.id !== id))
    message.success('Удалено')
  }

  const saveCabinet = async (values: any) => {
    if (editingCabinet) {
      setCabinets(cabinets.map(c => c.id === editingCabinet.id ? { ...c, ...values } : c))
    } else {
      setCabinets([...cabinets, { id: Date.now(), ...values, is_active: true, sync_status: 'pending' as const }])
    }
    form.resetFields()
    setCabinetModalVisible(false)
    setEditingCabinet(null)
  }

  const editUser = (user: User) => {
    setEditingUser(user)
    form.setFieldsValue({ name: user.name, email: user.email, role: user.role, allowed_tags: user.allowed_tags })
    setUserModalVisible(true)
  }

  const deleteUser = (id: number) => {
    setUsers(users.filter(u => u.id !== id))
    message.success('Удалено')
  }

  const saveUser = async (values: any) => {
    if (editingUser) {
      setUsers(users.map(u => u.id === editingUser.id ? { ...u, ...values } : u))
    } else {
      setUsers([...users, { id: Date.now(), ...values, created_at: new Date().toLocaleDateString() }])
    }
    form.resetFields()
    setUserModalVisible(false)
    setEditingUser(null)
  }

  const tabItems: TabsProps['items'] = [
    {
      key: 'cabinets',
      label: 'Кабинеты',
      children: (
        <>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingCabinet(null); form.resetFields(); setCabinetModalVisible(true) }} style={{ marginBottom: 16 }}>
            Добавить кабинет
          </Button>
          <Table columns={cabinetColumns} dataSource={cabinets} rowKey="id" pagination={false} size="small" />
        </>
      )
    },
    {
      key: 'users',
      label: 'Пользователи',
      children: (
        <>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingUser(null); form.resetFields(); setUserModalVisible(true) }} style={{ marginBottom: 16 }}>
            Добавить пользователя
          </Button>
          <Table columns={userColumns} dataSource={users} rowKey="id" pagination={false} size="small" />
        </>
      )
    }
  ]

  return (
    <Card title="Настройки">
      <Tabs items={tabItems} />

      <Modal title={editingCabinet ? 'Редактировать кабинет' : 'Добавить кабинет'} open={cabinetModalVisible} onOk={() => form.submit()} onCancel={() => setCabinetModalVisible(false)}>
        <Form form={form} layout="vertical" onFinish={saveCabinet}>
          <Form.Item name="name" label="Название ИП" rules={[{ required: true }]}>
            <Input placeholder="ИП Иванов И.И." />
          </Form.Item>
          <Form.Item name="api_token" label="API Токен" rules={[{ required: true }]}>
            <Input.Password placeholder="Введи WB API токен" />
          </Form.Item>
          <Button type="primary" block onClick={() => message.success('Токен проверен ✓')}>
            Проверить токен
          </Button>
        </Form>
      </Modal>

      <Modal title={editingUser ? 'Редактировать пользователя' : 'Добавить пользователя'} open={userModalVisible} onOk={() => form.submit()} onCancel={() => setUserModalVisible(false)}>
        <Form form={form} layout="vertical" onFinish={saveUser}>
          <Form.Item name="name" label="Имя" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}>
            <Input />
          </Form.Item>
          {!editingUser && (
            <Form.Item name="password" label="Пароль" rules={[{ required: true }]}>
              <Input.Password />
            </Form.Item>
          )}
          <Form.Item name="role" label="Роль" rules={[{ required: true }]}>
            <Select options={[{ label: 'Администратор', value: 'admin' }, { label: 'Руководитель', value: 'leader' }, { label: 'Менеджер', value: 'manager' }]} />
          </Form.Item>
          <Form.Item noStyle shouldUpdate={(prevValues, currentValues) => prevValues.role !== currentValues.role}>
            {({ getFieldValue }) => getFieldValue('role') === 'manager' ? (
              <Form.Item name="allowed_tags" label="Теги менеджера">
                <Input placeholder="склад, логистика" />
              </Form.Item>
            ) : null}
          </Form.Item>
          <Form.Item name="send_invite" valuePropName="checked">
            <Checkbox>Отправить приглашение</Checkbox>
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
