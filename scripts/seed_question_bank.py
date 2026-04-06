#!/usr/bin/env python3
"""Seed additional level test and mock exam questions into Postgres."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set in .env")

LevelQuestion = Dict[str, str]

LEVEL_TEST_QUESTIONS: List[LevelQuestion] = [
    {
        "stem": "Which email closing is most appropriate when you promise future help?",
        "options": [
            "Thanks!",
            "Thank you for your support and please let me know if you need anything else.",
            "Thx buddy",
            "Bye"
        ],
        "answer": "Thank you for your support and please let me know if you need anything else.",
        "explanation": "A complete closing sentence keeps a formal and helpful tone.",
        "level": "BEC Preliminary",
        "difficulty": "easy",
    },
    {
        "stem": "What does 'circle back' usually mean in business English?",
        "options": [
            "Ignore someone",
            "Return to the topic later",
            "Schedule a party",
            "Cancel the plan"
        ],
        "answer": "Return to the topic later",
        "explanation": "'Circle back' signals revisiting an item after gathering more info.",
        "level": "BEC Preliminary",
        "difficulty": "easy",
    },
    {
        "stem": "Choose the best phrase for arranging a short sync call.",
        "options": [
            "Give me your time",
            "Could we have a quick sync at 3 p.m. tomorrow?",
            "Call me now",
            "Need meeting"
        ],
        "answer": "Could we have a quick sync at 3 p.m. tomorrow?",
        "explanation": "It clearly proposes a polite meeting time.",
        "level": "BEC Preliminary",
        "difficulty": "easy",
    },
    {
        "stem": "Which sentence best acknowledges a colleague's idea?",
        "options": [
            "Whatever",
            "That makes sense, and we could also explore option B",
            "Next",
            "Stop"
        ],
        "answer": "That makes sense, and we could also explore option B",
        "explanation": "It validates the idea and adds constructive input.",
        "level": "BEC Preliminary",
        "difficulty": "medium",
    },
    {
        "stem": "Select the clearest reminder for unpaid invoices.",
        "options": [
            "Pay now",
            "This is a friendly reminder that invoice #248 is due on Friday.",
            "Money please",
            "Hurry up"
        ],
        "answer": "This is a friendly reminder that invoice #248 is due on Friday.",
        "explanation": "It references the invoice and keeps a professional tone.",
        "level": "BEC Preliminary",
        "difficulty": "medium",
    },
    {
        "stem": "Which phrase best escalates an issue politely?",
        "options": [
            "I already told you",
            "May I escalate this to our director so we can unblock the shipment?",
            "Handle it",
            "This is not my job"
        ],
        "answer": "May I escalate this to our director so we can unblock the shipment?",
        "explanation": "It states the intention and the business reason.",
        "level": "BEC Vantage",
        "difficulty": "medium",
    },
    {
        "stem": "Choose the best transition for a status presentation.",
        "options": [
            "Whatever, next",
            "Now let us move to the risk mitigation plan",
            "Skip it",
            "Done"
        ],
        "answer": "Now let us move to the risk mitigation plan",
        "explanation": "A clear transition keeps listeners oriented.",
        "level": "BEC Vantage",
        "difficulty": "easy",
    },
    {
        "stem": "What is the most diplomatic way to challenge a budget cut?",
        "options": [
            "You cannot",
            "Could we review the impact on client commitments before finalizing the cut?",
            "This is nonsense",
            "Forget it"
        ],
        "answer": "Could we review the impact on client commitments before finalizing the cut?",
        "explanation": "It questions the change while focusing on business outcomes.",
        "level": "BEC Vantage",
        "difficulty": "medium",
    },
    {
        "stem": "Select the strongest phrase for summarizing next steps in a meeting.",
        "options": [
            "All good",
            "To summarize, marketing will deliver the draft by Tuesday and finance will confirm the budget.",
            "That is it",
            "Okay"
        ],
        "answer": "To summarize, marketing will deliver the draft by Tuesday and finance will confirm the budget.",
        "explanation": "It clearly assigns owners and deadlines.",
        "level": "BEC Vantage",
        "difficulty": "medium",
    },
    {
        "stem": "Which sentence best requests clarification on a KPI?",
        "options": [
            "Explain",
            "Could you clarify whether the KPI is measured weekly or monthly?",
            "Why",
            "Tell"
        ],
        "answer": "Could you clarify whether the KPI is measured weekly or monthly?",
        "explanation": "It specifies what needs clarification.",
        "level": "BEC Vantage",
        "difficulty": "easy",
    },
    {
        "stem": "How should you highlight a strategic risk in an executive review?",
        "options": [
            "We may fail",
            "There is a high probability that supply delays will impact Q3 revenue unless we confirm a secondary vendor.",
            "Maybe bad",
            "It is risky"
        ],
        "answer": "There is a high probability that supply delays will impact Q3 revenue unless we confirm a secondary vendor.",
        "explanation": "It quantifies the risk and proposes mitigation.",
        "level": "BEC Higher",
        "difficulty": "hard",
    },
    {
        "stem": "Choose the best statement for aligning global stakeholders.",
        "options": [
            "Do what I said",
            "Let us align with both APAC and EMEA teams so the pricing narrative stays consistent across regions.",
            "Follow me",
            "Just copy"
        ],
        "answer": "Let us align with both APAC and EMEA teams so the pricing narrative stays consistent across regions.",
        "explanation": "It specifies whom to align and why.",
        "level": "BEC Higher",
        "difficulty": "medium",
    },
    {
        "stem": "Which option demonstrates effective executive persuasion?",
        "options": [
            "You must approve",
            "Approving the additional headcount will shorten onboarding by two weeks and protect the go-live date.",
            "No choice",
            "Trust me"
        ],
        "answer": "Approving the additional headcount will shorten onboarding by two weeks and protect the go-live date.",
        "explanation": "It connects the request to measurable business impact.",
        "level": "BEC Higher",
        "difficulty": "medium",
    },
    {
        "stem": "Select the most persuasive response to a client's quality concern.",
        "options": [
            "Relax",
            "We have added an extra QA gate so your shipment meets every compliance requirement.",
            "Do not worry",
            "Later"
        ],
        "answer": "We have added an extra QA gate so your shipment meets every compliance requirement.",
        "explanation": "It shows a concrete action tied to the client's worry.",
        "level": "BEC Higher",
        "difficulty": "medium",
    },
    {
        "stem": "Which phrase best asks for a strategic decision timeline?",
        "options": [
            "Decide now",
            "Could you let us know the decision timeline so we can reserve production capacity?",
            "Tell me",
            "Time please"
        ],
        "answer": "Could you let us know the decision timeline so we can reserve production capacity?",
        "explanation": "It links the decision timing to a business dependency.",
        "level": "BEC Vantage",
        "difficulty": "medium",
    },
]


LEVEL_TEST_QUESTIONS.extend(
    [
        {
            "stem": "Which sentence best asks a colleague to send the meeting attachments?",
            "options": [
                "Give files",
                "Could you please forward the deck and notes after the call?",
                "Files now",
                "Send it"
            ],
            "answer": "Could you please forward the deck and notes after the call?",
            "explanation": "It is a polite and specific follow-up request.",
            "level": "BEC Preliminary",
            "difficulty": "easy",
        },
        {
            "stem": "Choose the best phrase to confirm understanding of action items.",
            "options": [
                "Ok",
                "Just to confirm, I will share the draft and you will review it by Thursday, correct?",
                "Fine",
                "Sure"
            ],
            "answer": "Just to confirm, I will share the draft and you will review it by Thursday, correct?",
            "explanation": "It restates owners and deadline clearly.",
            "level": "BEC Preliminary",
            "difficulty": "medium",
        },
        {
            "stem": "Which expression politely requests meeting minutes?",
            "options": [
                "Send minutes",
                "Would you mind sharing the meeting minutes once they are ready?",
                "We need it",
                "Do it"
            ],
            "answer": "Would you mind sharing the meeting minutes once they are ready?",
            "explanation": "It is polite and gives context.",
            "level": "BEC Preliminary",
            "difficulty": "easy",
        },
        {
            "stem": "What is the most professional way to acknowledge a delay?",
            "options": [
                "We are late",
                "We apologize for the delay and have added extra staff to recover the timeline.",
                "Sorry",
                "Deal with it"
            ],
            "answer": "We apologize for the delay and have added extra staff to recover the timeline.",
            "explanation": "It acknowledges responsibility and shares a solution.",
            "level": "BEC Preliminary",
            "difficulty": "medium",
        },
        {
            "stem": "Which phrase best requests an updated forecast?",
            "options": [
                "Tell future",
                "Could you share the revised sales forecast before Friday's leadership call?",
                "Forecast now",
                "Update soon"
            ],
            "answer": "Could you share the revised sales forecast before Friday's leadership call?",
            "explanation": "It is precise about the deliverable and deadline.",
            "level": "BEC Vantage",
            "difficulty": "medium",
        },
        {
            "stem": "How should you highlight a dependency risk to partners?",
            "options": [
                "Risk big",
                "Our launch depends on your API by 5 May; without it the training sequence slips two weeks.",
                "Be careful",
                "Need API"
            ],
            "answer": "Our launch depends on your API by 5 May; without it the training sequence slips two weeks.",
            "explanation": "It quantifies impact and names the dependency.",
            "level": "BEC Vantage",
            "difficulty": "medium",
        },
        {
            "stem": "Choose the best statement to secure resources from leadership.",
            "options": [
                "Give us budget",
                "Approving two additional engineers now keeps the regulatory deadline on track and avoids penalty fees.",
                "Need people",
                "Send staff"
            ],
            "answer": "Approving two additional engineers now keeps the regulatory deadline on track and avoids penalty fees.",
            "explanation": "It ties the request to measurable business impact.",
            "level": "BEC Vantage",
            "difficulty": "medium",
        },
        {
            "stem": "Which sentence best frames ROI in an executive summary?",
            "options": [
                "ROI is ok",
                "This project delivers a 4x ROI within 12 months by reducing manual onboarding cost by $1.2M.",
                "Profit soon",
                "Money good"
            ],
            "answer": "This project delivers a 4x ROI within 12 months by reducing manual onboarding cost by $1.2M.",
            "explanation": "It quantifies value and timing.",
            "level": "BEC Higher",
            "difficulty": "medium",
        },
        {
            "stem": "How do you request compliance documentation from a vendor?",
            "options": [
                "Send docs",
                "Could you provide the latest SOC 2 certificate so our audit team can finalize approval?",
                "Need proof",
                "Compliance now"
            ],
            "answer": "Could you provide the latest SOC 2 certificate so our audit team can finalize approval?",
            "explanation": "It states exactly what is needed and why.",
            "level": "BEC Higher",
            "difficulty": "medium",
        },
        {
            "stem": "Which statement is best when offering service credits in a negotiation?",
            "options": [
                "Take discount",
                "If we provide two months of service credits, could you commit to the three-year renewal?",
                "Free service",
                "We pay"
            ],
            "answer": "If we provide two months of service credits, could you commit to the three-year renewal?",
            "explanation": "It frames the concession as a trade-off.",
            "level": "BEC Higher",
            "difficulty": "medium",
        },
        {
            "stem": "Which sentence summarizes cross-team dependencies most clearly?",
            "options": [
                "Teams must help",
                "Legal must finalize the contract draft by Monday so procurement can issue the PO on Wednesday.",
                "Do everything",
                "We all know"
            ],
            "answer": "Legal must finalize the contract draft by Monday so procurement can issue the PO on Wednesday.",
            "explanation": "It names owners and dates.",
            "level": "BEC Higher",
            "difficulty": "medium",
        },
        {
            "stem": "Which option best escalates a customer risk to the GM?",
            "options": [
                "Customer angry",
                "Our top-three customer is threatening to pause orders unless we guarantee the quality audit this Friday.",
                "Need help",
                "Fix it"
            ],
            "answer": "Our top-three customer is threatening to pause orders unless we guarantee the quality audit this Friday.",
            "explanation": "It qualifies the risk and urgency.",
            "level": "BEC Higher",
            "difficulty": "hard",
        },
    ]
)

MOCK_EXAM_QUESTIONS: List[LevelQuestion] = [
    {
        "stem": "Which reply best handles a client's urgent shipment request?",
        "options": [
            "Wait your turn",
            "We can prioritize production this week and share a revised delivery schedule tomorrow.",
            "Not possible",
            "Later"
        ],
        "answer": "We can prioritize production this week and share a revised delivery schedule tomorrow.",
        "explanation": "It acknowledges urgency and offers a concrete plan.",
        "level": "BEC Vantage",
        "difficulty": "medium",
    },
    {
        "stem": "Choose the best statement to summarize market insight in a report.",
        "options": [
            "Market is fine",
            "Customer data shows a 12% shift to premium bundles, so we should highlight value-add features in the launch deck.",
            "Everyone buys",
            "We guess"
        ],
        "answer": "Customer data shows a 12% shift to premium bundles, so we should highlight value-add features in the launch deck.",
        "explanation": "It quantifies the trend and links it to an action.",
        "level": "BEC Higher",
        "difficulty": "medium",
    },
    {
        "stem": "Which negotiation move keeps the discussion collaborative?",
        "options": [
            "Take it or leave it",
            "If we extend payment terms, could you increase the monthly volume commitment?",
            "Your problem",
            "We quit"
        ],
        "answer": "If we extend payment terms, could you increase the monthly volume commitment?",
        "explanation": "It proposes a trade-off instead of a threat.",
        "level": "BEC Vantage",
        "difficulty": "medium",
    },
    {
        "stem": "Select the best follow-up after a steering committee decision.",
        "options": [
            "Great",
            "Thank you for approving phase two. We will circulate the updated implementation roadmap by Friday.",
            "Cool",
            "Done"
        ],
        "answer": "Thank you for approving phase two. We will circulate the updated implementation roadmap by Friday.",
        "explanation": "It acknowledges the decision and states a clear next step.",
        "level": "BEC Vantage",
        "difficulty": "easy",
    },
    {
        "stem": "Which sentence best communicates a risk mitigation plan to stakeholders?",
        "options": [
            "Risk exists",
            "To mitigate the vendor outage, we have activated two backup suppliers and secured inventory for six weeks.",
            "Maybe fine",
            "Ignore it"
        ],
        "answer": "To mitigate the vendor outage, we have activated two backup suppliers and secured inventory for six weeks.",
        "explanation": "It names the mitigation steps and timeframe.",
        "level": "BEC Higher",
        "difficulty": "medium",
    },
    {
        "stem": "Choose the strongest briefing update for leadership.",
        "options": [
            "Working on it",
            "The pilot reduced support tickets by 28%, so we recommend rolling it out to APAC next month.",
            "Fine",
            "Ok"
        ],
        "answer": "The pilot reduced support tickets by 28%, so we recommend rolling it out to APAC next month.",
        "explanation": "It shares data and a recommendation.",
        "level": "BEC Higher",
        "difficulty": "medium",
    },
    {
        "stem": "Which response best addresses a team's workload concern?",
        "options": [
            "Work faster",
            "Let us redistribute the client migrations so each pod handles three accounts instead of five.",
            "Too bad",
            "Deal with it"
        ],
        "answer": "Let us redistribute the client migrations so each pod handles three accounts instead of five.",
        "explanation": "It proposes a concrete adjustment.",
        "level": "BEC Vantage",
        "difficulty": "medium",
    },
    {
        "stem": "Which reply best handles a customer complaint about onboarding speed?",
        "options": [
            "Wait",
            "I understand the concern. We have assigned a dedicated specialist to complete the onboarding checklist by Wednesday.",
            "Cannot help",
            "Later"
        ],
        "answer": "I understand the concern. We have assigned a dedicated specialist to complete the onboarding checklist by Wednesday.",
        "explanation": "It shows empathy plus a specific fix.",
        "level": "BEC Preliminary",
        "difficulty": "medium",
    },
    {
        "stem": "Select the best sentence for summarizing action items in meeting minutes.",
        "options": [
            "Tasks noted",
            "Engineering will deliver the beta build on 18 April and sales will launch the customer webinar on 25 April.",
            "We all know",
            "Done"
        ],
        "answer": "Engineering will deliver the beta build on 18 April and sales will launch the customer webinar on 25 April.",
        "explanation": "It clearly lists owners and deadlines.",
        "level": "BEC Preliminary",
        "difficulty": "easy",
    },
]


MOCK_EXAM_QUESTIONS.extend(
    [
        {
            "stem": "Which statement best communicates a phased rollout plan?",
            "options": [
                "Roll out",
                "We will pilot with 50 enterprise customers in May, gather feedback for two weeks, then expand globally in June.",
                "Launch all",
                "Everyone now"
            ],
            "answer": "We will pilot with 50 enterprise customers in May, gather feedback for two weeks, then expand globally in June.",
            "explanation": "It shows timing and next steps.",
            "level": "BEC Higher",
            "difficulty": "medium",
        },
        {
            "stem": "Which option best frames a commercial concession?",
            "options": [
                "Discount given",
                "If you sign the three-year term, we can extend payment terms to 60 days and add premium support.",
                "Ok cheaper",
                "Take price"
            ],
            "answer": "If you sign the three-year term, we can extend payment terms to 60 days and add premium support.",
            "explanation": "It trades concessions for commitment.",
            "level": "BEC Higher",
            "difficulty": "medium",
        },
        {
            "stem": "Which sentence best summarizes customer health for leadership?",
            "options": [
                "Customers fine",
                "ARR retention is 94% but two strategic accounts need executive outreach due to integration delays.",
                "Ok",
                "All good"
            ],
            "answer": "ARR retention is 94% but two strategic accounts need executive outreach due to integration delays.",
            "explanation": "It combines a metric with a call to action.",
            "level": "BEC Higher",
            "difficulty": "medium",
        },
        {
            "stem": "Which response best addresses an RFP clarification?",
            "options": [
                "See spec",
                "Attached is the security architecture diagram plus the data encryption policy you requested.",
                "Later",
                "Use manual"
            ],
            "answer": "Attached is the security architecture diagram plus the data encryption policy you requested.",
            "explanation": "It confirms delivery of the exact materials.",
            "level": "BEC Vantage",
            "difficulty": "medium",
        },
        {
            "stem": "What is the strongest wrap-up for a quarterly business review?",
            "options": [
                "Thanks",
                "To close, we agreed on three priorities: stabilize onboarding, launch the upsell pilot, and review pricing in July.",
                "Bye",
                "That's it"
            ],
            "answer": "To close, we agreed on three priorities: stabilize onboarding, launch the upsell pilot, and review pricing in July.",
            "explanation": "It summarizes commitments and timing.",
            "level": "BEC Vantage",
            "difficulty": "easy",
        },
        {
            "stem": "Which sentence best explains a financial variance to the CFO?",
            "options": [
                "Costs up",
                "Marketing costs exceeded plan by $180k because the APAC launch was pulled ahead by one quarter.",
                "Budget bad",
                "Too expensive"
            ],
            "answer": "Marketing costs exceeded plan by $180k because the APAC launch was pulled ahead by one quarter.",
            "explanation": "It quantifies the variance and reason.",
            "level": "BEC Higher",
            "difficulty": "medium",
        },
    ]
)


def insert_questions(items: List[LevelQuestion], module_type: str) -> int:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    inserted = 0
    with engine.begin() as conn:
        for item in items:
            exists = conn.execute(
                text(
                    """
                    SELECT 1 FROM question_content
                    WHERE module_type = :module_type AND stem = :stem
                    LIMIT 1
                    """
                ),
                {"module_type": module_type, "stem": item["stem"]},
            ).first()
            if exists:
                continue
            conn.execute(
                text(
                    """
                    INSERT INTO question_content (
                        module_type, question_type, stem, options_json,
                        correct_answer, explanation, level, difficulty,
                        review_status, publish_status
                    ) VALUES (
                        :module_type, 'single_choice', :stem, :options_json,
                        :correct_answer, :explanation, :level, :difficulty,
                        'approved', 'published'
                    )
                    """
                ),
                {
                    "module_type": module_type,
                    "stem": item["stem"],
                    "options_json": json.dumps(item["options"]),
                    "correct_answer": item["answer"],
                    "explanation": item["explanation"],
                    "level": item["level"],
                    "difficulty": item["difficulty"],
                },
            )
            inserted += 1
    return inserted


def main() -> None:
    level_count = insert_questions(LEVEL_TEST_QUESTIONS, "level_test")
    mock_count = insert_questions(MOCK_EXAM_QUESTIONS, "mock_exam")
    print(f"Inserted {level_count} new level test questions and {mock_count} mock exam questions.")


if __name__ == "__main__":
    main()
