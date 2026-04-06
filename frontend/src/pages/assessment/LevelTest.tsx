import React, { useEffect, useMemo, useState } from 'react'
import { Alert, Button, Card, Col, List, Radio, Row, Space, Statistic, Tag, Typography } from 'antd'
import type { RadioChangeEvent } from 'antd'
import { request } from '@/api'
import { getAuthSession } from '@/utils/auth'

const { Title, Paragraph, Text } = Typography

type RawOption = string | Record<string, any>

interface LevelTestQuestion {
  id: number
  question_type: string
  prompt: string
  level_tag?: string
  difficulty?: string
  options?: RawOption[]
}

interface LevelTestSubmitResult {
  record_id: number
  total_score: number
  result_level: string
  ability_summary: string
}

interface LevelTestRecordDetail {
  record: {
    id: number
    username: string
    total_score: number
    result_level: string
    ability_summary?: string | null
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
  }>
}

interface NormalizedOption {
  value: string
  label: string
}

const LevelTestPage: React.FC = () => {
  const username = getAuthSession()?.username
  const [questions, setQuestions] = useState<LevelTestQuestion[]>([])
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState<LevelTestSubmitResult | null>(null)
  const [detail, setDetail] = useState<LevelTestRecordDetail | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [error, setError] = useState('')

  const allAnswered = useMemo(
    () => questions.length > 0 && questions.every((q) => Boolean(answers[q.id])),
    [questions, answers],
  )

  const loadQuestions = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await request<{ data: { questions: LevelTestQuestion[] } }>({
        url: '/level-test/start',
        method: 'GET',
        params: { limit: 10, order: 'desc' },
      })
      setQuestions(res.data.questions || [])
      setAnswers({})
      setResult(null)
      setDetail(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载测试题失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadQuestions()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleAnswerChange = (questionId: number, evt: RadioChangeEvent) => {
    setAnswers((prev) => ({ ...prev, [questionId]: evt.target.value }))
  }

  const handleSubmit = async () => {
    if (!username) {
      setError('缺少登录信息，请重新登录后再试')
      return
    }
    if (!allAnswered) {
      setError('请先回答完全部题目')
      return
    }
    setSubmitting(true)
    setError('')
    try {
      const payloadAnswers = questions.map((question) => ({
        question_id: question.id,
        user_answer: answers[question.id],
      }))
      const res = await request<{ data: LevelTestSubmitResult }>({
        url: '/level-test/submit',
        method: 'POST',
        data: { username, answers: payloadAnswers },
      })
      setResult(res.data)
      setDetail(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : '提交失败，请稍后重试')
    } finally {
      setSubmitting(false)
    }
  }

  const fetchDetail = async () => {
    if (!result) return
    setDetailLoading(true)
    try {
      const res = await request<{ data: LevelTestRecordDetail }>({
        url: `/level-test/result/${result.record_id}`,
        method: 'GET',
      })
      setDetail(res.data)
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取答题详情失败')
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

      const text = pickText(raw.label, raw.text, raw.description, raw.explanation, raw.content)
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
        <Title level={2} style={{ marginBottom: 8 }}>商务英语水平测试</Title>
        <Paragraph type="secondary" style={{ marginBottom: 0 }}>
          题目与答案均来自 FC handler 的真实接口，提交后会写入 level_test_record / level_test_answer。
        </Paragraph>
      </div>

      {error ? <Alert type="error" message={error} /> : null}

      <Row gutter={16}>
        <Col xs={24} lg={16}>
          <Card
            title={`测试题目 (${questions.length})`}
            extra={<Button onClick={loadQuestions} loading={loading}>刷新题库</Button>}
          >
            <List
              loading={loading && questions.length === 0}
              dataSource={questions}
              locale={{ emptyText: '暂时没有可用的测试题' }}
              renderItem={(question, index) => {
                const options = normalizeOptions(question.options)
                return (
                  <List.Item key={question.id} style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                    <Space direction="vertical" size={8} style={{ width: '100%' }}>
                      <Space wrap>
                        <Text strong>{`第 ${index + 1} 题`}</Text>
                        {question.level_tag ? <Tag color="blue">{question.level_tag}</Tag> : null}
                        {question.difficulty ? <Tag>{question.difficulty}</Tag> : null}
                        <Tag color="purple">{question.question_type === 'single_choice' ? '单选题' : question.question_type}</Tag>
                      </Space>
                      <Paragraph style={{ marginBottom: 8 }}>{question.prompt}</Paragraph>
                      <Radio.Group
                        onChange={(evt) => handleAnswerChange(question.id, evt)}
                        value={answers[question.id]}
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
            <Card title="测试设置">
              <Space direction="vertical" size={4} style={{ width: '100%' }}>
                <Text>· 默认拉取 10 道题，可根据 level 筛选</Text>
                <Text>· 必须完成所有题才能提交</Text>
                <Text>· 提交结果会自动计算等级与建议</Text>
              </Space>
            </Card>

            <Card title="操作">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Button
                  type="primary"
                  block
                  disabled={!allAnswered}
                  loading={submitting}
                  onClick={handleSubmit}
                >
                  提交测试
                </Button>
                <Button onClick={loadQuestions} block disabled={loading}>
                  换一套题
                </Button>
              </Space>
            </Card>

            {result ? (
              <Card title="测试结果">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Statistic title="总分" value={result.total_score} suffix="分" />
                  <Tag color="geekblue">{result.result_level}</Tag>
                  <Paragraph style={{ whiteSpace: 'pre-line' }}>{result.ability_summary}</Paragraph>
                  <Space>
                    <Button onClick={fetchDetail} loading={detailLoading}>
                      查看答题详情
                    </Button>
                    <Button onClick={loadQuestions} disabled={loading}>
                      重新测试
                    </Button>
                  </Space>
                </Space>
              </Card>
            ) : null}
          </Space>
        </Col>
      </Row>

      {detail ? (
        <Card title="答题详情">
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
                  <Text>我的作答：{item.user_answer || '-'}</Text>
                  <Text type="secondary">正确答案：{item.correct_answer}</Text>
                </Space>
              </List.Item>
            )}
          />
        </Card>
      ) : null}
    </Space>
  )
}

export default LevelTestPage
