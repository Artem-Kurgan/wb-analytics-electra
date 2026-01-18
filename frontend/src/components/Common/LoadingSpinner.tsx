import { Spin } from 'antd'

export default function LoadingSpinner() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', width: '100%' }}>
      <Spin size="large" />
    </div>
  )
}
