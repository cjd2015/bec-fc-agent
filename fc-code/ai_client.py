import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
from src.core.config import Settings

logger = logging.getLogger("ai_client")


DEFAULT_PROVIDER_CONFIG = {
    "novacode": {
        "base_url": "https://ai.novacode.top/v1",
        "model": "gpt-5.4",
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
    },
}


class AIChatClient:
    """Minimal chat completion client for FC handler."""

    def __init__(self, settings: Settings):
        provider = (settings.model_provider or os.environ.get("MODEL_PROVIDER") or "novacode").lower()
        default_cfg = DEFAULT_PROVIDER_CONFIG.get(provider, DEFAULT_PROVIDER_CONFIG["novacode"])

        self.base_url = (settings.model_base_url or os.environ.get("MODEL_BASE_URL") or default_cfg["base_url"]).rstrip("/")
        self.api_key = settings.model_api_key or os.environ.get("MODEL_API_KEY")
        if not self.api_key:
            env_key = f"{provider.upper()}_API_KEY"
            self.api_key = os.environ.get(env_key)
        self.model_name = settings.model_name or os.environ.get("MODEL_NAME") or default_cfg["model"]
        self.timeout = settings.model_timeout_seconds or 60
        self.provider = provider
        self.enabled = bool(self.base_url and self.api_key and self.model_name)
        self.last_error: Optional[str] = None
        self.last_error_time: Optional[str] = None
        self.last_success_time: Optional[str] = None

    def _record_error(self, message: str):
        self.last_error = message
        self.last_error_time = datetime.utcnow().isoformat()
        self.last_success_time = None
        logger.warning("AI request failed: %s", message)

    def _record_success(self):
        self.last_error = None
        self.last_error_time = None
        self.last_success_time = datetime.utcnow().isoformat()

    def debug_status(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "provider": self.provider,
            "base_url": self.base_url,
            "model": self.model_name,
            "timeout": self.timeout,
            "last_error": self.last_error,
            "last_error_time": self.last_error_time,
            "last_success_time": self.last_success_time,
        }

        self.last_error: Optional[str] = None
        self.last_error_time: Optional[str] = None
        self.last_success_time: Optional[str] = None

    def _build_messages(self, system_prompt: str, user_prompt: str):
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _request(self, payload: Dict) -> Optional[str]:
        if not self.enabled:
            return None
        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            response = httpx.post(endpoint, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices") or []
            if not choices:
                self._record_error("empty choices from AI response")
                return None
            self._record_success()
            return choices[0].get("message", {}).get("content")
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:1000] if exc.response is not None else str(exc)
            self._record_error(f"HTTP {exc.response.status_code if exc.response else 'NA'}: {body}")
            return None
        except Exception as exc:
            self._record_error(str(exc))
            return None

    def _chat(self, messages, temperature: float = 0.7, max_tokens: int = 600) -> Optional[str]:
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        return self._request(payload)

    def generate_scene_reply(
        self,
        scene_name: str,
        ai_role: str,
        training_goal: str,
        user_message: str,
        recommended_expression: Optional[str] = None,
        history: Optional[str] = None,
    ) -> Optional[Dict[str, str]]:
        if not self.enabled:
            return None
        system_prompt = (
            "You are role-playing in a Business English training scene. "
            "Respond strictly in JSON with keys reply and feedback. "
            "reply should be the AI role's answer (max 80 words). "
            "feedback should be actionable coaching tips (max 60 words)."
        )
        history_text = f"Previous conversation summary:\n{history}" if history else ""
        user_prompt = (
            f"Scene name: {scene_name}. AI role: {ai_role}. Training goal: {training_goal}.\n"
            f"Recommended expressions: {recommended_expression or 'N/A'}.\n"
            f"{history_text}\n"
            f"Latest learner message: {user_message}."
        )
        messages = self._build_messages(system_prompt, user_prompt)
        raw = self._chat(messages, temperature=0.6, max_tokens=400)
        if not raw:
            return None
        try:
            parsed = json.loads(raw)
            reply = parsed.get("reply") or parsed.get("response")
            feedback = parsed.get("feedback") or parsed.get("coach")
            if reply and feedback:
                return {"reply": reply, "feedback": feedback}
        except json.JSONDecodeError:
            logger.debug("AI response is not JSON, returning raw text")
        return {"reply": raw.strip(), "feedback": recommended_expression or training_goal}

    def generate_scene_summary(
        self,
        scene_name: str,
        training_goal: str,
        user_summary: Optional[str],
        ai_feedback_summary: Optional[str],
    ) -> Optional[Dict[str, str]]:
        if not self.enabled:
            return None
        system_prompt = (
            "You are a Business English coach summarizing a completed role play. "
            "Return JSON with keys summary, feedback, score. "
            "score should be an integer between 60 and 95."
        )
        user_prompt = (
            f"Scene: {scene_name}. Training goal: {training_goal}.\n"
            f"Learner contributions:\n{user_summary or 'N/A'}\n"
            f"Coach feedback so far:\n{ai_feedback_summary or 'N/A'}"
        )
        raw = self._chat(self._build_messages(system_prompt, user_prompt), temperature=0.4, max_tokens=300)
        if not raw:
            return None
        try:
            parsed = json.loads(raw)
            summary = parsed.get("summary") or parsed.get("result")
            feedback = parsed.get("feedback") or parsed.get("tips")
            score = parsed.get("score")
            if summary and feedback:
                return {
                    "summary": summary,
                    "feedback": feedback,
                    "score": int(score) if score else None,
                }
        except json.JSONDecodeError:
            logger.debug("Summary response is not JSON")
        return {"summary": raw.strip(), "feedback": training_goal, "score": None}
