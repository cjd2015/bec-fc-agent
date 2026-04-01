-- BEC 商务英语智能学习平台 - seed.sql
-- 版本: 1.0
-- 更新时间: 2026-03-31
-- 说明: MVP 基础初始化数据

-- 初始化标签
INSERT INTO content_tag (tag_name, tag_code, tag_type, tag_desc, status)
VALUES
('BEC 初级', 'bec_preliminary', 'level', '适用于 BEC 初级学习内容', 'active'),
('BEC 中级', 'bec_vantage', 'level', '适用于 BEC 中级学习内容', 'active'),
('BEC 高级', 'bec_higher', 'level', '适用于 BEC 高级学习内容', 'active'),
('会议沟通', 'meeting', 'scene', '会议沟通场景', 'active'),
('商务邮件', 'email', 'scene', '商务邮件场景', 'active'),
('商务谈判', 'negotiation', 'scene', '商务谈判场景', 'active'),
('汇报表达', 'presentation', 'scene', '汇报表达场景', 'active'),
('词汇学习', 'vocab', 'skill', '词汇能力标签', 'active'),
('句型学习', 'pattern', 'skill', '句型能力标签', 'active'),
('对话训练', 'dialogue', 'skill', '对话训练能力标签', 'active'),
('模拟考试', 'mock_exam', 'skill', '模拟考试能力标签', 'active')
ON CONFLICT (tag_code) DO NOTHING;

-- 初始化默认内容来源
INSERT INTO content_source (source_name, source_type, source_url, source_desc, credibility_score, copyright_note)
VALUES
('内部人工整理内容库', 'manual', NULL, '由产品/内容团队人工整理维护', 90.00, '内部使用'),
('AI辅助生成内容', 'ai', NULL, '由 AI 辅助生成，需人工审核', 70.00, '需人工审核后使用')
ON CONFLICT DO NOTHING;
