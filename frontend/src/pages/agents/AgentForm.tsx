import React, { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Form,
  Input,
  Select,
  Slider,
  InputNumber,
  Button,
  Card,
  Divider,
  message,
} from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { useAgent, useCreateAgent, useUpdateAgent } from '@/hooks/useAgent'
import type { AgentCreateRequest } from '@/types/agent'

const { TextArea } = Input
const { Option } = Select

const AgentForm: React.FC = () => {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const isEdit = !!id

  const [form] = Form.useForm()
  const { data: agent, isLoading } = useAgent(id ? parseInt(id) : undefined)
  const createMutation = useCreateAgent()
  const updateMutation = useUpdateAgent(id ? parseInt(id) : 0)

  useEffect(() => {
    if (agent && isEdit) {
      form.setFieldsValue(agent)
    }
  }, [agent, isEdit, form])

  const handleSubmit = async (values: AgentCreateRequest) => {
    try {
      if (isEdit) {
        await updateMutation.mutateAsync({
          ...values,
          create_version: true,
          change_summary: '更新配置',
        })
        message.success('更新成功')
      } else {
        await createMutation.mutateAsync(values)
        message.success('创建成功')
      }
      navigate('/agents')
    } catch {
      message.error(isEdit ? '更新失败' : '创建失败')
    }
  }

  if (isLoading && isEdit) {
    return <div>加载中...</div>
  }

  return (
    <div className="agent-form">
      <div className="page-header">
        <h2>
          <ArrowLeftOutlined
            style={{ cursor: 'pointer', marginRight: 16 }}
            onClick={() => navigate(-1)}
          />
          {isEdit ? '编辑 Agent' : '创建 Agent'}
        </h2>
        <Button onClick={() => navigate(-1)}>返回</Button>
      </div>

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            provider: 'novacode',
            model: 'codex-mini-latest',
            model_variant: 'medium',
            temperature: 0.7,
            max_tokens: 4096,
          }}
        >
          <Form.Item
            label="Agent 名称"
            name="name"
            rules={[
              { required: true, message: '请输入 Agent 名称' },
              { min: 1, max: 100, message: '长度在 1 到 100 个字符' },
            ]}
          >
            <Input placeholder="请输入 Agent 名称" />
          </Form.Item>

          <Form.Item label="描述" name="description">
            <TextArea rows={3} placeholder="请输入 Agent 描述" />
          </Form.Item>

          <Form.Item label="图标 URL" name="icon">
            <Input placeholder="请输入图标 URL（可选）" />
          </Form.Item>

          <Divider orientation="left">模型配置</Divider>

          <Form.Item label="Provider" name="provider">
            <Select placeholder="请选择 Provider">
              <Option value="novacode">NovaCode</Option>
              <Option value="qwen">通义千问</Option>
              <Option value="deepseek">DeepSeek</Option>
              <Option value="kimi">Kimi</Option>
            </Select>
          </Form.Item>

          <Form.Item label="模型" name="model">
            <Select placeholder="请选择模型" showSearch>
              <Option value="gpt-5.4">GPT-5.4 (105 万上下文)</Option>
              <Option value="gpt-5.2-codex">GPT-5.2 Codex</Option>
              <Option value="gpt-5.3-codex">GPT-5.3 Codex</Option>
              <Option value="codex-mini-latest">Codex Mini</Option>
            </Select>
          </Form.Item>

          <Form.Item label="模型变体" name="model_variant">
            <Select placeholder="请选择变体">
              <Option value="low">Low (快速)</Option>
              <Option value="medium">Medium (平衡)</Option>
              <Option value="high">High (高质量)</Option>
              <Option value="xhigh">XHigh (极致)</Option>
            </Select>
          </Form.Item>

          <Form.Item label="温度" name="temperature">
            <Slider min={0} max={2} step={0.1} marks={{ 0: '0', 1: '1', 2: '2' }} />
          </Form.Item>

          <Form.Item label="最大 Tokens" name="max_tokens">
            <InputNumber min={100} max={128000} step={100} style={{ width: '100%' }} />
          </Form.Item>

          <Divider orientation="left">系统提示词</Divider>

          <Form.Item label="系统提示词" name="system_prompt">
            <TextArea
              rows={5}
              placeholder="请输入系统提示词，定义 Agent 的角色和行为（可选）"
            />
          </Form.Item>

          <Divider orientation="left">知识库关联</Divider>

          <Form.Item label="关联知识库" name="knowledge_base_ids">
            <Select
              mode="multiple"
              placeholder="请选择关联的知识库（可选）"
              style={{ width: '100%' }}
            >
              <Option value={1}>BEC 商务英语知识库</Option>
              <Option value={2}>旅游攻略知识库</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={createMutation.isPending || updateMutation.isPending}>
                {isEdit ? '保存' : '创建'}
              </Button>
              <Button onClick={() => navigate(-1)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}

export default AgentForm
