import React, { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout as AntLayout, Menu, Avatar, Dropdown } from 'antd'
import type { MenuProps } from 'antd'
import {
  Monitor,
  User,
  Document,
  ChatDotRound,
  Calendar,
  Logout,
} from '@ant-design/icons'

const { Header, Sider, Content } = AntLayout

const Layout: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)

  const menuItems: MenuProps['items'] = [
    {
      key: '/agents',
      icon: <User />,
      label: 'BEC Agent',
    },
    {
      key: '/knowledge',
      icon: <Document />,
      label: '知识库',
    },
    {
      key: '/chat',
      icon: <ChatDotRound />,
      label: '对话测试',
    },
    {
      key: '/tasks',
      icon: <Calendar />,
      label: '任务管理',
    },
  ]

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      label: '个人设置',
    },
    {
      key: 'logout',
      icon: <Logout />,
      label: '退出登录',
    },
  ]

  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    if (key === 'logout') {
      localStorage.removeItem('token')
      navigate('/login')
    } else {
      navigate(key)
    }
  }

  return (
    <AntLayout style={{ height: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="dark"
        width={250}
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: collapsed ? 0 : 18,
            fontWeight: 'bold',
            overflow: 'hidden',
          }}
        >
          <Monitor style={{ fontSize: 24, marginRight: 8 }} />
          {!collapsed && 'AI Agent Platform'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <AntLayout>
        <Header
          style={{
            background: '#fff',
            padding: '0 24px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            boxShadow: '0 1px 4px rgba(0,21,41,.08)',
          }}
        >
          <div style={{ fontSize: 18, fontWeight: 600 }}>
            {getLocationTitle(location.pathname)}
          </div>
          <Dropdown menu={{ items: userMenuItems, onClick: handleMenuClick }}>
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
              <Avatar icon={<User />} size={32} />
              <span style={{ marginLeft: 8 }}>Admin</span>
            </div>
          </Dropdown>
        </Header>
        <Content
          style={{
            margin: 24,
            padding: 24,
            background: '#fff',
            borderRadius: 4,
            overflow: 'auto',
          }}
        >
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  )
}

function getLocationTitle(pathname: string): string {
  const map: Record<string, string> = {
    '/agents': 'BEC Agent 管理',
    '/agents/create': '创建 Agent',
    '/knowledge': '知识库',
    '/chat': '对话测试',
    '/tasks': '任务管理',
  }

  if (pathname.startsWith('/agents/') && pathname !== '/agents' && pathname !== '/agents/create') {
    return 'Agent 详情'
  }

  return map[pathname] || 'AI Agent Platform'
}

export default Layout
