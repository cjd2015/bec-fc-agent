import React, { useEffect, useState } from 'react'
import { Card, Col, Row, List, Tag, Typography, Space, Alert, Button } from 'antd'
import { request } from '@/api'

const { Title, Paragraph, Text } = Typography

interface VocabItem {
  id: number
  word: string
  phonetic?: string
  meaning_zh: string
  business_example?: string
  collocation?: string
  level: string
  difficulty: string
}

interface PatternItem {
  id: number
  pattern_text: string
  scene_type?: string
  function_type?: string
  example_text?: string
  slot_desc?: string
  level: string
  difficulty: string
}

const KnowledgeList: React.FC = () => {
  const [vocab, setVocab] = useState<VocabItem[]>([])
  const [patterns, setPatterns] = useState<PatternItem[]>([])
  const [error, setError] = useState<string>('')
  const [vocabLoading, setVocabLoading] = useState<boolean>(true)
  const [patternLoading, setPatternLoading] = useState<boolean>(true)
  const [vocabLoadingMore, setVocabLoadingMore] = useState<boolean>(false)
  const [patternLoadingMore, setPatternLoadingMore] = useState<boolean>(false)
  const [vocabHasMore, setVocabHasMore] = useState<boolean>(true)
  const [patternHasMore, setPatternHasMore] = useState<boolean>(true)
  const [vocabNextPage, setVocabNextPage] = useState<number>(1)
  const [patternNextPage, setPatternNextPage] = useState<number>(1)
  const vocabPageSize = 100
  const patternPageSize = 60

  const fetchVocab = async (reset: boolean = false) => {
    const page = reset ? 1 : vocabNextPage
    if (reset) {
      setVocabLoading(true)
      setError('')
    } else {
      setVocabLoadingMore(true)
    }
    try {
      const res = await request<{ data: { items: VocabItem[] } }>({
        url: '/vocab',
        method: 'GET',
        params: { page, page_size: vocabPageSize, order: 'desc', status: 'published' },
      })
      const items = res.data.items || []
      setVocabHasMore(items.length === vocabPageSize)
      if (reset) {
        setVocab(items)
        setVocabNextPage(2)
      } else {
        setVocab((prev) => [...prev, ...items])
        setVocabNextPage(page + 1)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载学习内容失败')
    } finally {
      if (reset) {
        setVocabLoading(false)
      } else {
        setVocabLoadingMore(false)
      }
    }
  }

  const fetchPatterns = async (reset: boolean = false) => {
    const page = reset ? 1 : patternNextPage
    if (reset) {
      setPatternLoading(true)
      setError('')
    } else {
      setPatternLoadingMore(true)
    }
    try {
      const res = await request<{ data: { items: PatternItem[] } }>({
        url: '/patterns',
        method: 'GET',
        params: { page, page_size: patternPageSize, order: 'desc', status: 'published' },
      })
      const items = res.data.items || []
      setPatternHasMore(items.length === patternPageSize)
      if (reset) {
        setPatterns(items)
        setPatternNextPage(2)
      } else {
        setPatterns((prev) => [...prev, ...items])
        setPatternNextPage(page + 1)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载学习内容失败')
    } finally {
      if (reset) {
        setPatternLoading(false)
      } else {
        setPatternLoadingMore(false)
      }
    }
  }

  useEffect(() => {
    fetchVocab(true)
    fetchPatterns(true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <div>
        <Title level={2} style={{ marginBottom: 8 }}>学习内容中心</Title>
        <Paragraph type="secondary" style={{ marginBottom: 0 }}>
          这里直接联到当前 FC handler 的词汇和句型接口，已经不是占位页了。
        </Paragraph>
      </div>

      {error ? <Alert type="error" message={error} /> : null}

      <Row gutter={16}>
        <Col xs={24} lg={12}>
          <Card
            title={`商务词汇（已加载 ${vocab.length} 条）`}
            loading={vocabLoading && vocab.length === 0}
            extra={
              vocabHasMore ? (
                <Button size="small" onClick={() => fetchVocab(false)} loading={vocabLoadingMore}>
                  加载更多
                </Button>
              ) : (
                <Text type="secondary">已加载全部</Text>
              )
            }
          >
            <List
              loading={vocabLoading && vocab.length === 0}
              dataSource={vocab}
              renderItem={(item) => (
                <List.Item>
                  <Space direction="vertical" size={4} style={{ width: '100%' }}>
                    <Space wrap>
                      <Text strong>{item.word}</Text>
                      {item.phonetic ? <Text type="secondary">{item.phonetic}</Text> : null}
                      <Tag color="blue">{item.level}</Tag>
                      <Tag>{item.difficulty}</Tag>
                    </Space>
                    <Text>{item.meaning_zh}</Text>
                    {item.collocation ? <Text type="secondary">搭配：{item.collocation}</Text> : null}
                    {item.business_example ? <Text type="secondary">例句：{item.business_example}</Text> : null}
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card
            title={`商务句型（已加载 ${patterns.length} 条）`}
            loading={patternLoading && patterns.length === 0}
            extra={
              patternHasMore ? (
                <Button size="small" onClick={() => fetchPatterns(false)} loading={patternLoadingMore}>
                  加载更多
                </Button>
              ) : (
                <Text type="secondary">已加载全部</Text>
              )
            }
          >
            <List
              loading={patternLoading && patterns.length === 0}
              dataSource={patterns}
              renderItem={(item) => (
                <List.Item>
                  <Space direction="vertical" size={4} style={{ width: '100%' }}>
                    <Space wrap>
                      <Text strong>{item.pattern_text}</Text>
                      <Tag color="purple">{item.level}</Tag>
                      <Tag>{item.difficulty}</Tag>
                      {item.scene_type ? <Tag color="geekblue">{item.scene_type}</Tag> : null}
                      {item.function_type ? <Tag color="gold">{item.function_type}</Tag> : null}
                    </Space>
                    {item.slot_desc ? <Text>{item.slot_desc}</Text> : null}
                    {item.example_text ? <Text type="secondary">示例：{item.example_text}</Text> : null}
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </Space>
  )
}

export default KnowledgeList
