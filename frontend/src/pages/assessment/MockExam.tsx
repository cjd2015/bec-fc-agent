import React, { useEffect, useMemo, useState } from 'react'
import { Alert, Button, Card, Col, List, Radio, Row, Space, Statistic, Tag, Typography } from 'antd'
import type { RadioChangeEvent } from 'antd'
import { request } from '@/api'
import { getAuthSession } from '@/utils/auth'

const { Title, Paragraph, Text } = Typography

type RawOption = string | Record<string, any>

interface MockExamQuestion {
  id: number
  stem: string
  question_type: string
  level?: string
  difficulty?: string
  options?: RawOption[]
}

interface MockExamResult {
  record_id: number
  total_score: number
  accuracy_rate: number
  weak_tags?: string | null
}

interface MockExamDetail {
  record: {
    id: number
    username: string
    total_score: number
    accuracy_rate: number
    weak_tags?: string | null
    status: string
    started_at?: string
    ended_at?: string | null
  }
  answers: Array<{
    question_id: number
    stem: string
    user_answer: string
    correct_answer: string
    is_correct: boolean
    score: number
    explanation_result?: string | null
  }>
}

interface NormalizedOption {
  value: string
  label: string
}

const SAMPLE_SIZE = 5

const pickRandomQuestions = (items: MockExamQuestion[], size: number = SAMPLE_SIZE): MockExamQuestion[] => {
  if (!Array.isArray(items) || items.length === 0) return []
  if (items.length <= size) return [...items]
  const pool = [...items]
  const selected: MockExamQuestion[] = []
  while (selected.length < size && pool.length > 0) {
    const idx = Math.floor(Math.random() * pool.length)
    selected.push(pool.splice(idx, 1)[0])
  }
  return selected
}

