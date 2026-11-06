from datetime import datetime, timezone
from typing import Any

MISSION_NAMES = {
    "Assassination": "刺杀",
    "Capture": "捕获",
    "Defense": "防御",
    "Disruption": "破坏",
    "Excavation": "挖掘",
    "Extermination": "歼灭",
    "Hijack": "劫持",
    "Interception": "拦截",
    "Mobile Defense": "移动防御",
    "Rescue": "救援",
    "Sabotage": "破坏",
    "Spy": "间谍",
    "Survival": "生存",
    "Void Cascade": "虚空洪流",
}


def _remaining(item: dict[str, Any]) -> str:
    expiry = item.get("expiry")
    if not expiry:
        return "剩余时间未知"
    try:
        end = datetime.fromisoformat(str(expiry).replace("Z", "+00:00"))
        seconds = int((end - datetime.now(timezone.utc)).total_seconds())
    except (TypeError, ValueError):
        return "剩余时间未知"
    if seconds <= 0:
        return "即将结束"
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    if hours:
        return f"剩余 {hours}小时{minutes}分"
    return f"剩余 {minutes}分"


def _mission_name(value: Any) -> str:
    name = str(value or "未知任务")
    return MISSION_NAMES.get(name, name)


def format_fissures(payload: Any) -> str:
    if not isinstance(payload, list) or not payload:
        return "当前没有可显示的虚空裂隙。"
    items = sorted(payload, key=lambda item: str(item.get("expiry", "")))[:12]
    lines = ["当前虚空裂隙"]
    for item in items:
        tier = item.get("tier", "未知")
        mission = _mission_name(item.get("missionType"))
        node = item.get("node", "未知节点")
        modifier = "钢铁之路" if item.get("isHard") else ""
        storm = "九重天" if item.get("isStorm") else ""
        flags = " / ".join(value for value in (modifier, storm) if value)
        suffix = f" [{flags}]" if flags else ""
        lines.append(
            f"• {tier} · {mission} · {node}{suffix} · {_remaining(item)}"
        )
    return "\n".join(lines)


def format_sortie(payload: Any) -> str:
    if not isinstance(payload, dict) or not payload:
        return "当前没有可显示的突击任务。"
    lines = [
        f"今日突击：{payload.get('boss', '未知指挥官')}",
        f"剩余时间：{_remaining(payload)}",
    ]
    variants = payload.get("variants")
    if isinstance(variants, list):
        for index, mission in enumerate(variants, start=1):
            if not isinstance(mission, dict):
                continue
            task = _mission_name(mission.get("missionType"))
            node = mission.get("node", "未知节点")
            modifier = mission.get("modifier")
            details = f"（{modifier}）" if modifier else ""
            lines.append(f"{index}. {task} · {node}{details}")
    return "\n".join(lines)


def format_arbitration(payload: Any) -> str:
    if not isinstance(payload, dict) or not payload:
        return "当前没有可显示的仲裁任务。"
    mission = _mission_name(payload.get("type"))
    node = payload.get("node", "未知节点")
    enemy = payload.get("enemy", "未知派系")
    return (
        "当前仲裁\n"
        f"• {mission} · {node}\n"
        f"• 敌人：{enemy}\n"
        f"• {_remaining(payload)}"
    )


def format_alerts(payload: Any) -> str:
    if not isinstance(payload, list) or not payload:
        return "当前没有可显示的警报任务。"
    items = sorted(payload, key=lambda item: str(item.get("expiry", "")))[:5]
    lines = ["当前警报"]
    for item in items:
        mission = item.get("mission") or {}
        reward = item.get("reward") or {}
        node = mission.get("node", "未知节点")
        task = _mission_name(mission.get("type"))
        rewards = reward.get("asString") or "奖励信息未知"
        lines.append(
            f"• {task} · {node}\n"
            f"  奖励：{rewards} · {_remaining(item)}"
        )
    return "\n".join(lines)
