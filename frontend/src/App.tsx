import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import KnowledgeList from '@/pages/knowledge/KnowledgeList'
import Chat from '@/pages/chat/Chat'
import TaskList from '@/pages/tasks/TaskList'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/tasks" replace />} />
        <Route path="knowledge" element={<KnowledgeList />} />
        <Route path="chat" element={<Chat />} />
        <Route path="tasks" element={<TaskList />} />
        <Route path="*" element={<Navigate to="/tasks" replace />} />
      </Route>
    </Routes>
  )
}

export default App
