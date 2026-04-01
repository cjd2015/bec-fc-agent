import React from 'react'
import { Empty } from 'antd'

const KnowledgeList: React.FC = () => {
  return (
    <div className="knowledge-list">
      <h2>知识库管理（开发中）</h2>
      <Empty description="知识库功能正在开发中，敬请期待..." />
    </div>
  )
}

export default KnowledgeList
