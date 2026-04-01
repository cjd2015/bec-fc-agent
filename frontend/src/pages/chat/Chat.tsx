import React, { useEffect, useState } from 'react'
import { Alert, Button, Card, Col, Input, List, Row, Space, Tag, Typography } from 'antd'
import { request } from '@/api'

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
  const username = 'fc_user_1775006297'

  useEffect(() => {
    const loadScenes = async () => {
      try {
        const res = await request<{ data: { items: SceneItem[] } }>({ url: '/scenes', method: 'GET' })
        setScenes(res.data.items || [])
      } catch (err) {
        setError(err instanceof Error ? err.message : '加载场景失败')
      }
    }
    loadScenes()
  }, [])

  const startScene = async (scene: SceneItem) => {
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

      {error ? <Alert type="error" message={error} /> : null}
      {result ? <Alert type="success" message={result} /> : null}

      <Row gutter={16}>
        <Col xs={24} lg={10}>
          <Card title={`训练场景 (${scenes.length})`}>
            <List
              dataSource={scenes}
              renderItem={(item) => (
                <List.Item
                  actions={[
                    <Button type="primary" onClick={() => startScene(item)} key={`start-${item.id}`}>
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
