import React, { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Card,
  Timeline,
  Tag,
  Button,
  Descriptions,
  Divider,
  Input,
  Modal,
  message,
  Empty,
  Col,
  Row,
} from 'antd'
import { ArrowLeftOutlined, CheckOutlined, WarningOutlined } from '@ant-design/icons'
import { useAgentVersions, useRollback } from '@/hooks/useAgent'
import type { AgentVersion } from '@/types/agent'
import dayjs from 'dayjs'

const { TextArea } = Input

const AgentVersions: React.FC = () => {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const agentId = id ? parseInt(id) : 0

  const { data: versions = [], isLoading } = useAgentVersions(agentId)
  const rollbackMutation = useRollback(agentId)

  const [selectedVersion, setSelectedVersion] = useState<AgentVersion | null>(null)
  const [rollbackVisible, setRollbackVisible] = useState(false)
  const [targetVersion, setTargetVersion] = useState<AgentVersion | null>(null)

  const currentVersion = versions.length > 0 ? versions[0].version : 1

  const handleRollback = (version: AgentVersion) => {
    setTargetVersion(version)
    setRollbackVisible(true)
  }

  const confirmRollback = async () => {
    if (!targetVersion) return

    try {
      await rollbackMutation.mutateAsync(targetVersion.id)
      message.success(`已成功回滚到版本 v${targetVersion.version}`)
      setRollbackVisible(false)
      navigate(`/agents/${id}`)
    } catch {
      message.error('回滚失败')
    }
  }

  if (isLoading) {
    return <div>加载中...</div>
  }

  return (
    <div className="agent-versions">
      <div className="page-header">
        <h2>
          <ArrowLeftOutlined
            style={{ cursor: 'pointer', marginRight: 16 }}
            onClick={() => navigate(-1)}
          />
          版本历史
        </h2>
        <Button onClick={() => navigate(-1)}>返回</Button>
      </div>

      <Row gutter={20}>
        <Col span={16}>
          <Card title={`版本列表 (当前版本：v${currentVersion})`}>
            {versions.length === 0 ? (
              <Empty description="暂无版本记录" />
            ) : (
              <Timeline>
                {versions.map((version) => (
                  <Timeline.Item
                    key={version.id}
                    timestamp={dayjs(version.created_at).format('YYYY-MM-DD HH:mm:ss')}
                    color={version.version === currentVersion ? 'blue' : 'gray'}
                    dot={
                      version.version === currentVersion ? (
                        <CheckOutlined style={{ fontSize: 16 }} />
                      ) : undefined
                    }
                  >
                    <Card size="small">
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          marginBottom: 12,
                        }}
                      >
                        <h4 style={{ margin: 0 }}>
                          <Tag color={version.version === currentVersion ? 'blue' : 'default'}>
                            v{version.version}
                          </Tag>
                          {version.version === currentVersion && (
                            <span style={{ marginLeft: 8, color: '#1890ff' }}>
                              <CheckOutlined /> 当前版本
                            </span>
                          )}
                        </h4>
                        <div>
                          <Button type="link" onClick={() => setSelectedVersion(version)}>
                            预览
                          </Button>
                          <Button
                            type="link"
                            danger
                            disabled={version.version === currentVersion}
                            onClick={() => handleRollback(version)}
                          >
                            回滚到此版本
                          </Button>
                        </div>
                      </div>

                      {version.change_summary && (
                        <p style={{ margin: '4px 0', color: '#666' }}>
                          <strong>变更摘要：</strong>{version.change_summary}
                        </p>
                      )}
                      {version.operator_name && (
                        <p style={{ margin: '4px 0', color: '#666' }}>
                          <strong>操作者：</strong>{version.operator_name}
                        </p>
                      )}
                    </Card>
                  </Timeline.Item>
                ))}
              </Timeline>
            )}
          </Card>
        </Col>

        <Col span={8}>
          <Card
            title={selectedVersion ? `版本预览 - v${selectedVersion.version}` : '版本预览'}
            style={{ position: 'sticky', top: 24 }}
          >
            {selectedVersion ? (
              <>
                <Descriptions column={1} bordered size="small">
                  <Descriptions.Item label="版本">v{selectedVersion.version}</Descriptions.Item>
                  <Descriptions.Item label="创建时间">
                    {dayjs(selectedVersion.created_at).format('YYYY-MM-DD HH:mm:ss')}
                  </Descriptions.Item>
                  <Descriptions.Item label="变更摘要">
                    {selectedVersion.change_summary || '-'}
                  </Descriptions.Item>
                </Descriptions>

                <Divider>配置详情</Divider>

                <Descriptions column={1} bordered size="small">
                  <Descriptions.Item label="名称">{selectedVersion.snapshot?.name}</Descriptions.Item>
                  <Descriptions.Item label="Provider">{selectedVersion.snapshot?.provider}</Descriptions.Item>
                  <Descriptions.Item label="模型">{selectedVersion.snapshot?.model}</Descriptions.Item>
                  <Descriptions.Item label="变体">{selectedVersion.snapshot?.model_variant}</Descriptions.Item>
                  <Descriptions.Item label="温度">{selectedVersion.snapshot?.temperature}</Descriptions.Item>
                  <Descriptions.Item label="最大 Tokens">{selectedVersion.snapshot?.max_tokens}</Descriptions.Item>
                </Descriptions>

                {selectedVersion.snapshot?.system_prompt && (
                  <>
                    <Divider>系统提示词</Divider>
                    <TextArea value={selectedVersion.snapshot.system_prompt} rows={6} readOnly />
                  </>
                )}

                <Button
                  type="primary"
                  danger
                  style={{ width: '100%', marginTop: 16 }}
                  disabled={selectedVersion.version === currentVersion}
                  onClick={() => handleRollback(selectedVersion)}
                >
                  回滚到此版本
                </Button>
              </>
            ) : (
              <Empty description="点击版本预览配置详情" />
            )}
          </Card>
        </Col>
      </Row>

      <Modal
        title="确认回滚"
        open={rollbackVisible}
        onOk={confirmRollback}
        onCancel={() => setRollbackVisible(false)}
        okText="确认回滚"
        cancelText="取消"
        okButtonProps={{ danger: true, loading: rollbackMutation.isPending }}
      >
        <p>确定要回滚到 <strong>v{targetVersion?.version}</strong> 吗？</p>
        <p style={{ color: '#ff4d4f', fontSize: 14 }}>
          <WarningOutlined /> 回滚前会自动创建当前版本的备份，您可以随时恢复到回滚前的状态。
        </p>
        {targetVersion?.change_summary && (
          <p>
            <strong>该版本的变更：</strong>{targetVersion.change_summary}
          </p>
        )}
      </Modal>
    </div>
  )
}

export default AgentVersions
