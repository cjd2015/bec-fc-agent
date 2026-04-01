BEGIN;
INSERT INTO scene_content (
  scene_name, scene_background, training_goal, user_role, ai_role,
  prompt_template, recommended_expression, level, difficulty, review_status, publish_status
) VALUES
(
  'Project Kickoff Meeting',
  'You are joining a kickoff meeting with a new overseas client to confirm timeline, responsibilities, and communication rules.',
  'Practice opening a meeting, clarifying deliverables, and confirming next steps.',
  'Project coordinator',
  'Client representative',
  'You are a professional overseas client representative. Hold a short kickoff discussion, ask about timeline and deliverables, and respond naturally in business English.',
  'Could we align on the timeline?; Let us summarize the action items.; If I understand correctly, ...',
  'BEC Vantage',
  'medium',
  'approved',
  'published'
),
(
  'Shipment Delay Call',
  'A customer is calling about a delayed shipment and expects a clear explanation plus a recovery plan.',
  'Practice apologizing professionally, explaining delay reasons, and proposing solutions.',
  'Account manager',
  'Concerned customer',
  'You are a concerned customer asking why the shipment is late and what compensation or solution is available.',
  'We regret to inform you that ...; We are taking steps to resolve it.; Would it be possible to ...',
  'BEC Higher',
  'hard',
  'approved',
  'published'
),
(
  'Weekly Sales Update',
  'You need to report weekly sales performance to your manager and highlight both progress and risks.',
  'Practice giving a concise update, reporting numbers, and flagging issues.',
  'Sales executive',
  'Sales manager',
  'You are a sales manager listening to an update. Ask follow-up questions about numbers, risks, and next actions.',
  'I''d like to begin with ...; From our perspective, ...; Moving on to the next point.',
  'BEC Preliminary',
  'easy',
  'approved',
  'published'
);
COMMIT;
