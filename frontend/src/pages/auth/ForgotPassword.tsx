import React, { useState } from 'react'
import { Alert, Button, Card, Form, Input, message, Tabs, Typography } from 'antd'
import { Link, useNavigate } from 'react-router-dom'
import { request } from '@/api'

const { Title, Paragraph } = Typography

interface ForgotFormValues {
  username?: string
  email?: string
}

interface ResetFormValues {
  token: string
  new_password: string
}

const ForgotPasswordPage: React.FC = () => {
  const [requestLoading, setRequestLoading] = useState(false)
  const [resetLoading, setResetLoading] = useState(false)
  const [issuedToken, setIssuedToken] = useState<string>('')
  const [requestForm] = Form.useForm<ForgotFormValues>()
  const [resetForm] = Form.useForm<ResetFormValues>()
  const navigate = useNavigate()

  const handleRequest = async (values: ForgotFormValues) => {
    if (!values.username && !values.email) {
      message.warning('请输入用户名或邮箱')
      return
    }
    setRequestLoading(true)
    try {
      const res = await request<{ data: { reset_token?: string } }>({
        url: '/users/password/forgot',
        method: 'POST',
        data: values,
      })
      const token = res.data.reset_token
      if (token) {
        setIssuedToken(token)
        message.success('重置 token 已生成（仅供联调）')
      } else {
        setIssuedToken('')
        message.success('申请成功，请查看通知渠道获取 token')
      }
    } catch (error) {
      message.error(error instanceof Error ? error.message : '申请重置失败')
    } finally {
      setRequestLoading(false)
    }
  }

  const handleReset = async (values: ResetFormValues) => {
    setResetLoading(true)
    try {
      await request({
        url: '/users/password/reset',
        method: 'POST',
        data: values,
      })
      message.success('密码已重置，请使用新密码登录')
      resetForm.resetFields()
      navigate('/login')
    } catch (error) {
      message.error(error instanceof Error ? error.message : '重置失败')
    } finally {
      setResetLoading(false)
    }
  }

  return (
    <div
      style={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#f5f5f5',
        padding: 16,
      }}
    >
      <Card style={{ maxWidth: 460, width: '100%' }}>
        <Title level={3}>找回密码</Title>
        <Paragraph type="secondary">
          暂时以 token 形式返回，后续可接入短信/邮件。在生产环境请勿展示 token。
        </Paragraph>

        <Tabs
          defaultActiveKey="request"
          items={[
            {
              key: 'request',
              label: '申请重置',
              children: (
                <Form layout="vertical" form={requestForm} onFinish={handleRequest} autoComplete="off">
                  <Form.Item name="username" label="用户名">
                    <Input placeholder="输入用户名" />
                  </Form.Item>
                  <Form.Item name="email" label="邮箱">
                    <Input placeholder="或输入邮箱" />
                  </Form.Item>
                  <Button type="primary" htmlType="submit" block loading={requestLoading}>
                    申请重置
                  </Button>
                  {issuedToken ? (
                    <Alert
                      style={{ marginTop: 16 }}
                      showIcon
                      type="info"
                      message="调试用 token"
                      description={issuedToken}
                    />
                  ) : null}
                </Form>
              ),
            },
            {
              key: 'reset',
              label: '使用 token 重置',
              children: (
                <Form layout="vertical" form={resetForm} onFinish={handleReset} autoComplete="off">
                  <Form.Item
                    name="token"
                    label="重置 token"
                    rules={[{ required: true, message: '请输入 token' }]}
                  >
                    <Input placeholder="请输入收到的 token" />
                  </Form.Item>
                  <Form.Item
                    name="new_password"
                    label="新密码"
                    rules={[{ required: true, min: 8, message: '至少 8 位密码' }]}
                  >
                    <Input.Password placeholder="输入新密码" />
                  </Form.Item>
                  <Button type="primary" htmlType="submit" block loading={resetLoading}>
                    重置密码
                  </Button>
                </Form>
              ),
            },
          ]}
        />

        <div style={{ marginTop: 16, textAlign: 'center' }}>
          <Link to="/login">返回登录</Link>
        </div>
      </Card>
    </div>
  )
}

export default ForgotPasswordPage
