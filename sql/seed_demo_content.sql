BEGIN;

INSERT INTO question_content (module_type, question_type, stem, options_json, correct_answer, explanation, level, difficulty, review_status, publish_status)
VALUES
('level_test', 'single_choice', 'Which phrase is most appropriate to open a formal business email?', '["Hi buddy", "Dear Mr. Chen", "Yo Chen", "Hey there"]'::jsonb, 'Dear Mr. Chen', 'Formal business emails usually start with a professional salutation.', 'BEC Preliminary', 'easy', 'approved', 'published'),
('level_test', 'single_choice', 'Choose the best response in a meeting: "Could you clarify the timeline?"', '["Yes, I timeline", "Sure, we expect delivery next Friday", "Timeline is good", "No comment"]'::jsonb, 'Sure, we expect delivery next Friday', 'The best answer directly clarifies the schedule.', 'BEC Preliminary', 'easy', 'approved', 'published'),
('level_test', 'single_choice', 'What does "follow up" most likely mean in business English?', '["Cancel a task", "Check progress later", "Sign a contract", "Take a vacation"]'::jsonb, 'Check progress later', 'Follow up means checking progress after an earlier action.', 'BEC Preliminary', 'easy', 'approved', 'published'),
('level_test', 'single_choice', 'Choose the most suitable phrase for negotiation.', '["Take it or leave it", "Let us explore a win-win solution", "I do not care", "Whatever"]'::jsonb, 'Let us explore a win-win solution', 'Negotiation language should be cooperative and professional.', 'BEC Vantage', 'medium', 'approved', 'published'),
('level_test', 'single_choice', 'Which sentence is best for a presentation transition?', '["Anyway, next", "Moving on to the next point", "Stop here", "You know"]'::jsonb, 'Moving on to the next point', 'It is the clearest and most professional transition.', 'BEC Vantage', 'easy', 'approved', 'published'),
('level_test', 'single_choice', 'Which option best expresses a polite disagreement?', '["You are wrong", "I see your point, but I have a different view", "No", "Impossible"]'::jsonb, 'I see your point, but I have a different view', 'Polite disagreement is important in business settings.', 'BEC Vantage', 'medium', 'approved', 'published'),
('level_test', 'single_choice', 'What is the best phrase for confirming understanding?', '["Got it", "If I understand correctly, the shipment leaves on Monday", "Fine", "Okay maybe"]'::jsonb, 'If I understand correctly, the shipment leaves on Monday', 'This phrase is explicit and professional.', 'BEC Higher', 'medium', 'approved', 'published'),
('level_test', 'single_choice', 'Choose the best phrase to close a meeting.', '["Bye", "Let us summarize the action items", "Enough", "End now"]'::jsonb, 'Let us summarize the action items', 'Summarizing action items is a strong business habit.', 'BEC Higher', 'medium', 'approved', 'published'),
('level_test', 'single_choice', 'Which sentence sounds most professional in a delay notice?', '["We are late, sorry", "We regret the delay and are taking steps to resolve it", "Delay happened", "Not our problem"]'::jsonb, 'We regret the delay and are taking steps to resolve it', 'Professional delay notices acknowledge the issue and show action.', 'BEC Higher', 'hard', 'approved', 'published'),
('level_test', 'single_choice', 'Which phrase best invites questions after a presentation?', '["Any issues?", "I would be happy to take your questions", "No questions", "Finished"]'::jsonb, 'I would be happy to take your questions', 'This is polite and natural in presentations.', 'BEC Vantage', 'easy', 'approved', 'published')
ON CONFLICT DO NOTHING;

INSERT INTO vocab_content (word, phonetic, part_of_speech, meaning_zh, business_example, collocation, level, difficulty, review_status, publish_status)
VALUES
('agenda', '/əˈdʒendə/', 'noun', '议程', 'Let us begin with the first item on today''s agenda.', 'meeting agenda', 'BEC Preliminary', 'easy', 'approved', 'published'),
('deadline', '/ˈdedlaɪn/', 'noun', '截止日期', 'We need to meet the client''s deadline.', 'meet a deadline', 'BEC Preliminary', 'easy', 'approved', 'published'),
('shipment', '/ˈʃɪpmənt/', 'noun', '货运，发货', 'The shipment will arrive on Thursday.', 'shipment delay', 'BEC Preliminary', 'easy', 'approved', 'published'),
('invoice', '/ˈɪnvɔɪs/', 'noun', '发票', 'Please send the invoice by email.', 'issue an invoice', 'BEC Preliminary', 'easy', 'approved', 'published'),
('negotiate', '/nɪˈɡoʊʃieɪt/', 'verb', '谈判', 'We need to negotiate better payment terms.', 'negotiate terms', 'BEC Vantage', 'medium', 'approved', 'published'),
('proposal', '/prəˈpoʊzl/', 'noun', '提案', 'The sales team prepared a detailed proposal.', 'submit a proposal', 'BEC Vantage', 'easy', 'approved', 'published'),
('stakeholder', '/ˈsteɪkhoʊldər/', 'noun', '利益相关方', 'We should update all stakeholders.', 'key stakeholder', 'BEC Vantage', 'medium', 'approved', 'published'),
('margin', '/ˈmɑːrdʒɪn/', 'noun', '利润空间', 'Our margin improved this quarter.', 'profit margin', 'BEC Vantage', 'medium', 'approved', 'published'),
('benchmark', '/ˈbentʃmɑːrk/', 'noun', '基准', 'This result is our industry benchmark.', 'set a benchmark', 'BEC Higher', 'medium', 'approved', 'published'),
('allocate', '/ˈæləkeɪt/', 'verb', '分配', 'We need to allocate more budget to marketing.', 'allocate resources', 'BEC Higher', 'medium', 'approved', 'published');

INSERT INTO pattern_content (pattern_text, scene_type, function_type, example_text, slot_desc, level, difficulty, review_status, publish_status)
VALUES
('Could we + verb ...?', 'meeting', 'polite_request', 'Could we review the sales forecast together?', '用于礼貌提出请求', 'BEC Preliminary', 'easy', 'approved', 'published'),
('I''d like to + verb ...', 'presentation', 'introduction', 'I''d like to begin with a quick overview.', '用于引出发言或议题', 'BEC Preliminary', 'easy', 'approved', 'published'),
('Would it be possible to + verb ...?', 'email', 'polite_request', 'Would it be possible to move the meeting to Friday?', '用于更正式地提出请求', 'BEC Vantage', 'medium', 'approved', 'published'),
('From our perspective, ...', 'negotiation', 'opinion', 'From our perspective, a longer contract term would be beneficial.', '用于表达立场', 'BEC Vantage', 'medium', 'approved', 'published'),
('If I understand correctly, ...', 'meeting', 'confirmation', 'If I understand correctly, the new pricing starts next month.', '用于确认理解', 'BEC Higher', 'medium', 'approved', 'published'),
('We regret to inform you that ...', 'email', 'formal_notice', 'We regret to inform you that the shipment has been delayed.', '用于正式告知不利消息', 'BEC Higher', 'hard', 'approved', 'published');

COMMIT;
