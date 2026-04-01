# BEC 商务英语智能学习平台 - 字段字典

**版本:** 1.0  
**更新时间:** 2026-03-31  
**适用范围:** MVP 核心表字段定义

---

## 1. users

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 用户主键ID |
| username | VARCHAR(64) | 用户名，唯一 |
| email | VARCHAR(128) | 邮箱，唯一，可空 |
| password_hash | VARCHAR(255) | 密码加密存储值 |
| status | VARCHAR(32) | 用户状态，如 active/inactive |
| register_source | VARCHAR(32) | 注册来源，如 web |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 2. user_profile

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 主键ID |
| user_id | BIGINT | 用户ID，关联 users.id |
| target_level | VARCHAR(32) | 目标等级，如 BEC 初/中/高 |
| current_level | VARCHAR(32) | 当前水平 |
| industry_background | VARCHAR(128) | 行业背景 |
| learning_goal | VARCHAR(255) | 学习目标 |
| learning_preference | VARCHAR(255) | 学习偏好 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 3. content_source

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 主键ID |
| source_name | VARCHAR(255) | 内容来源名称 |
| source_type | VARCHAR(32) | 来源类型，如 web/doc/manual/ai |
| source_url | TEXT | 来源链接 |
| source_desc | TEXT | 来源说明 |
| credibility_score | NUMERIC(5,2) | 来源可信度评分 |
| copyright_note | TEXT | 版权说明 |
| created_at | TIMESTAMP | 创建时间 |

---

## 4. raw_content

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 主键ID |
| source_id | BIGINT | 来源ID，关联 content_source.id |
| raw_title | VARCHAR(255) | 原始标题 |
| raw_body | TEXT | 原始正文 |
| raw_format | VARCHAR(32) | 原始格式，如 html/pdf/txt |
| clean_status | VARCHAR(32) | 清洗状态 |
| struct_status | VARCHAR(32) | 结构化状态 |
| created_at | TIMESTAMP | 创建时间 |

---

## 5. vocab_content

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 主键ID |
| raw_content_id | BIGINT | 原始内容ID |
| word | VARCHAR(128) | 单词 |
| phonetic | VARCHAR(128) | 音标 |
| part_of_speech | VARCHAR(32) | 词性 |
| meaning_zh | TEXT | 中文释义 |
| business_example | TEXT | 商务例句 |
| collocation | TEXT | 常见搭配 |
| level | VARCHAR(32) | 适用等级 |
| difficulty | VARCHAR(32) | 难度 |
| review_status | VARCHAR(32) | 审核状态 |
| publish_status | VARCHAR(32) | 发布状态 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 6. pattern_content

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 主键ID |
| raw_content_id | BIGINT | 原始内容ID |
| pattern_text | TEXT | 句型正文 |
| scene_type | VARCHAR(64) | 场景类型 |
| function_type | VARCHAR(64) | 功能类型 |
| example_text | TEXT | 示例表达 |
| slot_desc | TEXT | 替换位说明 |
| level | VARCHAR(32) | 适用等级 |
| difficulty | VARCHAR(32) | 难度 |
| review_status | VARCHAR(32) | 审核状态 |
| publish_status | VARCHAR(32) | 发布状态 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 7. scene_content

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 主键ID |
| raw_content_id | BIGINT | 原始内容ID |
| scene_name | VARCHAR(255) | 场景名称 |
| scene_background | TEXT | 场景背景 |
| training_goal | TEXT | 训练目标 |
| user_role | VARCHAR(128) | 用户角色 |
| ai_role | VARCHAR(128) | AI角色 |
| prompt_template | TEXT | 提示模板 |
| recommended_expression | TEXT | 推荐表达 |
| level | VARCHAR(32) | 适用等级 |
| difficulty | VARCHAR(32) | 难度 |
| review_status | VARCHAR(32) | 审核状态 |
| publish_status | VARCHAR(32) | 发布状态 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 8. question_content

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 主键ID |
| raw_content_id | BIGINT | 原始内容ID |
| module_type | VARCHAR(32) | 所属模块，如 level_test/mock_exam |
| question_type | VARCHAR(32) | 题型 |
| stem | TEXT | 题干 |
| options_json | JSONB | 选项JSON |
| correct_answer | TEXT | 正确答案 |
| explanation | TEXT | 解析 |
| level | VARCHAR(32) | 适用等级 |
| difficulty | VARCHAR(32) | 难度 |
| review_status | VARCHAR(32) | 审核状态 |
| publish_status | VARCHAR(32) | 发布状态 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 9. content_tag

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 主键ID |
| tag_name | VARCHAR(128) | 标签名称 |
| tag_code | VARCHAR(64) | 标签编码，唯一 |
| tag_type | VARCHAR(32) | 标签类型 |
| tag_desc | TEXT | 标签说明 |
| status | VARCHAR(32) | 状态 |
| created_at | TIMESTAMP | 创建时间 |

