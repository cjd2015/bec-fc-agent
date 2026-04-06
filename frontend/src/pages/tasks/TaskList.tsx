import React, { useEffect, useState } from 'react'
import { Alert, Card, Col, List, Progress, Row, Space, Statistic, Tag, Typography } from 'antd'
import { request } from '@/api'
import { getAuthSession } from '@/utils/auth'

const { Title, Paragraph, Text } = Typography

interface SummaryData {
  username: string
  vocab_progress: {
    total: number
    learned: number
    review: number
    avg_correct_rate: number
  }
  pattern_progress: {
    total: number
    learned: number
    review: number
    avg_familiarity_score: number
  }
  scene_progress: {
    total_sessions: number
    finished_sessions: number
    avg_scene_score: number
  }
  latest_level_test: {
    total_score: number | null
    result_level: string | null
    ended_at: string | null
  }
  latest_mock_exam: {
    total_score: number | null
    accuracy_rate: number | null
    weak_tags: string | null
    ended_at: string | null
  }
}

const TaskList: React.FC = () => {
  const [summary, setSummary] = useState<SummaryData | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const username = getAuthSession()?.username

  useEffect(() => {
    if (!username) return
    const load = async () => {
      setLoading(true)
      setError('')
      try {
        const res = await request<{ data: SummaryData }>({
          url: `/learning/summary?username=${username}`,
          method: 'GET',
        })
        setSummary(res.data)
      } catch (err) {
        setError(err instanceof Error ? err.message : '加载学习看板失败')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [username])

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <div>
        <Title level={2} style={{ marginBottom: 8 }}>学习进度看板</Title>
        <Paragraph type="secondary" style={{ marginBottom: 0 }}>
          这里已经接到真实学习汇总接口，可直接作为前端联调入口页。
        </Paragraph>
      </div>

      {!username ? <Alert type="warning" message="请登录后查看学习数据" /> : null}
      {error ? <Alert type="error" message={error} /> : null}

      {loading ? (
        <Row gutter={16}>
          <Col xs={24} md={8}>
            <Card loading style={{ minHeight: 120 }} />
          </Col>
          <Col xs={24} md={8}>
            <Card loading style={{ minHeight: 120 }} />
          </Col>
          <Col xs={24} md={8}>
            <Card loading style={{ minHeight: 120 }} />
          </Col>
        </Row>
      ) : summary ? (
        <>
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Card><Statistic title="词汇平均正确率" value={summary.vocab_progress.avg_correct_rate} suffix="%" /></Card>
            </Col>
            <Col xs={24} md={8}>
              <Card><Statistic title="句型熟悉度" value={summary.pattern_progress.avg_familiarity_score} suffix="分" /></Card>
            </Col>
            <Col xs={24} md={8}>
              <Card><Statistic title="场景训练平均分" value={summary.scene_progress.avg_scene_score} suffix="分" /></Card>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} lg={12}>
              <Card title="词汇学习进度">
                <Progress percent={summary.vocab_progress.avg_correct_rate} />
                <List
                  dataSource={[
                    `累计记录：${summary.vocab_progress.total}`,
                    `已学会：${summary.vocab_progress.learned}`,
                    `待复习：${summary.vocab_progress.review}`,
                  ]}
                  renderItem={(item) => <List.Item>{item}</List.Item>}
                />
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title="句型学习进度">
                <Progress percent={summary.pattern_progress.avg_familiarity_score} status="active" />
                <List
                  dataSource={[
                    `累计记录：${summary.pattern_progress.total}`,
                    `已学会：${summary.pattern_progress.learned}`,
                    `待复习：${summary.pattern_progress.review}`,
                  ]}
                  renderItem={(item) => <List.Item>{item}</List.Item>}
                />
              </Card>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} lg={12}>
              <Card title="最近一次水平测试">
                <Space direction="vertical">
                  <Text>分数：{summary.latest_level_test.total_score ?? '-'}</Text>
                  <Tag color="blue">{summary.latest_level_test.result_level || '暂无结果'}</Tag>
                  <Text type="secondary">完成时间：{summary.latest_level_test.ended_at || '-'}</Text>
                </Space>
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title="最近一次模拟考试">
                <Space direction="vertical">
                  <Text>总分：{summary.latest_mock_exam.total_score ?? '-'}</Text>
                  <Text>正确率：{summary.latest_mock_exam.accuracy_rate ?? '-'}%</Text>
                  <Tag color="volcano">弱项：{summary.latest_mock_exam.weak_tags || '暂无'}</Tag>
                  <Text type="secondary">完成时间：{summary.latest_mock_exam.ended_at || '-'}</Text>
                </Space>
              </Card>
            </Col>
          </Row>
        </>
      ) : null}
    </Space>
  )
}

export default TaskList
