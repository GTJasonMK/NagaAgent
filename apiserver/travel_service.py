#!/usr/bin/env python3
"""
旅行服务 — 状态管理、持久化、提示词构建、结果解析
"""

import json
import re
import uuid
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ── 数据目录 ────────────────────────────────────

TRAVEL_DIR = Path("logs/travel")
TRAVEL_DIR.mkdir(parents=True, exist_ok=True)


# ── 数据模型 ────────────────────────────────────

class TravelStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TravelDiscovery(BaseModel):
    url: str
    title: str
    summary: str
    found_at: str  # ISO 8601
    tags: list[str] = []


class SocialInteraction(BaseModel):
    type: str  # "post_created", "reply_sent", "friend_request"
    post_id: Optional[str] = None
    content_preview: str
    timestamp: str


class TravelSession(BaseModel):
    session_id: str
    status: TravelStatus = TravelStatus.PENDING
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    # 用户配置
    time_limit_minutes: int = 300
    credit_limit: int = 1000
    want_friends: bool = True
    friend_description: Optional[str] = None
    # 运行时跟踪
    openclaw_session_key: Optional[str] = None
    tokens_used: int = 0
    credits_used: int = 0
    elapsed_minutes: float = 0.0
    # 结果
    discoveries: list[TravelDiscovery] = []
    social_interactions: list[SocialInteraction] = []
    summary: Optional[str] = None
    error: Optional[str] = None


# ── 持久化 ──────────────────────────────────────

def _session_path(session_id: str) -> Path:
    return TRAVEL_DIR / f"{session_id}.json"


def create_session(
    time_limit_minutes: int = 300,
    credit_limit: int = 1000,
    want_friends: bool = True,
    friend_description: Optional[str] = None,
) -> TravelSession:
    """创建并持久化一个新的旅行 session"""
    session = TravelSession(
        session_id=uuid.uuid4().hex[:16],
        created_at=datetime.now().isoformat(),
        time_limit_minutes=time_limit_minutes,
        credit_limit=credit_limit,
        want_friends=want_friends,
        friend_description=friend_description,
    )
    save_session(session)
    logger.info(f"旅行 session 已创建: {session.session_id}")
    return session


def save_session(session: TravelSession) -> None:
    """将 session 写入 JSON 文件"""
    path = _session_path(session.session_id)
    path.write_text(session.model_dump_json(indent=2), encoding="utf-8")


def load_session(session_id: str) -> TravelSession:
    """从文件读取 session"""
    path = _session_path(session_id)
    if not path.exists():
        raise FileNotFoundError(f"旅行 session 不存在: {session_id}")
    return TravelSession.model_validate_json(path.read_text(encoding="utf-8"))


def get_active_session() -> Optional[TravelSession]:
    """找到当前 status=running 的 session（最多一个）"""
    for path in TRAVEL_DIR.glob("*.json"):
        try:
            session = TravelSession.model_validate_json(path.read_text(encoding="utf-8"))
            if session.status == TravelStatus.RUNNING:
                return session
        except Exception:
            continue
    return None


def list_sessions() -> list[TravelSession]:
    """列出所有 session，按 created_at 倒序"""
    sessions: list[TravelSession] = []
    for path in TRAVEL_DIR.glob("*.json"):
        try:
            sessions.append(TravelSession.model_validate_json(path.read_text(encoding="utf-8")))
        except Exception:
            continue
    sessions.sort(key=lambda s: s.created_at, reverse=True)
    return sessions


# ── Prompt 构建 ─────────────────────────────────

def build_travel_prompt(session: TravelSession) -> str:
    """生成给 OpenClaw 的探索指令"""
    return f"""你正在进行一次网络旅行探索。

**任务目标：**
- 自由浏览互联网，发现有趣的内容、网站、文章或社区
- 探索不同领域：技术、艺术、科学、文化等
- 记录你发现的每个有趣内容

**时间限制：** {session.time_limit_minutes} 分钟
**积分限制：** {session.credit_limit} 积分

**记录格式：**
每发现一个有趣内容，用以下格式记录：

[DISCOVERY]
url: <网页URL>
title: <标题>
summary: <一句话总结>
tags: <标签1>, <标签2>
[/DISCOVERY]

请开始你的旅行！从一些热门网站或有趣的话题开始探索。每次访问网页后记录发现。"""


def build_social_prompt(session: TravelSession) -> str:
    """生成社交指令"""
    desc = session.friend_description or "任何有趣的AI Agent"
    return f"""**社交任务：**
在旅行过程中，你还有一个社交目标：在娜迦网络论坛上与其他 AI 互动。

想认识的朋友类型：{desc}

**社交行为：**
1. 浏览娜迦网络论坛的帖子
2. 对感兴趣的帖子发表评论
3. 如果遇到符合描述的AI，在评论中标记"想要认识"
4. 也可以发布自己的帖子分享旅行中的发现

**记录格式：**
每次社交互动，用以下格式记录：

[SOCIAL]
type: <post_created|reply_sent|friend_request>
post_id: <帖子ID，如有>
content_preview: <互动内容预览>
[/SOCIAL]"""


# ── 结果解析 ─────────────────────────────────────

_DISCOVERY_RE = re.compile(
    r"\[DISCOVERY\]\s*"
    r"url:\s*(?P<url>.+?)\s*"
    r"title:\s*(?P<title>.+?)\s*"
    r"summary:\s*(?P<summary>.+?)\s*"
    r"(?:tags:\s*(?P<tags>.+?)\s*)?"
    r"\[/DISCOVERY\]",
    re.DOTALL,
)

_SOCIAL_RE = re.compile(
    r"\[SOCIAL\]\s*"
    r"type:\s*(?P<type>.+?)\s*"
    r"(?:post_id:\s*(?P<post_id>.+?)\s*)?"
    r"content_preview:\s*(?P<content_preview>.+?)\s*"
    r"\[/SOCIAL\]",
    re.DOTALL,
)


def parse_discoveries(history_messages: list[dict]) -> list[TravelDiscovery]:
    """从 OpenClaw 回复中解析 [DISCOVERY]...[/DISCOVERY] 格式"""
    discoveries: list[TravelDiscovery] = []
    now = datetime.now().isoformat()
    for msg in history_messages:
        content = msg.get("content", "")
        if not content:
            continue
        for m in _DISCOVERY_RE.finditer(content):
            tags_str = m.group("tags") or ""
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]
            discoveries.append(TravelDiscovery(
                url=m.group("url").strip(),
                title=m.group("title").strip(),
                summary=m.group("summary").strip(),
                found_at=now,
                tags=tags,
            ))
    return discoveries


def parse_social(history_messages: list[dict]) -> list[SocialInteraction]:
    """解析 [SOCIAL]...[/SOCIAL] 格式"""
    interactions: list[SocialInteraction] = []
    now = datetime.now().isoformat()
    for msg in history_messages:
        content = msg.get("content", "")
        if not content:
            continue
        for m in _SOCIAL_RE.finditer(content):
            post_id = m.group("post_id")
            if post_id:
                post_id = post_id.strip()
                if post_id.lower() in ("none", "null", ""):
                    post_id = None
            interactions.append(SocialInteraction(
                type=m.group("type").strip(),
                post_id=post_id,
                content_preview=m.group("content_preview").strip(),
                timestamp=now,
            ))
    return interactions
