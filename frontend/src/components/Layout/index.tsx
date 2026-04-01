import React, { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout as AntLayout, Menu, Avatar, Dropdown } from 'antd'
import type { MenuProps } from 'antd'
import {
  BookOutlined,
  MessageOutlined,
  DashboardOutlined,
  ReadOutlined,
  LogoutOutlined,
  UserOutlined,
} from '@ant-design/icons'

const { Header, Sider, Content } = AntLayout

const Layout: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)

  const menuItems: MenuProps['items'] = [
    {
      key: '/tasks',
      icon: <DashboardOutlined />,
      label: '学习看板',
    },
    {
      key: '/knowledge',
      icon: <BookOutlined />,
      label: '词汇与句型',
    },
    {
      key: '/chat',
      icon: <MessageOutlined />,
      label: '场景训练',
    },
  ]

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      label: '学习档案',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
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
          <ReadOutlined style={{ fontSize: 24, marginRight: 8 }} />
          {!collapsed && 'BEC 学习平台'}
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
              <Avatar icon={<UserOutlined />} size={32} />
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
    '/knowledge': '词汇与句型学习',
    '/chat': '场景对话训练',
    '/tasks': '学习进度看板',
  }

  return map[pathname] || 'BEC 学习平台'
}

export default Layout
