import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import AgentList from '@/pages/agents/AgentList'
import AgentForm from '@/pages/agents/AgentForm'
import AgentDetail from '@/pages/agents/AgentDetail'
import AgentVersions from '@/pages/agents/AgentVersions'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/agents" replace />} />
        <Route path="agents" element={<AgentList />} />
        <Route path="agents/create" element={<AgentForm />} />
        <Route path="agents/:id" element={<AgentDetail />} />
        <Route path="agents/:id/edit" element={<AgentForm />} />
        <Route path="agents/:id/versions" element={<AgentVersions />} />
        <Route path="knowledge" element={<div>知识库（开发中）</div>} />
        <Route path="chat" element={<div>对话测试（开发中）</div>} />
        <Route path="tasks" element={<div>任务管理（开发中）</div>} />
      </Route>
    </Routes>
  )
}

export default App
