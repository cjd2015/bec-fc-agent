import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Table,
  Button,
  Tag,
  Space,
  Input,
  Select,
  Card,
  Avatar,
  Modal,
  message,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { PlusOutlined, UserOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { useAgents, useDeleteAgent } from '@/hooks/useAgent'
import type { Agent } from '@/types/agent'
import dayjs from 'dayjs'

const { Search } = Input
const { Option } = Select

const AgentList: React.FC = () => {
  const navigate = useNavigate()
  const [statusFilter, setStatusFilter] = useState<string>()
  const { data: agents = [], isLoading, refetch } = useAgents({ status: statusFilter })
  const deleteMutation = useDeleteAgent()

  const getStatusText = (status: Agent['status']): string => {
    const map = {
      draft: '草稿',
      active: '激活',
      inactive: '停用',
      archived: '归档',
    }
    return map[status] || status
  }

  const columns: ColumnsType<Agent> = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 80,
    },
    {
      title: '名称',
      dataIndex: 'name',
      render: (_, record) => (
        <Space>
          <Avatar src={record.icon} icon={!record.icon && <UserOutlined />} />
          <span>{record.name}</span>
          <Tag color={record.status === 'active' ? 'green' : 'default'}>
            {getStatusText(record.status)}
          </Tag>
        </Space>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      ellipsis: true,
      width: 250,
    },
    {
      title: '模型',
      render: (_, record) => `${record.provider} / ${record.model}`,
      width: 180,
    },
    {
      title: '版本',
      dataIndex: 'version',
      align: 'center',
      width: 80,
    },
    {
      title: '对话数',
      dataIndex: 'total_conversations',
      align: 'center',
      width: 100,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      render: (date) => dayjs(date).format('YYYY-MM-DD HH:mm'),
      width: 160,
    },
    {
      title: '操作',
      key: 'action',
      width: 280,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button type="link" onClick={() => navigate(`/agents/${record.id}`)}>
            详情
          </Button>
          <Button type="link" icon={<EditOutlined />} onClick={() => navigate(`/agents/${record.id}/edit`)}>
            编辑
          </Button>
          <Button type="link" onClick={() => navigate(`/agents/${record.id}/versions`)}>
            版本
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  const handleDelete = (record: Agent) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除 Agent "${record.name}" 吗？删除后可以恢复。`,
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteMutation.mutateAsync(record.id)
          message.success('删除成功')
          refetch()
        } catch {
          message.error('删除失败')
        }
      },
    })
  }

  return (
    <div className="agent-list">
      <div className="page-header">
        <h2>BEC Agent 管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/agents/create')}>
          创建 Agent
        </Button>
      </div>

      <Card className="filter-card" style={{ marginBottom: 16 }}>
        <Space>
          <Select
            placeholder="状态筛选"
            style={{ width: 150 }}
            onChange={setStatusFilter}
            allowClear
          >
            <Option value="draft">草稿</Option>
            <Option value="active">激活</Option>
            <Option value="inactive">停用</Option>
            <Option value="archived">归档</Option>
          </Select>
          <Search placeholder="搜索 Agent" onSearch={refetch} style={{ width: 300 }} />
        </Space>
      </Card>

      <Table
        columns={columns}
        dataSource={agents}
        loading={isLoading}
        rowKey="id"
        onRow={(record) => ({
          onClick: () => navigate(`/agents/${record.id}`),
        })}
        scroll={{ x: 1200 }}
      />
    </div>
  )
}

export default AgentList
