import React, { useState } from 'react'
import { Button, Card, Form, Input, message, Tabs, Typography } from 'antd'
import { LockOutlined, MailOutlined, UserOutlined } from '@ant-design/icons'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import type { Location } from 'react-router-dom'
import { request } from '@/api'
import { saveAuthSession } from '@/utils/auth'

const { Title, Paragraph, Text } = Typography

interface LoginPayload {
  username: string
  password: string
}

interface RegisterPayload extends LoginPayload {
  email?: string
}

const LoginPage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [registerLoading, setRegisterLoading] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as { from?: Location })?.from?.pathname || '/tasks'

  const handleLogin = async (values: LoginPayload) => {
    setLoading(true)
    try {
      const res = await request<{ data: { id: number; username: string; status: string; token?: string } }>({
        url: '/auth/login',
        method: 'POST',
        data: values,
      })
      saveAuthSession({ username: res.data.username, userId: res.data.id, token: res.data.token })
      message.success('登录成功')
      navigate(from, { replace: true })
    } catch (error) {
      message.error(error instanceof Error ? error.message : '登录失败')
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (values: RegisterPayload) => {
    setRegisterLoading(true)
    try {
      const res = await request<{ data: { id: number; username: string; email?: string | null; status: string; token?: string } }>({
        url: '/auth/register',
        method: 'POST',
        data: values,
      })
      if (res.data.token) {
        saveAuthSession({ username: res.data.username, userId: res.data.id, token: res.data.token })
        message.success('注册成功，已自动登录')
        navigate(from, { replace: true })
      } else {
        message.success('注册成功，请使用新账户登录')
      }
    } catch (error) {
      message.error(error instanceof Error ? error.message : '注册失败')
    } finally {
      setRegisterLoading(false)
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
      <Card style={{ maxWidth: 420, width: '100%' }}>
        <SpaceBlock />
        <Title level={3} style={{ marginBottom: 8 }}>BEC 商务英语学习平台</Title>
        <Paragraph type="secondary">使用真实账号登录后，可同步到 FC handler 的所有学习数据。</Paragraph>

        <Tabs
          defaultActiveKey="login"
          items={[
            {
              key: 'login',
              label: '登录',
              children: (
                <Form layout="vertical" onFinish={handleLogin} autoComplete="off">
                  <Form.Item
                    name="username"
                    label="用户名"
                    rules={[{ required: true, message: '请输入用户名' }]}
                  >
                    <Input prefix={<UserOutlined />} placeholder="用户名" />
                  </Form.Item>
                  <Form.Item
                    name="password"
                    label="密码"
                    rules={[{ required: true, message: '请输入密码' }]}
                  >
                    <Input.Password prefix={<LockOutlined />} placeholder="密码" />
                  </Form.Item>
                  <Button type="primary" htmlType="submit" block loading={loading}>
                    登录
                  </Button>
                  <div style={{ marginTop: 12, textAlign: 'right' }}>
                    <Link to="/forgot-password">忘记密码？</Link>
                  </div>
                </Form>
              ),
            },
            {
              key: 'register',
              label: '注册新账号',
              children: (
                <Form layout="vertical" onFinish={handleRegister} autoComplete="off">
                  <Form.Item
                    name="username"
                    label="用户名"
                    rules={[{ required: true, message: '请输入用户名' }]}
                  >
                    <Input prefix={<UserOutlined />} placeholder="用户名" />
                  </Form.Item>
                  <Form.Item name="email" label="邮箱">
                    <Input prefix={<MailOutlined />} placeholder="邮箱（可选）" />
                  </Form.Item>
                  <Form.Item
                    name="password"
                    label="密码"
                    rules={[{ required: true, min: 8, message: '至少 8 位密码' }]}
                  >
                    <Input.Password prefix={<LockOutlined />} placeholder="密码" />
                  </Form.Item>
                  <Button type="primary" htmlType="submit" block loading={registerLoading}>
                    注册
                  </Button>
                </Form>
              ),
            },
          ]}
        />
        <Text type="secondary">忘记密码？点击登录窗体中的“忘记密码”，可离线申请 token。</Text>
      </Card>
    </div>
  )
}

const SpaceBlock = () => <div style={{ height: 8 }} />

export default LoginPage