const MockExamPage: React.FC = () => {
  const username = getAuthSession()?.username
  const [questions, setQuestions] = useState<MockExamQuestion[]>([])
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState<MockExamResult | null>(null)
  const [detail, setDetail] = useState<MockExamDetail | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [error, setError] = useState('')

  const answeredCount = useMemo(() => Object.values(answers).filter(Boolean).length, [answers])
  const canSubmit = useMemo(
    () => questions.length > 0 && questions.every((q) => Boolean(answers[q.id])),
    [questions, answers],
  )

  const loadQuestions = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await request<{ data: { items: MockExamQuestion[] } }>({
        url: '/mock-exams',
        method: 'GET',
        params: { limit: 100, order: 'desc' },
      })
      const items = res.data.items || []
      const randomized = pickRandomQuestions(items, SAMPLE_SIZE)
      setQuestions(randomized)
      setAnswers({})
      setResult(null)
      setDetail(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载模拟考试题失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadQuestions()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleAnswer = (questionId: number, evt: RadioChangeEvent) => {
    setAnswers((prev) => ({ ...prev, [questionId]: evt.target.value }))
  }

  const handleSubmit = async () => {
    if (!username) {
      setError('缺少登录信息，请重新登录后再试')
      return
    }
    if (!questions.length) {
      setError('当前没有可用的模拟考试题')
      return
    }
    if (!canSubmit) {
      setError('请先完成全部题目再提交')
      return
    }
    const examId = questions[0]?.id
    if (!examId) {
      setError('未找到有效的模拟考试 ID')
      return
    }
    setSubmitting(true)
    setError('')
    try {
      const payloadAnswers = questions.map((question) => ({
        question_id: question.id,
        user_answer: answers[question.id],
      }))
      const res = await request<{ data: MockExamResult }>({
        url: `/mock-exams/${examId}/submit`,
        method: 'POST',
        data: { username, answers: payloadAnswers },
      })
      setResult(res.data)
      setDetail(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : '提交模拟考试失败')
    } finally {
      setSubmitting(false)
    }
  }

  const fetchDetail = async () => {
    if (!result) return
    setDetailLoading(true)
    try {
      const res = await request<{ data: MockExamDetail }>({
        url: `/mock-exams/result/${result.record_id}`,
        method: 'GET',
      })
      setDetail(res.data)
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取模拟考试详情失败')
    } finally {
      setDetailLoading(false)
    }
  }

  const normalizeOptions = (optionList?: RawOption[]): NormalizedOption[] => {
    if (!Array.isArray(optionList)) return []
    return optionList.map((raw, index) => {
      if (typeof raw === 'string') {
        return { value: raw, label: raw }
      }
      const pickText = (...candidates: Array<unknown>) =>
        candidates
          .map((item) => (typeof item === 'string' ? item.trim() : ''))
          .find((item) => item.length > 0)

      const text = pickText(raw.label, raw.text, raw.description, raw.content)
        || pickText(raw.value, raw.key, raw.id)
        || `选项 ${index + 1}`
      const prefix = pickText(raw.value, raw.key, raw.id)
      const label = prefix && !text.startsWith(prefix) ? `${prefix}. ${text}` : text
      return { value: text, label }
    })
  }

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <div>
        <Title level={2} style={{ marginBottom: 8 }}>模拟考试</Title>
        <Paragraph type="secondary" style={{ marginBottom: 0 }}>
          该页面直接请求 FC handler 的 /mock-exams 与 /mock-exams/
          {'{'}id{'}'}/submit，实现题目展示与答题流程。
        </Paragraph>
      </div>

      {error ? <Alert type="error" message={error} /> : null}

      <Row gutter={16}>
        <Col xs={24} lg={16}>
          <Card
            title={`模拟考试题 (${questions.length})`}
            extra={<Button onClick={loadQuestions} loading={loading}>重新抽题</Button>}
          >
            <List
              loading={loading && questions.length === 0}
              dataSource={questions}
              locale={{ emptyText: '暂时没有模拟考试题' }}
              renderItem={(question, index) => {
                const options = normalizeOptions(question.options)
                return (
                  <List.Item key={question.id} style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                    <Space direction="vertical" size={8} style={{ width: '100%' }}>
                      <Space wrap>
                        <Text strong>{`第 ${index + 1} 题`}</Text>
                        {question.level ? <Tag color="blue">{question.level}</Tag> : null}
                        {question.difficulty ? <Tag>{question.difficulty}</Tag> : null}
                        <Tag color="purple">{question.question_type === 'single_choice' ? '单选题' : question.question_type}</Tag>
                      </Space>
                      <Paragraph style={{ marginBottom: 8 }}>{question.stem}</Paragraph>
                      <Radio.Group
                        value={answers[question.id]}
                        onChange={(evt) => handleAnswer(question.id, evt)}
                        style={{ width: '100%' }}
                      >
                        <Space direction="vertical" style={{ width: '100%' }}>
                          {options.map((option) => (
                            <Radio key={`${question.id}-${option.value}`} value={option.value}>
                              {option.label}
                            </Radio>
                          ))}
                        </Space>
                      </Radio.Group>
                    </Space>
                  </List.Item>
                )
              }}
            />
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <Card title="考试说明">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>· 默认抽取 5 道题，提交后计分</Text>
                <Text>· 需要完成全部题目才能提交</Text>
                <Text>· 结果会记录得分、正确率与薄弱标签</Text>
                <Text type="secondary">· 当前版本将第一题作为考试 ID，用于 FC handler 记录</Text>
              </Space>
            </Card>

            <Card title="进度">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>已作答：{answeredCount}/{questions.length}</Text>
                <Button
                  type="primary"
                  block
                  disabled={!canSubmit}
                  onClick={handleSubmit}
                  loading={submitting}
                >
                  提交模拟考试
                </Button>
                <Button block onClick={loadQuestions} disabled={loading}>
                  换一套试题
                </Button>
              </Space>
            </Card>

            {result ? (
              <Card title="考试结果">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Statistic title="总分" value={result.total_score} suffix="分" />
                  <Statistic title="正确率" value={result.accuracy_rate} suffix="%" precision={2} />
                  <Paragraph>薄弱项：{result.weak_tags || '暂无'}</Paragraph>
                  <Space>
                    <Button onClick={fetchDetail} loading={detailLoading}>
                      查看试卷详情
                    </Button>
                    <Button onClick={loadQuestions} disabled={loading}>
                      重新练习
                    </Button>
                  </Space>
                </Space>
              </Card>
            ) : null}
          </Space>
        </Col>
      </Row>

      {detail ? (
        <Card title="模拟考试答题详情">
          <List
            dataSource={detail.answers}
            renderItem={(item, index) => (
              <List.Item key={item.question_id} style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                <Space direction="vertical" size={4} style={{ width: '100%' }}>
                  <Space wrap>
                    <Text strong>{`第 ${index + 1} 题`}</Text>
                    <Tag color={item.is_correct ? 'green' : 'red'}>
                      {item.is_correct ? '回答正确' : '回答错误'}
                    </Tag>
                    <Tag>{item.score} 分</Tag>
                  </Space>
                  <Paragraph style={{ marginBottom: 4 }}>{item.stem}</Paragraph>
                  <Text>我的答案：{item.user_answer || '-'}</Text>
                  <Text type="secondary">正确答案：{item.correct_answer}</Text>
                  {item.explanation_result ? (
                    <Text type="secondary">系统结论：{item.explanation_result}</Text>
                  ) : null}
                </Space>
              </List.Item>
            )}
          />
        </Card>
      ) : null}
    </Space>
  )
}

export default MockExamPage