---

## 10. content_tag_relation

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 主键ID |
| content_type | VARCHAR(32) | 内容类型，如 vocab/pattern/scene/question |
| content_id | BIGINT | 内容ID |
| tag_id | BIGINT | 标签ID |
| created_at | TIMESTAMP | 创建时间 |

---

## 11. content_review_record

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 主键ID |
| content_type | VARCHAR(32) | 内容类型 |
| content_id | BIGINT | 内容ID |
| reviewer_id | BIGINT | 审核人ID |
| review_result | VARCHAR(32) | 审核结果 |
| review_comment | TEXT | 审核意见 |
| reviewed_at | TIMESTAMP | 审核时间 |

---

## 12. user_vocab_progress

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 主键ID |
| user_id | BIGINT | 用户ID |
| vocab_id | BIGINT | 单词ID |
| learn_status | VARCHAR(32) | 学习状态 |
| learn_count | INT | 学习次数 |
| correct_rate | NUMERIC(5,2) | 正确率 |
| last_learned_at | TIMESTAMP | 最近学习时间 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 13. user_pattern_progress

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 主键ID |
| user_id | BIGINT | 用户ID |
| pattern_id | BIGINT | 句型ID |
| learn_status | VARCHAR(32) | 学习状态 |
| learn_count | INT | 学习次数 |
| familiarity_score | NUMERIC(5,2) | 熟悉度评分 |
| last_learned_at | TIMESTAMP | 最近学习时间 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 14. user_scene_session

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 主键ID |
| user_id | BIGINT | 用户ID |
| scene_id | BIGINT | 场景ID |
| session_status | VARCHAR(32) | 会话状态 |
| round_count | INT | 对话轮数 |
| user_summary | TEXT | 用户输入摘要 |
| ai_feedback_summary | TEXT | AI反馈摘要 |
| score | NUMERIC(5,2) | 表现评分 |
| started_at | TIMESTAMP | 开始时间 |
| ended_at | TIMESTAMP | 结束时间 |

---

## 15. level_test_record

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 主键ID |
| user_id | BIGINT | 用户ID |
| total_score | NUMERIC(6,2) | 总分 |
| result_level | VARCHAR(32) | 测试结果等级 |
| ability_summary | TEXT | 能力总结 |
| status | VARCHAR(32) | 状态 |
| started_at | TIMESTAMP | 开始时间 |
| ended_at | TIMESTAMP | 结束时间 |

---

## 16. level_test_answer

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 主键ID |
| test_record_id | BIGINT | 测试记录ID |
| question_id | BIGINT | 题目ID |
| user_answer | TEXT | 用户答案 |
| is_correct | BOOLEAN | 是否正确 |
| score | NUMERIC(6,2) | 得分 |
| created_at | TIMESTAMP | 创建时间 |

---

## 17. mock_exam_record

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 主键ID |
| user_id | BIGINT | 用户ID |
| total_score | NUMERIC(6,2) | 总分 |
| accuracy_rate | NUMERIC(5,2) | 正确率 |
| weak_tags | TEXT | 弱项标签 |
| status | VARCHAR(32) | 状态 |
| started_at | TIMESTAMP | 开始时间 |
| ended_at | TIMESTAMP | 结束时间 |

---

## 18. mock_exam_answer

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | BIGSERIAL | 主键ID |
| exam_record_id | BIGINT | 模考记录ID |
| question_id | BIGINT | 题目ID |
| user_answer | TEXT | 用户答案 |
| is_correct | BOOLEAN | 是否正确 |
| score | NUMERIC(6,2) | 得分 |
| explanation_result | TEXT | 结果说明 |
| created_at | TIMESTAMP | 创建时间 |
