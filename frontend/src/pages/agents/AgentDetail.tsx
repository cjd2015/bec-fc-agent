import React from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Descriptions,
  Card,
  Button,
  Tag,
  Space,
  Divider,
  Input,
  Statistic,
  Row,
  Col,
  Timeline,
} from 'antd'
import { ArrowLeftOutlined, EditOutlined, DeleteOutlined, FileTextOutlined, ChatOutlined } from '@ant-design/icons'
import { useAgent, useDeleteAgent } from '@/hooks/useAgent'
import dayjs from 'dayjs'

const { TextArea } = Input

const AgentDetail: React.FC = () => {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const { data: agent, isLoading } = useAgent(id ? parseInt(id) : undefined)
  const deleteMutation = useDeleteAgent()

  const getStatusText = (status?: string): string => {
    if (!status) return '未知'
    const map: Record<string, string> = {
      draft: '草稿',
      active: '激活',
      inactive: '停用',
      archived: '归档',
    }
    return map[status] || status
  }

  const getStatusColor = (status?: string): string => {
    const map: Record<string, string> = {
      draft: 'default',
      active: 'success',
      inactive: 'warning',
      archived: 'default',
    }
    return map[status || ''] || 'default'
  }

  const handleDelete = () => {
    if (!agent) return
    deleteMutation.mutate(agent.id)
    navigate('/agents')
  }

  if (isLoading) {
    return <div>加载中...</div>
  }

  if (!agent) {
    return <div>Agent 不存在</div>
  }

  return (
    <div className="agent-detail">
      <div className="page-header">
        <h2>
          <ArrowLeftOutlined
            style={{ cursor: 'pointer', marginRight: 16 }}
            onClick={() => navigate(-1)}
          />
          {agent.name}
        </h2>
        <Space>
          <Button onClick={() => navigate(-1)}>返回</Button>
          <Button type="primary" icon={<EditOutlined />} onClick={() => navigate(`/agents/${agent.id}/edit`)}>
            编辑
          </Button>
        </Space>
      </div>

      <Row gutter={20}>
        <Col span={16}>
          <Card
            title="基本信息"
            extra={<Tag color={getStatusColor(agent.status)}>{getStatusText(agent.status)}</Tag>}
            style={{ marginBottom: 16 }}
          >
            <Descriptions column={2} bordered>
              <Descriptions.Item label="ID">{agent.id}</Descriptions.Item>
              <Descriptions.Item label="版本">v{agent.version}</Descriptions.Item>
              <Descriptions.Item label="名称" span={2}>{agent.name}</Descriptions.Item>
              <Descriptions.Item label="描述" span={2}>
                {agent.description || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Provider">{agent.provider}</Descriptions.Item>
              <Descriptions.Item label="模型">{agent.model}</Descriptions.Item>
              <Descriptions.Item label="变体">{agent.model_variant}</Descriptions.Item>
              <Descriptions.Item label="温度">{agent.temperature}</Descriptions.Item>
              <Descriptions.Item label="最大 Tokens">{agent.max_tokens}</Descriptions.Item>
              <Descriptions.Item label="对话数">{agent.total_conversations}</Descriptions.Item>
              <Descriptions.Item label="消息数">{agent.total_messages}</Descriptions.Item>
              <Descriptions.Item label="平均评分">{agent.avg_rating?.toFixed(1) || '0.0'}</Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {dayjs(agent.created_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
              <Descriptions.Item label="更新时间">
                {dayjs(agent.updated_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
            </Descriptions>

            {agent.system_prompt && (
              <>
                <Divider>系统提示词</Divider>
                <TextArea value={agent.system_prompt} rows={6} readOnly />
              </>
            )}
          </Card>

          <Card title="最近操作">
            <Timeline>
              <Timeline.Item color="blue" dot={<FileTextOutlined />}>
                Agent 创建
                <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
                  {dayjs(agent.created_at).format('YYYY-MM-DD HH:mm:ss')}
                </div>
              </Timeline.Item>
            </Timeline>
          </Card>
        </Col>

        <Col span={8}>
          <Card title="统计信息" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic title="会话数" value={agent.total_conversations} />
              </Col>
              <Col span={12}>
                <Statistic title="消息数" value={agent.total_messages} />
              </Col>
              <Col span={12}>
                <Statistic title="版本" value={agent.version} />
              </Col>
              <Col span={12}>
                <Statistic title="评分" value={agent.avg_rating?.toFixed(1) || '0.0'} precision={1} />
              </Col>
            </Row>
          </Card>

          <Card title="快捷操作">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button
                type="primary"
                icon={<FileTextOutlined />}
                style={{ width: '100%' }}
                onClick={() => navigate(`/agents/${agent.id}/versions`)}
              >
                版本历史
              </Button>
              <Button icon={<ChatOutlined />} style={{ width: '100%' }}>
                对话测试
              </Button>
              <Button
                danger
                icon={<DeleteOutlined />}
                style={{ width: '100%' }}
                onClick={handleDelete}
              >
                删除 Agent
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default AgentDetail
