# ProactiveVision API 端点审查

## Agent Server (8001) - 10个端点

### 1. `GET /proactive_vision/config`
**用途：** 获取ProactiveVision配置
**是否需要：** ✅ **必需** - 前端配置界面需要读取当前配置
**使用场景：** 用户打开ProactiveVision设置页面

### 2. `POST /proactive_vision/config`
**用途：** 更新完整配置
**是否需要：** ✅ **必需** - 前端配置界面需要保存配置
**使用场景：** 用户修改配置后保存

### 3. `POST /proactive_vision/enable`
**用途：** 快速启用/禁用ProactiveVision
**是否需要：** ⚠️ **可选** - 功能与 `POST /config` 重叠，但提供了便利性
**分析：**
- 重复功能：可以通过 `POST /config` 更新 `enabled` 字段实现
- 但保留此端点的理由：
  - 前端可能只有一个开关按钮，不需要发送完整配置
  - 更语义化：`POST /enable` 比 `POST /config {"enabled": true}` 更直观
**建议：** 保留（便利性 > 冗余性）

### 4. `GET /proactive_vision/status`
**用途：** 获取运行时状态（是否运行、统计信息等）
**是否需要：** ✅ **必需** - 监控和调试需要
**使用场景：**
- 前端显示"ProactiveVision当前状态：运行中/已暂停"
- 健康检查
- 性能监控

### 5. `POST /proactive_vision/trigger/test`
**用途：** 手动测试触发规则（忽略冷却时间）
**是否需要：** ✅ **必需** - 配置验证和调试
**使用场景：**
- 用户添加新规则后测试是否生效
- 调试规则匹配问题
- 开发时验证功能

### 6. `POST /proactive_vision/activity`
**用途：** 更新用户活动时间
**是否需要：** ❌ **可能无用** - 悬浮球模式已暂停主界面
**分析：**
- 原设计：用户在主界面交互时更新活动时间，避免用户离开时仍然分析屏幕
- 当前问题：ProactiveVision只在悬浮球模式运行，此时主界面已不活跃
- 用户活动检测应该基于悬浮球的交互，而非主界面
**建议：**
- **短期：** 保留但不调用（兼容性）
- **长期：** 重新设计用户活动检测机制（基于鼠标/键盘全局事件）

### 7. `POST /proactive_vision/window_mode`
**用途：** 设置窗口模式（classic/ball/compact/full）
**是否需要：** ✅ **必需** - 刚添加，用于悬浮球模式集成
**使用场景：** 前端切换窗口模式时自动通知后端，控制ProactiveVision启停

### 8. `GET /proactive_vision/metrics`
**用途：** 获取性能指标（JSON格式）
**是否需要：** ✅ **必需** - 性能监控和调试
**使用场景：**
- 前端性能仪表板
- 查看差异检测节省率
- 分析AI调用次数和耗时

### 9. `GET /proactive_vision/metrics/prometheus`
**用途：** 获取Prometheus格式的性能指标
**是否需要：** ⚠️ **可选** - 除非有Prometheus监控需求
**分析：**
- 当前项目未集成Prometheus
- 如果未来需要生产监控，此端点有用
- 实现成本低，保留不影响性能
**建议：** 保留（预留扩展性）

### 10. `GET /health/full` (间接相关)
**用途：** 完整健康检查，包含ProactiveVision状态
**是否需要：** ✅ **必需** - 系统诊断
**使用场景：** 启动时检查所有服务是否正常

## API Server (8000) - 5个端点

### 1. `POST /proactive_message`
**用途：** 接收来自ProactiveVision的主动消息（HTTP降级方案）
**是否需要：** ⚠️ **降级方案** - WebSocket正常时不使用
**分析：**
- 当前优先使用WebSocket广播
- HTTP仅作为WebSocket失败时的降级方案
- 提高了系统可靠性
**建议：** 保留（容错机制）

### 2. `POST /ws/broadcast`
**用途：** 触发WebSocket广播（由ProactiveVision调用）
**是否需要：** ✅ **必需** - 主要通知路径
**使用场景：** ProactiveVision通过此端点向所有WebSocket客户端推送主动消息

### 3. `GET /ws` (WebSocket端点)
**用途：** WebSocket连接
**是否需要：** ✅ **必需** - 实时通信基础设施
**使用场景：** 前端建立WebSocket连接，接收实时消息

### 4. `GET /health/full`
**用途：** 完整健康检查
**是否需要：** ✅ **必需** - 系统诊断

### 5. `GET /health/quick`
**用途：** 快速健康检查
**是否需要：** ✅ **必需** - 心跳监控

## 总结

### ✅ 必需端点 (13个)
1. Agent: GET /proactive_vision/config
2. Agent: POST /proactive_vision/config
3. Agent: GET /proactive_vision/status
4. Agent: POST /proactive_vision/trigger/test
5. Agent: POST /proactive_vision/window_mode
6. Agent: GET /proactive_vision/metrics
7. Agent: GET /health/full
8. API: POST /ws/broadcast
9. API: WS /ws
10. API: GET /health/full
11. API: GET /health/quick
12. Agent: POST /proactive_vision/enable (便利性)
13. Agent: GET /proactive_vision/metrics/prometheus (预留扩展)

### ⚠️ 可选端点 (2个)
- Agent: POST /proactive_vision/enable - 与POST /config重复，但更便利
- Agent: GET /proactive_vision/metrics/prometheus - 未集成Prometheus但预留扩展

### ❌ 可能无用端点 (1个)
- Agent: POST /proactive_vision/activity - 悬浮球模式下主界面不活跃

### ⚠️ 降级方案端点 (1个)
- API: POST /proactive_message - WebSocket失败时的HTTP降级

## 优化建议

### 短期（保持兼容性）
1. 保留所有端点不变
2. `/proactive_vision/activity` 标记为 deprecated，前端不调用
3. 添加文档说明各端点用途

### 长期（优化设计）
1. **移除 `/proactive_vision/activity`**
   - 重新设计：基于系统级鼠标/键盘事件检测用户活动
   - 或者：悬浮球交互自动更新活动时间

2. **考虑合并 `/enable` 到 `/config`**
   - 减少端点数量
   - 但需评估前端便利性损失

3. **Prometheus端点**
   - 如果确定不会集成Prometheus监控，可移除
   - 但实现简单，保留成本低

## 最终决策

**建议保留所有端点，仅将 `/proactive_vision/activity` 标记为 deprecated。**

理由：
1. 端点数量合理（15个总计，ProactiveVision相关10个）
2. 每个端点都有明确用途或预留扩展性
3. 移除端点的收益（减少1-2个端点）< 风险（破坏兼容性）
4. 代码维护成本低，不影响性能

**无需删除任何接口。**
