import asyncio
from datetime import datetime, timezone
from typing import Any

import aiohttp
from astrbot.api import logger, star
from astrbot.api.event import AstrMessageEvent, filter

from .formatting import format_arbitration, format_alerts, format_fissures, format_sortie

PLUGIN_NAME = "astrbot_plugin_tenno_dispatch"
API_BASE = "https://api.warframestat.us/pc"
CACHE_SECONDS = 60
STALE_CACHE_SECONDS = 15 * 60

COMMANDS = {
    "fissures": ("裂隙", "fissure", "fissures"),
    "sortie": ("突击", "突击任务", "sortie"),
    "arbitration": ("仲裁", "仲裁任务", "arbitration"),
    "alerts": ("警报", "alerts", "alert"),
}
FORMATTERS = {
    "fissures": format_fissures,
    "sortie": format_sortie,
    "arbitration": format_arbitration,
    "alerts": format_alerts,
}


@star.register(
    PLUGIN_NAME,
    "CJwen",
    "查询星际战甲世界状态。",
    "0.1.0",
)
class WarframeHelperPlugin(star.Star):
    """Provide lightweight Warframe world-state commands."""

    def __init__(self, context: star.Context) -> None:
        super().__init__(context)
        self._session: aiohttp.ClientSession | None = None
        self._cache: dict[str, tuple[float, Any]] = {}
        self._cache_lock = asyncio.Lock()

    async def _get_data(self, endpoint: str) -> tuple[Any, bool]:
        """Fetch a world-state endpoint and return data plus stale-cache status."""
        now = asyncio.get_running_loop().time()
        cached = self._cache.get(endpoint)
        if cached and now - cached[0] < CACHE_SECONDS:
            return cached[1], False

        async with self._cache_lock:
            now = asyncio.get_running_loop().time()
            cached = self._cache.get(endpoint)
            if cached and now - cached[0] < CACHE_SECONDS:
                return cached[1], False

            if self._session is None or self._session.closed:
                timeout = aiohttp.ClientTimeout(total=8)
                self._session = aiohttp.ClientSession(
                    timeout=timeout,
                    headers={
                        "Accept": "application/json",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.6",
                        "User-Agent": f"{PLUGIN_NAME}/0.1.0",
                    },
                    trust_env=True,
                )

            try:
                async with self._session.get(f"{API_BASE}/{endpoint}") as response:
                    response.raise_for_status()
                    payload = await response.json(content_type=None)
                self._cache[endpoint] = (now, payload)
                return payload, False
            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as exc:
                logger.warning(
                    "Warframe world-state request failed: endpoint=%s error=%s",
                    endpoint,
                    type(exc).__name__,
                )
                cached = self._cache.get(endpoint)
                if cached and now - cached[0] <= STALE_CACHE_SECONDS:
                    return cached[1], True
                raise

    @filter.command("wf")
    async def warframe(self, event: AstrMessageEvent, action: str | None = None):
        """Show Warframe world state for the requested category."""
        aliases = {
            alias: key for key, values in COMMANDS.items() for alias in values
        }
        if not action or action.lower() in {"help", "帮助"}:
            yield event.plain_result(
                "天诺通讯（国际服 PC 数据）\n"
                "用法：wf 裂隙 / wf 突击 / wf 仲裁 / wf 警报\n"
                "每周无尽任务排行榜：接口尚未验证，当前版本不提供查榜。"
            )
            return

        endpoint = aliases.get(action.lower())
        if endpoint is None:
            yield event.plain_result("未知类别。发送 wf 帮助 查看可用命令。")
            return

        try:
            payload, is_stale = await self._get_data(endpoint)
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
            yield event.plain_result(
                "暂时无法读取世界状态数据源，请稍后重试。"
                "本版本不使用游戏账号登录，也不会要求账号密码。"
            )
            return

        updated_at = datetime.now(timezone.utc).astimezone().strftime("%H:%M")
        result = FORMATTERS[endpoint](payload)
        if is_stale:
            result += "\n（数据源暂不可用，以下为缓存数据）"
        else:
            result += f"\n查询时间：{updated_at}"
        yield event.plain_result(result)

    async def terminate(self) -> None:
        """Close the shared HTTP session during plugin shutdown."""
        if self._session and not self._session.closed:
            await self._session.close()
