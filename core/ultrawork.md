# omo-bridge / core / ultrawork.md — ultrawork 编排协议（平台无关）

> 借鉴 OMO 的 ultrawork 理念：一个词触发，所有 agent 激活，不完成不停止。
> 本文件描述协议本身；各 adapter 负责在本平台落地驱动机制。

## 0. 触发词

用户在输入中包含 `ultrawork` 或 `ulw` → 进入 ultrawork 模式。
默认编排器：**Sisyphus**。

## 1. 四阶段协议

### 阶段 A — Intent Gate（意图门）
在分类或行动前，先解析用户**真实意图**，不只看字面。
- 显式意图：用户明说的目标。
- 隐式意图：从上下文 / 代码库成熟度 / 历史推断的潜在需求。
- 产出：一句「真实意图」陈述，写入 todo 顶部。

### 阶段 B — Codebase Assessment（代码库评估）
动任何一行代码前，先摸清架构。
- 用 Explore / Librarian 子 agent 并行 grep + glob + 读关键文件。
- 产出：架构地图（关键文件、入口、依赖、约定）写入 todo。

### 阶段 C — Smart Delegation（智能委派）
按 **category** 委派子任务，**不指定模型**——category 由 adapter 路由到本平台最优模型。
- 每个子任务带：intent、category、acceptance（验收标准）、subagent_id。
- 委派后不阻塞，可并行起多个子 agent。

### 阶段 D — Independent Verification（独立验证）
**不相信任何子 agent 的自述**。Sisyphus 用独立通道复验：
- 产物是否满足 acceptance。
- 测试 / 诊断是否真的通过（不是 agent 说通过）。
- 失败 → 回到阶段 C 重新委派，不放过。

## 2. todo 持久与续跑（boulder）

- 每轮开始先读 todo（本平台持久化机制：DSH=session state, WorkBuddy=TaskList, Trae=文件）。
- 每步完成立即更新 todo 状态。
- 中断恢复时，从 todo 断点继续，不重头。
- 这是「不完成不停止」的实现基础——状态在 todo 里，不在对话记忆里。

## 3. 不完成不停止（boulder 契约）

- ultrawork 模式下，Sisyphus 不得在任务未达 acceptance 前停止。
- 遇到阻塞：先尝试降级 / 换 category / 拆细，再考虑求助用户。
- 只有显式 acceptance 全部满足，或用户显式中止，才退出 ultrawork。

## 4. 降级约定（诚实声明）

OMO 原生 ultrawork 依赖 54+ 生命周期 hooks（`tool.pre/post`、`session.idle`）做自动注入与续跑。
没有 hook 的平台，ultrawork **降级**为：
- 多轮 prompt 驱动（每轮 Sisyphus 主动推进，而非被动等 hook）。
- todo 持久化由 adapter 用本平台机制承载（见上 §2）。
- 「不完成不停止」靠 Sisyphus 提示词 + adapter 续跑脚本共同保证。

降级版仍是 ultrawork——核心是「解析意图→摸架构→按类别委派→独立验证→不完成不停止」的协议，不是 hook 本身。

## 5. adapter 落地契约

每个 adapter 必须提供：
- [ ] 触发词识别（把 ultrawork 路由到 Sisyphus preset / Skill / rule）
- [ ] todo 持久化载体映射（session state / TaskList / 文件）
- [ ] 续跑入口（用户输入「继续」或重启后能从断点恢复）
- [ ] 子 agent 委派通道（DSH: cordis sub-preset; WorkBuddy: sub-Skill; Trae: 子 rule）
- [ ] 独立验证通道（Sisyphus 能用只读工具复验，不信子 agent）
