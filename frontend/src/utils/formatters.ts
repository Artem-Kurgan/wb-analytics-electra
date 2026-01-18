export const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0
  }).format(value)
}

export const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('ru-RU').format(value)
}

export const formatPercent = (value: number): string => {
  return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`
}
