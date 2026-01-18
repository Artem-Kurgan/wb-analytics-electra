import { Card, Statistic, Space } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons'

interface KPICardProps {
  title: string
  value: number | string
  changePercent?: number
  prefix?: string
  suffix?: string
  valueStyle?: React.CSSProperties
}

export default function KPICard({ title, value, changePercent, prefix, suffix, valueStyle }: KPICardProps) {
  const trendColor = changePercent && changePercent > 0 ? '#3f8600' : changePercent && changePercent < 0 ? '#cf1322' : '#999'
  const TrendIcon = changePercent && changePercent > 0 ? ArrowUpOutlined : ArrowDownOutlined

  return (
    <Card>
      <Statistic
        title={title}
        value={value}
        prefix={prefix}
        suffix={suffix}
        valueStyle={{ ...valueStyle, fontSize: 28, fontWeight: 600 }}
      />
      {changePercent !== undefined && (
        <Space style={{ marginTop: 8 }}>
          <TrendIcon style={{ color: trendColor, fontSize: 14 }} />
          <span style={{ color: trendColor, fontWeight: 500 }}>
            {changePercent > 0 ? '+' : ''}{changePercent.toFixed(1)}%
          </span>
          <span style={{ color: '#999', fontSize: 12 }}>vs пред. период</span>
        </Space>
      )}
    </Card>
  )
}
