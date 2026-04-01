BEGIN;
INSERT INTO question_content (module_type, question_type, stem, options_json, correct_answer, explanation, level, difficulty, review_status, publish_status)
VALUES
('mock_exam', 'single_choice', 'Which sentence is best for politely asking for an update?', '["Update me now", "Could you please share the latest progress update?", "Where is it?", "Tell me quickly"]'::jsonb, 'Could you please share the latest progress update?', 'Polite update requests are common in business communication.', 'BEC Preliminary', 'easy', 'approved', 'published'),
('mock_exam', 'single_choice', 'Which response is most suitable when a client requests a discount?', '["No chance", "We can discuss volume-based pricing options", "Too expensive for you", "Not interested"]'::jsonb, 'We can discuss volume-based pricing options', 'This keeps the negotiation open and professional.', 'BEC Vantage', 'medium', 'approved', 'published'),
('mock_exam', 'single_choice', 'Choose the strongest sentence for summarizing a proposal.', '["That is it", "In summary, this proposal reduces cost and improves delivery speed", "Okay done", "Please decide"]'::jsonb, 'In summary, this proposal reduces cost and improves delivery speed', 'A strong summary highlights value clearly.', 'BEC Higher', 'medium', 'approved', 'published');
COMMIT;
