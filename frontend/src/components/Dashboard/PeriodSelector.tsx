import { Segmented } from 'antd'

interface PeriodSelectorProps {
  value: string
  onChange: (value: string) => void
}

export default function PeriodSelector({ value, onChange }: PeriodSelectorProps) {
  const options = [
    { label: 'Сегодня', value: 'day' },
    { label: 'Неделя', value: 'week' },
    { label: 'Месяц', value: 'month' },
    { label: '3 месяца', value: '3months' }
  ]

  return (
    <Segmented
      options={options}
      value={value}
      onChange={(val) => onChange(val as string)}
      size="large"
    />
  )
}
