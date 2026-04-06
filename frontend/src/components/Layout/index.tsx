import React, { useMemo, useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout as AntLayout, Menu, Avatar, Dropdown, Button } from 'antd'
import type { MenuProps } from 'antd'
import {
  BookOutlined,
  MessageOutlined,
  DashboardOutlined,
  ReadOutlined,
  LogoutOutlined,
  UserOutlined,
  IdcardOutlined,
  ExperimentOutlined,
  TrophyOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons'
import { clearAuthSession, getAuthSession } from '@/utils/auth'

const { Header, Sider, Content } = AntLayout

const Layout: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)
  const [isMobile, setIsMobile] = useState(false)
  const session = getAuthSession()
  const displayName = session?.displayName || session?.username || '学员'

  const menuItems: MenuProps['items'] = [
    {
      key: '/tasks',
      icon: <DashboardOutlined />,
      label: '学习看板',
    },
    {
      key: '/level-test',
      icon: <ExperimentOutlined />,
      label: '水平测试',
    },
    {
      key: '/mock-exam',
      icon: <TrophyOutlined />,
      label: '模拟考试',
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
      key: '/profile',
      icon: <IdcardOutlined />,
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
      clearAuthSession()
      navigate('/login', { replace: true })
      return
    }
    navigate(key)
    if (isMobile) {
      setCollapsed(true)
    }
  }

  const selectedKey = useMemo(() => {
    if (location.pathname === '/' || location.pathname === '') {
      return '/tasks'
    }
    return location.pathname
  }, [location.pathname])

  const toggleCollapsed = () => {
    setCollapsed((prev) => !prev)
  }

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        trigger={null}
        theme="dark"
        width={250}
        collapsedWidth={isMobile ? 0 : 72}
        breakpoint="lg"
        onBreakpoint={(broken) => {
          setIsMobile(broken)
          setCollapsed(broken)
        }}
        style={{ position: isMobile ? 'fixed' : 'relative', height: '100vh', zIndex: 1000 }}
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
        <Menu theme="dark" mode="inline" selectedKeys={[selectedKey]} items={menuItems} onClick={handleMenuClick} />
      </Sider>
      <AntLayout style={{ marginLeft: isMobile && !collapsed ? 250 : 0, transition: 'margin-left 0.2s ease' }}>
        <Header
          style={{
            background: '#fff',
            padding: isMobile ? '0 16px' : '0 24px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 12,
            flexWrap: 'wrap',
            boxShadow: '0 1px 4px rgba(0,21,41,.08)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <Button
              type="text"
              onClick={toggleCollapsed}
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              className="layout-toggle"
            />
            <div style={{ fontSize: 18, fontWeight: 600 }}>{getLocationTitle(location.pathname)}</div>
          </div>
          <Dropdown menu={{ items: userMenuItems, onClick: handleMenuClick }}>
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
              <Avatar icon={<UserOutlined />} size={32} />
              <span style={{ marginLeft: 8 }}>{displayName}</span>
            </div>
          </Dropdown>
        </Header>
        <Content
          style={{
            margin: isMobile ? 12 : 24,
            padding: isMobile ? 16 : 24,
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
    '/level-test': '商务英语水平测试',
    '/mock-exam': '模拟考试',
  }

  return map[pathname] || 'BEC 学习平台'
}

export default Layout
