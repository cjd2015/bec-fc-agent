import React, { useEffect, useState } from 'react'
import { Alert, Button, Card, Col, Input, List, Row, Space, Tag, Typography } from 'antd'
import { request } from '@/api'
import { getAuthSession } from '@/utils/auth'

const { Title, Paragraph, Text } = Typography

interface SceneItem {
  id: number
  scene_name: string
  scene_background: string
  training_goal: string
  user_role: string
  ai_role: string
  level: string
  difficulty: string
}

interface SessionState {
  sessionId: number
  sceneId: number
  openingMessage: string
}

const Chat: React.FC = () => {
  const [scenes, setScenes] = useState<SceneItem[]>([])
  const [selectedScene, setSelectedScene] = useState<SceneItem | null>(null)
  const [session, setSession] = useState<SessionState | null>(null)
  const [message, setMessage] = useState('')
  const [conversation, setConversation] = useState<string[]>([])
  const [result, setResult] = useState<string>('')
  const [error, setError] = useState('')
  const [loadingScenes, setLoadingScenes] = useState<boolean>(true)
  const [loadingMoreScenes, setLoadingMoreScenes] = useState<boolean>(false)
  const [hasMoreScenes, setHasMoreScenes] = useState<boolean>(true)
  const [nextPage, setNextPage] = useState<number>(1)
  const pageSize = 6
  const username = getAuthSession()?.username

  const fetchScenes = async (reset: boolean = false) => {
    const pageToLoad = reset ? 1 : nextPage
    if (reset) {
      setLoadingScenes(true)
      setError('')
    } else {
      setLoadingMoreScenes(true)
    }
    try {
      const res = await request<{ data: { items: SceneItem[] } }>({
        url: '/scenes',
        method: 'GET',
        params: { page: pageToLoad, limit: pageSize, order: 'desc' },
      })
      const items = res.data.items || []
      setHasMoreScenes(items.length === pageSize)
      if (reset) {
        setScenes(items)
        setNextPage(2)
      } else {
        setScenes((prev) => [...prev, ...items])
        setNextPage(pageToLoad + 1)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载场景失败')
    } finally {
      if (reset) {
        setLoadingScenes(false)
      } else {
        setLoadingMoreScenes(false)
      }
    }
  }

  useEffect(() => {
    fetchScenes(true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const startScene = async (scene: SceneItem) => {
    if (!username) {
      setError('请先登录后再开始训练')
      return
    }
    setError('')
    setResult('')
    try {
      const res = await request<{ data: { session_id: number; opening_message: string } }>({
        url: `/scenes/${scene.id}/start`,
        method: 'POST',
        data: { username },
      })
      setSelectedScene(scene)
      setSession({
        sessionId: res.data.session_id,
        sceneId: scene.id,
        openingMessage: res.data.opening_message,
      })
      setConversation([`AI: ${res.data.opening_message}`])
    } catch (err) {
      setError(err instanceof Error ? err.message : '启动场景失败')
    }
  }

  const sendMessage = async () => {
    if (!session || !message.trim()) return
    setError('')
    try {
      const userMessage = message.trim()
      const res = await request<{ data: { reply: string; feedback: string } }>({
        url: `/scenes/${session.sceneId}/message`,
        method: 'POST',
        data: { session_id: session.sessionId, message: userMessage },
      })
      setConversation((prev) => [
        ...prev,
        `我: ${userMessage}`,
        `AI: ${res.data.reply}`,
        `反馈: ${res.data.feedback}`,
      ])
      setMessage('')
    } catch (err) {
      setError(err instanceof Error ? err.message : '发送消息失败')
    }
  }

  const finishScene = async () => {
    if (!session) return
    setError('')
    try {
      const res = await request<{ data: { summary: string; feedback_summary: string; score: number } }>({
        url: `/scenes/${session.sceneId}/finish`,
        method: 'POST',
        data: { session_id: session.sessionId },
      })
      setResult(`得分 ${res.data.score}｜${res.data.summary}｜${res.data.feedback_summary}`)
      setSession(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : '结束场景失败')
    }
  }

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <div>
        <Title level={2} style={{ marginBottom: 8 }}>场景对话训练</Title>
        <Paragraph type="secondary" style={{ marginBottom: 0 }}>
          已接入 FC 场景接口：列表、start、message、finish 全链路可用。
        </Paragraph>
      </div>

      {!username ? <Alert type="warning" message="请先登录以启动真实场景对话" /> : null}
      {error ? <Alert type="error" message={error} /> : null}
      {result ? <Alert type="success" message={result} /> : null}

      <Row gutter={16}>
        <Col xs={24} lg={10}>
          <Card
            title={`训练场景 (${scenes.length})`}
            extra={
              hasMoreScenes ? (
                <Button size="small" onClick={() => fetchScenes(false)} loading={loadingMoreScenes}>
                  加载更多
                </Button>
              ) : (
                <Text type="secondary">没有更多场景</Text>
              )
            }
          >
            <List
              loading={loadingScenes}
              dataSource={scenes}
              renderItem={(item) => (
                <List.Item
                  style={{ background: selectedScene?.id === item.id ? '#f0f5ff' : undefined }}
                  actions={[
                    <Button
                      type="primary"
                      onClick={() => startScene(item)}
                      key={`start-${item.id}`}
                      disabled={!username || loadingScenes}
                    >
                      开始训练
                    </Button>,
                  ]}
                >
                  <Space direction="vertical" size={4} style={{ width: '100%' }}>
                    <Text strong>{item.scene_name}</Text>
                    <Text>{item.training_goal}</Text>
                    <Space wrap>
                      <Tag color="blue">{item.level}</Tag>
                      <Tag>{item.difficulty}</Tag>
                      <Tag color="purple">{item.user_role}</Tag>
                      <Tag color="geekblue">{item.ai_role}</Tag>
                    </Space>
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        </Col>

        <Col xs={24} lg={14}>
          <Card title={selectedScene ? `当前场景：${selectedScene.scene_name}` : '训练区'}>
            {!selectedScene ? (
              <Text type="secondary">先从左侧选择一个场景开始训练。</Text>
            ) : (
              <Space direction="vertical" size={16} style={{ width: '100%' }}>
                <div>
                  <Text strong>背景：</Text>
                  <Paragraph>{selectedScene.scene_background}</Paragraph>
                  <Text strong>目标：</Text>
                  <Paragraph>{selectedScene.training_goal}</Paragraph>
                </div>

                <List
                  bordered
                  dataSource={conversation}
                  renderItem={(item) => <List.Item>{item}</List.Item>}
                  locale={{ emptyText: '还没有对话内容' }}
                />

                <Space.Compact style={{ width: '100%' }}>
                  <Input
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="输入你的商务英语表达..."
                    disabled={!session}
                  />
                  <Button type="primary" onClick={sendMessage} disabled={!session || !message.trim()}>
                    发送
                  </Button>
                  <Button onClick={finishScene} disabled={!session}>
                    结束训练
                  </Button>
                </Space.Compact>
              </Space>
            )}
          </Card>
        </Col>
      </Row>
    </Space>
  )
}

export default Chat
