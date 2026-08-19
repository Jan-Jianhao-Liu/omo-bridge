# omo-bridge / adapters / workbuddy — WorkBuddy adapter

把 omo-bridge 的纪律 Agent + ultrawork 挂到 **WorkBuddy**（本 AI 助手平台）原生能力上。

## 为什么 WorkBuddy 适配性其实很好

WorkBuddy 原生就有 OMO 编排所需的全套对应物：

| OMO / DSH 概念 | WorkBuddy 原生等价 | 说明 |
|----------------|-------------------|------|
| `tool-todo`（todo 持久） | `TaskCreate` / `TaskUpdate` / `TaskList` | ultrawork 续跑命脉，原生支持 |
| `tool-subagent`(spawn) | `Agent` 工具（`subagent_type`） | 多 agent 委派，原生支持 |
| `tool-str-replace-editor` | `Edit` | 精确编辑 |
| `tool-fs` / `tool-fs-search` | `Read` / `Write` / `Glob` / `Grep` | 文件操作 + 搜索 |
| `tool-pwsh` / bash | `Bash` / `PowerShell` | 命令执行 |
| `persona`（agent 角色） | `subagent_type`（Explore/Plan/general-purpose） | 角色差异化 |
| Skill 体系 | `SKILL.md`（本文件） | 提示词 + 触发词注入 |

唯一缺的是 OpenCode 式生命周期 hooks，但 ultrawork 可降级为「多轮 prompt 驱动 + TaskCreate 续跑」——而 TaskCreate 续跑正是 WorkBuddy 的原生工作流（本会话就在用）。

## 文件

| 文件 | 作用 |
|------|------|
| `SKILL.md` | WorkBuddy Skill 骨架（触发词 ultrawork + Sisyphus 提示词 + 协议 + category 映射） |

## 安装（TODO，待 WorkBuddy skill 安装机制确认）

本 SKILL.md 设计为可放入 `~/.workbuddy/skills/omo-bridge/` 作为用户级 Skill。安装机制待与 WorkBuddy 的 SkillManage / skill 安装流程校准后补全步骤。

## 诚实声明：与 DSH 版的差异

| 维度 | DSH 版 | WorkBuddy 版 |
|------|--------|--------------|
| ultrawork 续跑 | `tool-todo` + continuable | `TaskCreate/TaskUpdate` + 多轮 prompt |
| 模型路由 | category → ollama model（精确） | category → `subagent_type`（能力档，非精确 model） |
| PoC 状态 | ✅ 5/5 阶段 PASS | 🔨 骨架（未端到端测） |
| 多模态 | 缺 | 待 WorkBuddy 多模态 agent |

## 路线图（WorkBuddy adapter）

- [x] SKILL.md 骨架 + category 映射
- [ ] 安装机制确认 + 步骤
- [ ] 端到端 PoC（在 WorkBuddy 会话跑 ultrawork 任务）
- [ ] model 级路由（待 WorkBuddy 暴露 model 选择）
