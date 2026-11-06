# 天诺通讯（AstrBot）

AstrBot 群聊插件原型，首版查询国际服 PC 世界状态。插件不要求 Warframe 账号，也不保存账号凭据。

## 当前命令

使用 AstrBot 配置的命令前缀：

- `wf`：显示帮助
- `wf 裂隙`
- `wf 突击`
- `wf 仲裁`
- `wf 警报`

每周无尽任务排行榜目前未实现。找到的周榜路径只是社区兼容实现中的未验证线索，不是 DE 公开承诺的 API。

## 本地测试

1. 将仓库克隆或复制到 AstrBot 实例的 `data/plugins/astrbot_plugin_tenno_dispatch/`。插件安装目录必须与 `metadata.yaml` 中的 Python 模块标识一致。
2. 重启 AstrBot，或在 WebUI 插件管理中加载并启用本地插件。
3. 在 AstrBot 测试会话发送 `wf`、`wf 裂隙` 等命令。命令前缀以你的 AstrBot 配置为准。
4. 若查询失败，先检查运行 AstrBot 的环境能否访问 `https://api.warframestat.us`；插件会在日志记录错误类型，并在数据源恢复前最多使用 15 分钟缓存。

插件使用 AstrBot 自带的 `aiohttp`，没有额外 Python 依赖。

## QQ 接入

插件命令不依赖 QQ 专属 API。先在本地 AstrBot 测试会话验证插件，再配置 QQ 平台适配器即可。

- AstrBot 文档推荐 QQ 官方机器人 WebSocket 接入，提供扫码绑定流程；若能使用官方机器人，这是优先推荐的路线。
- 若你已有 OneBot v11 + NapCat 环境，可直接复用；它是第三方协议实现，部署步骤和账号/平台规则风险需自行评估。

使用哪种接入方式不影响插件代码。
