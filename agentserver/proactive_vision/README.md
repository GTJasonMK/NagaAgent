# Proactive Vision System - 主动屏幕识别系统

## 概述

Proactive Vision（主动视觉）是NagaAgent的一个可选功能模块，让AI能够主动观察屏幕状态，在检测到特定条件时主动与用户对话。

## 功能特性

- ✨ **智能调度**：可配置截图间隔和静默时段
- 🎯 **规则引擎**：支持关键词匹配和AI智能场景识别
- 🔔 **主动对话**：检测到特定情况时主动发起对话
- ⚡ **低开销**：差分检测、智能缓存、CPU占用<5%
- 🔒 **隐私保护**：所有截图本地处理，不上传云端

## 架构设计

```
ProactiveVision System
├── Scheduler (调度器)    - 定时截图和任务编排
├── Analyzer (分析器)     - 调用screen_vision进行AI视觉分析
├── Trigger (触发器)      - 管理冷却时间和发送主动消息
└── Config (配置管理)     - 规则定义和系统配置
```

## 快速开始

### 1. 启用系统

编辑项目根目录的 `proactive_vision_config.json`：

```json
{
  "enabled": true,
  "check_interval_seconds": 30,
  "analysis_mode": "smart"
}
```

或通过API启用：

```bash
curl -X POST http://localhost:8001/proactive_vision/enable \\
  -H "Content-Type: application/json" \\
  -d '{"enabled": true}'
```

### 2. 配置触发规则

编辑配置文件中的 `trigger_rules`：

```json
{
  "trigger_rules": [
    {
      "rule_id": "game_helper",
      "name": "游戏助手",
      "enabled": true,
      "keywords": ["明日方舟", "关卡"],
      "message_template": "需要游戏攻略吗？",
      "cooldown_seconds": 300
    }
  ]
}
```

### 3. 测试规则

```bash
curl -X POST http://localhost:8001/proactive_vision/trigger/test \\
  -H "Content-Type: application/json" \\
  -d '{"rule_id": "game_helper"}'
```

## 配置说明

### 系统配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | false | 总开关 |
| `check_interval_seconds` | int | 30 | 检查间隔（10-600秒） |
| `max_fps` | float | 0.5 | 最大截图频率（帧/秒） |
| `analysis_mode` | string | smart | 分析模式（见下文） |
| `quiet_hours_start` | string | "23:00" | 静默开始时间 |
| `quiet_hours_end` | string | "07:00" | 静默结束时间 |
| `pause_on_user_inactive` | bool | true | 用户不活跃时暂停 |
| `inactive_threshold_minutes` | int | 10 | 不活跃阈值（分钟） |

### 分析模式

- **always**: 每次都用AI分析（准确但较慢）
- **smart**: 先规则匹配，不确定时用AI（推荐）
- **rule_only**: 仅使用规则匹配（快速但可能遗漏）

### 触发规则

每条规则包含：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `rule_id` | string | 是 | 唯一标识符 |
| `name` | string | 是 | 规则名称 |
| `enabled` | bool | 否 | 是否启用（默认true） |
| `keywords` | array | 否 | 必须包含的关键词 |
| `absence_keywords` | array | 否 | 不应出现的关键词 |
| `scene_description` | string | 否 | 场景描述（供AI匹配） |
| `message_template` | string | 是 | 消息模板（支持{context}占位符） |
| `cooldown_seconds` | int | 否 | 冷却时间（默认300秒） |

## API接口

### 获取配置

```
GET /proactive_vision/config
```

### 更新配置

```
POST /proactive_vision/config
Content-Type: application/json

{
  "check_interval_seconds": 60,
  "analysis_mode": "always"
}
```

### 启用/禁用

```
POST /proactive_vision/enable
Content-Type: application/json

{
  "enabled": true
}
```

### 获取状态

```
GET /proactive_vision/status
```

返回示例：

```json
{
  "success": true,
  "running": true,
  "enabled": true,
  "last_check": 1709012345.678,
  "last_activity": 1709012340.123,
  "check_interval": 30
}
```

### 测试触发规则

```
POST /proactive_vision/trigger/test
Content-Type: application/json

{
  "rule_id": "game_helper"
}
```

## 预设规则模板

系统提供3个预设规则模板（默认禁用）：

1. **游戏关卡提醒**
   - 检测游戏进入关卡界面
   - 主动询问是否需要攻略

2. **错误检测助手**
   - 检测屏幕错误提示
   - 主动询问是否需要帮助

3. **长时间停留助手**
   - 检测用户在同一界面停留过久
   - 主动询问是否需要指导

## 性能优化

- **截图缓存**：相同帧不重复分析
- **智能调度**：静默时段、用户不活跃时自动暂停
- **频率限制**：可配置最大截图频率
- **异步执行**：不阻塞主对话流程

## 安全性

- ✅ 所有截图本地处理，不上传云端
- ✅ 首次启用需用户明确同意
- ✅ 截图分析后立即释放内存
- ✅ 支持静默时段配置
- ✅ 完全可控的开关

## 故障排查

### 系统未启动

1. 检查配置文件 `enabled` 是否为 `true`
2. 查看agent_server日志：`[ProactiveVision]` 相关日志
3. 调用 `/proactive_vision/status` 检查状态

### 规则未触发

1. 确认规则 `enabled` 为 `true`
2. 检查是否在冷却时间内
3. 检查关键词匹配是否正确
4. 尝试使用 `/proactive_vision/trigger/test` 测试

### MCP调用失败

1. 确认mcp_server正常运行（端口8003）
2. 确认screen_vision服务已注册
3. 检查网络连接

## 开发指南

### 添加自定义规则

编辑配置文件，添加新规则：

```json
{
  "rule_id": "my_custom_rule",
  "name": "我的自定义规则",
  "enabled": true,
  "keywords": ["关键词1", "关键词2"],
  "scene_description": "详细的场景描述，供AI理解",
  "message_template": "检测到{context}，需要帮助吗？",
  "cooldown_seconds": 600
}
```

### 扩展触发器

可以继承 `ProactiveVisionTrigger` 并重写 `_notify_frontend` 方法，实现自定义通知方式（如语音播报、系统通知等）。

## 更新日志

- **v0.1.0** (2026-02-27)
  - 初始版本发布
  - 支持基础调度和规则匹配
  - 集成screen_vision MCP服务

## 许可证

遵循 NagaAgent 主项目许可证

## 支持

如有问题或建议，请在主项目仓库提交Issue。
