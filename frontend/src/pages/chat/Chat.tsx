import React from 'react'
import { Empty } from 'antd'

const Chat: React.FC = () => {
  return (
    <div className="chat">
      <h2>对话测试（开发中）</h2>
      <Empty description="对话测试功能正在开发中，敬请期待..." />
    </div>
  )
}

export default Chat
