import { FC } from 'react'

import { Badge, Button, Card, Group, Text } from '@mantine/core'

import { Result } from '../types'

interface ResultCardProps extends Result {}

export const ResultCard: FC<ResultCardProps> = ({ title, url, preview }) => {
  return (
    <Card shadow="sm" padding="lg" withBorder component="li">
      <Text
        variant="gradient"
        gradient={{ from: 'violet', to: 'blue', deg: 146 }}
        component="a"
        href={url}
        target="_blank"
        size="xl"
        mb="xs"
        fw="bold"
      >
        {title}
      </Text>

      <Text
        size="sm"
        c="dimmed"
        dangerouslySetInnerHTML={{ __html: preview }}
      />
    </Card>
  )
}
