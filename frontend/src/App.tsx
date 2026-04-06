import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import KnowledgeList from '@/pages/knowledge/KnowledgeList'
import Chat from '@/pages/chat/Chat'
import TaskList from '@/pages/tasks/TaskList'
import LoginPage from '@/pages/auth/Login'
import ForgotPasswordPage from '@/pages/auth/ForgotPassword'
import ProfilePage from '@/pages/profile/Profile'
import LevelTestPage from '@/pages/assessment/LevelTest'
import MockExamPage from '@/pages/assessment/MockExam'
import RequireAuth from '@/components/RequireAuth'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
        <Route index element={<Navigate to="/tasks" replace />} />
        <Route path="knowledge" element={<KnowledgeList />} />
        <Route path="chat" element={<Chat />} />
        <Route path="tasks" element={<TaskList />} />
        <Route path="level-test" element={<LevelTestPage />} />
        <Route path="mock-exam" element={<MockExamPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="*" element={<Navigate to="/tasks" replace />} />
      </Route>
    </Routes>
  )
}

export default App
