import { useState } from 'react'

import {
  Center,
  Container,
  Group,
  Loader,
  MantineProvider,
  Select,
  Stack,
  Text,
  TextInput
} from '@mantine/core'
import { Button } from '@mantine/core'
import { createTheme } from '@mantine/core'
import '@mantine/core/styles.css'
import { IconSearch } from '@tabler/icons-react'

import './App.css'
import { ResultCard } from './components/ResultCard'
import { Result } from './types'

const theme = createTheme({
  primaryColor: 'violet',
  defaultRadius: 'lg'
})

type Level = 'Бакалавриат' | 'Магистратура' | 'Специалитет'

interface Params {
  query: string
  level: Level | null
  code: string
  name: string
  field: string
}

const studyLevels: Level[] = ['Бакалавриат', 'Магистратура', 'Специалитет']

function App() {
  const [results, setResults] = useState<Result[]>()

  const [value, setValue] = useState<Params>({
    query: '',
    level: null,
    code: '',
    name: '',
    field: ''
  })

  const [isLoading, setIsLoading] = useState(false)

  const search = async ({ query, level, code, field, name }: Params) => {
    let url = `${import.meta.env.VITE_API_URL}/search?search_str=${query}`

    if (level) url += `&level=${level}`
    if (code) url += `&code=${code}`
    if (field) url += `&code=${field}`
    if (name) url += `&code=${name}`

    setIsLoading(true)

    await new Promise((resolve) => setTimeout(resolve, 1000))

    fetch(url)
      .then((response) => response.json())
      .then((json) => {
        console.log(json)
        setResults(json)
      })
      .finally(() => setIsLoading(false))
  }

  return (
    <MantineProvider theme={theme}>
      <Container py="xl">
        <Stack
          component="form"
          onSubmit={(e) => {
            e.preventDefault()
            search(value)
          }}
        >
          <Group wrap="nowrap">
            <TextInput
              size="lg"
              placeholder="Введите текст для поиска по файлам образовательных программ СПбГУ"
              style={{ width: '100%' }}
              value={value.query}
              onChange={(event) =>
                setValue((value) => ({
                  ...value,
                  query: event.currentTarget.value
                }))
              }
            />
            <Button variant="filled" type="submit" size="lg">
              <IconSearch />
            </Button>
          </Group>

          <Group>
            <Select
              size="md"
              data={studyLevels}
              placeholder="Уровень"
              allowDeselect
              value={value.level}
              onChange={(newValue) =>
                setValue((value) => ({
                  ...value,
                  level: newValue as Level | null
                }))
              }
            />
            <TextInput
              size="md"
              placeholder="Код специальности"
              value={value.code}
              onChange={(event) =>
                setValue((value) => ({
                  ...value,
                  code: event.currentTarget.value
                }))
              }
            />
            <TextInput
              size="md"
              placeholder="Специальность"
              value={value.name}
              onChange={(event) =>
                setValue((value) => ({
                  ...value,
                  name: event.currentTarget.value
                }))
              }
            />
            <TextInput
              size="md"
              placeholder="Направление"
              value={value.field}
              onChange={(event) =>
                setValue((value) => ({
                  ...value,
                  field: event.currentTarget.value
                }))
              }
            />
          </Group>
        </Stack>

        {isLoading && (
          <Center mt="xl">
            <Loader />
          </Center>
        )}

        {!isLoading && results?.length === 0 && (
          <Center mt="xl">
            <Text size="md" c="dimmed">
              По вашему запросу ничего не нашлось
            </Text>
          </Center>
        )}

        {results && (
          <Stack component="ul" style={{ padding: 0 }}>
            {results?.map((result) => <ResultCard {...result} />)}
          </Stack>
        )}
      </Container>
    </MantineProvider>
  )
}

export default App
