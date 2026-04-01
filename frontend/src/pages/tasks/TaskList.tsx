import React from 'react'
import { Empty } from 'antd'

const TaskList: React.FC = () => {
  return (
    <div className="task-list">
      <h2>任务管理（开发中）</h2>
      <Empty description="任务管理功能正在开发中，敬请期待..." />
    </div>
  )
}

export default TaskList
