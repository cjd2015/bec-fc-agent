import React, { useEffect, useState } from 'react'
import { Alert, Button, Card, Col, Form, Input, message, Row, Space, Typography } from 'antd'
import { request } from '@/api'
import { getAuthSession, updateAuthSession } from '@/utils/auth'

const { Title, Paragraph } = Typography

interface UserProfileInfo {
  target_level?: string | null
  current_level?: string | null
  industry_background?: string | null
  learning_goal?: string | null
  learning_preference?: string | null
  display_name?: string | null
  avatar_url?: string | null
  bio?: string | null
  phone_number?: string | null
  company?: string | null
  job_title?: string | null
}

interface ProfileResponse {
  id: number
  username: string
  email: string | null
  status: string
  profile?: UserProfileInfo | null
}

const ProfilePage: React.FC = () => {
  const session = getAuthSession()
  const username = session?.username
  const [profileForm] = Form.useForm()
  const [passwordForm] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [passwordLoading, setPasswordLoading] = useState(false)
  const [resetTokenMessage, setResetTokenMessage] = useState<string>('')

  useEffect(() => {
    if (!username) return
    const fetchProfile = async () => {
      setLoading(true)
      try {
        const res = await request<{ data: ProfileResponse }>({
          url: '/users/profile',
          method: 'GET',
        })
        profileForm.setFieldsValue({
          email: res.data.email ?? '',
          ...res.data.profile,
        })
      } catch (error) {
        message.error(error instanceof Error ? error.message : '加载用户信息失败')
      } finally {
        setLoading(false)
      }
    }
    fetchProfile()
  }, [username, profileForm])

  const handleProfileSubmit = async (values: Record<string, any>) => {
    if (!username) return
    try {
      await request({
        url: '/users/profile',
        method: 'PUT',
        data: values,
      })
      updateAuthSession({ displayName: values.display_name })
      message.success('资料已更新')
    } catch (error) {
      message.error(error instanceof Error ? error.message : '更新失败')
    }
  }

  const handlePasswordChange = async (values: { current_password: string; new_password: string }) => {
    if (!username) return
    setPasswordLoading(true)
    try {
      await request({
        url: '/users/password/change',
        method: 'POST',
        data: {
          current_password: values.current_password,
          new_password: values.new_password,
        },
      })
      message.success('密码已修改，请使用新密码重新登录体验')
      passwordForm.resetFields()
    } catch (error) {
      message.error(error instanceof Error ? error.message : '修改密码失败')
    } finally {
      setPasswordLoading(false)
    }
  }

  const handleForgotPassword = async () => {
    if (!username) return
    try {
      const res = await request<{ data: { reset_token?: string } }>({
        url: '/users/password/forgot',
        method: 'POST',
        data: { username },
      })
      const token = res.data.reset_token
      if (token) {
        setResetTokenMessage(`临时重置 token（请尽快使用）：${token}`)
      } else {
        setResetTokenMessage('已申请重置密码，请查收通知渠道。')
      }
    } catch (error) {
      message.error(error instanceof Error ? error.message : '重置密码申请失败')
    }
  }

  if (!username) {
    return <Alert type="error" message="未找到登录信息，请重新登录" />
  }

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <div>
        <Title level={2}>学习档案</Title>
        <Paragraph type="secondary">
          数据将直接写入 FC handler 的 PostgreSQL。这里可以维护个人信息、学习目标以及账号密码。
        </Paragraph>
      </div>

      <Row gutter={16}>
        <Col xs={24} lg={14}>
          <Card title="基本资料" loading={loading}>
            <Form form={profileForm} layout="vertical" onFinish={handleProfileSubmit}>
              <Form.Item name="display_name" label="昵称">
                <Input placeholder="展示名称" />
              </Form.Item>
              <Form.Item name="email" label="邮箱">
                <Input placeholder="邮箱" />
              </Form.Item>
              <Form.Item name="phone_number" label="电话">
                <Input placeholder="电话" />
              </Form.Item>
              <Form.Item name="company" label="公司">
                <Input placeholder="所在公司" />
              </Form.Item>
              <Form.Item name="job_title" label="职位">
                <Input placeholder="职位" />
              </Form.Item>
              <Form.Item name="target_level" label="目标等级">
                <Input placeholder="例如：BEC Higher" />
              </Form.Item>
              <Form.Item name="current_level" label="当前等级">
                <Input placeholder="例如：BEC Vantage" />
              </Form.Item>
              <Form.Item name="learning_goal" label="学习目标">
                <Input.TextArea rows={3} placeholder="希望达成的学习目标" />
              </Form.Item>
              <Form.Item name="learning_preference" label="学习偏好">
                <Input.TextArea rows={2} placeholder="学习方式偏好" />
              </Form.Item>
              <Button type="primary" htmlType="submit">
                保存资料
              </Button>
            </Form>
          </Card>
        </Col>

        <Col xs={24} lg={10}>
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <Card title="修改密码">
              <Form layout="vertical" form={passwordForm} onFinish={handlePasswordChange}>
                <Form.Item
                  name="current_password"
                  label="当前密码"
                  rules={[{ required: true, message: '请输入当前密码' }]}
                >
                  <Input.Password placeholder="当前密码" />
                </Form.Item>
                <Form.Item
                  name="new_password"
                  label="新密码"
                  rules={[{ required: true, min: 8, message: '至少 8 位密码' }]}
                >
                  <Input.Password placeholder="新密码" />
                </Form.Item>
                <Button type="primary" htmlType="submit" loading={passwordLoading}>
                  修改密码
                </Button>
              </Form>
            </Card>

            <Card title="忘记密码">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Paragraph>
                  应急方案：点击按钮向后台申请重置 token，返回值仅用于联调验证，实际场景应发送邮件或短信。
                </Paragraph>
                <Button onClick={handleForgotPassword}>申请重置 token</Button>
                {resetTokenMessage ? <Alert type="info" message={resetTokenMessage} showIcon /> : null}
              </Space>
            </Card>
          </Space>
        </Col>
      </Row>
    </Space>
  )
}

export default ProfilePage
