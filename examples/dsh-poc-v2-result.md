# omo-bridge DSH 端到端 PoC — v1 根因诊断 + v2 策略

## v1 根因（已定位）

v1 的 Step4「中断」**不是** cordis.patch schema 问题，**不是** subagent 工具未注册，而是：

### qwen3.5:4b 在第 4 轮 tool call 格式退化

对比 session jsonl 的 4 个 assistant/message：

| Step | stopReason | content 结构 | 是否真执行工具 |
|------|-----------|--------------|----------------|
| 1 (Intent Gate) | `toolUse` | `{"type":"tool-call","id":"call_xxx","name":"todo_write",...}` 结构化块 | ✅ dsh 执行了 |
| 2 (todo update) | `toolUse` | 结构化 tool-call 块 | ✅ |
| 3 (Codebase Assessment) | `toolUse` | `{"type":"tool-call","name":"glob",...}` 结构化 | ✅ glob 真调用 |
| 4 (Smart Delegation) | **`stop`** | **只有 `{"type":"reasoning","text":"...我会使用 qwen3.5:4b... {\"name\": \"todo_write\", \"arguments\": {...}}"}`** —— tool call 被写进 reasoning 文本 | ❌ dsh 当最终回复，turn/end completed |

**Step4 时 inputTokens=8855**（v1 system prompt 长 + 3 轮工具结果累积），qwen3.5:4b 在这个上下文长度下把 tool call 退化成了文本输出，没有产出结构化 tool-call block，dsh 因此判定模型回复完成（stop 而非 toolUse），未执行任何工具，session 正常 turn/end。

这与研究者长期记忆一致——qwen 系在长 prompt / 多轮后易出现 tool calling 退化（8/14 压测虽未复现，但那是单轮直测；真实 DSH 多轮 + 长 system prompt 下复现了）。

### 排除的可能
- ❌ cordis.patch schema 错误：tool-subagent 在用户级 cordis.patch 已正确注册（provider spawn, continuable）
- ❌ subagent 工具未启用：cordis.patch.yml 有 tool-subagent + tool-subagent-fork + tool-subagent-control 全启用
- ❌ headless 不支持 spawn：headless 能加载所有工具，是模型没发出结构化 tool-call

## v2 策略

既然根因是模型 tool call 退化（非 adapter 设计缺陷），v2 调整：

1. **精简 prompt**（v1 ~1500 字 → v2 ~400 字）降低 input token，减少退化概率
2. **强化 tool-call 格式指令**：明示「必须结构化 tool-call，绝不要把 JSON 当文本」
3. **改单 agent 直接执行**：不让模型 spawn subagent（subagent 调用更复杂、更易退化），改成 Sisyphus 自己用 tool-fs / tool-str-replace-editor 直接建文件
4. **目标**：端到端闭环到产物——workspace 真出 package.json / src/index.js / tests/index.test.js + npm test 真通过

**降级声明**：subagent 多 agent 委派（Sisyphus spawn Hephaestus）降为 v3。v3 需先解决 tool call 退化（换更稳模型如 my-qwen4b-no-think / 更大模型，或 ollama tool-call 格式优化，或减少上下文长度）。

## v2 验证结果（实测）

**39 个 step，756 行 session**（v1 才 81 行）。核心结论：**v1 的退化问题解决，文件创建端到端闭环成功；测试验证环节被 DSH `tool-pwsh` 本机环境问题阻塞**（非 adapter 问题）。

### 通过项 ✅
1. **无 tool call 退化**——39 个 step 全部 `stopReason=toolUse` + 结构化 tool-call。精简 prompt（~1500字→~400字）+ 强化格式指令完全解决了 v1 的 Step4 退化。
2. **`tool-fs` 真创建 3 个文件**——`write` 工具真实执行，"Created file"：
   - `package.json`（259B，含 `"test": "node --test tests/"` + type module）
   - `src/index.js`（`console.log("Hello, World!")`）
   - `tests/index.test.js`（node:test + execSync，cwd 用了绝对路径，内容正确）
3. **`tool-todo` 续跑**——多次 `todo_write` 状态正确流转（in_progress→completed）。
4. **ultrawork「不完成不停止」契约真实执行**——模型遇到 pwsh 输出干扰从 Step6 死磕到 Step38（19 次重试：换命令、背景作业、`Out-File`、`cmd /c`、拼错 `gwsh` 自纠），**没放弃**。这是真实 runtime 下契约生效的硬证据。

### 卡点 ⚠️
- **`tool-pwsh` 本机环境问题**：每个 pwsh 命令 stderr 都输出 UTF-16 乱码警告（`Windows PowerShell 警告: System.Management.Automation.Runs...`，UTF-16 被当 UTF-8 解析）+ `exit 4294901760`（0xFFFF0000 = 进程被终止）。**所有命令都无法真实执行**，测试验证环节被阻塞。
- 这是 **DSH `tool-pwsh` 的 spawn 环境问题**（PowerShell 启动即失败），不是 omo-bridge adapter 设计缺陷。模型自身已尽力绕开（read 文件验证、背景作业等）。

### v2 结论

| 层 | v1 | v2 |
|----|----|----|
| 大脑层（ultrawork 协议触发） | ✅ | ✅ |
| tool-call 格式稳定性 | ❌ Step4 退化 | ✅ 39 step 无退化 |
| tool-todo 续跑 | ✅ | ✅ |
| tool-fs 真实写文件 | ❌ 未到 | ✅ 3 文件闭环 |
| tool-pwsh 命令执行 | — | ⚠️ 环境阻塞（PowerShell spawn 失败） |

**v2 达成**：端到端闭环到「文件创建」+ 无退化。「跑测试验证」被 DSH tool-pwsh 环境问题阻塞，属环境修复项（v2.1），非 adapter 问题。

### v2.1 修复方向（tool-pwsh 环境问题）
- 排查 PowerShell spawn 失败根因（Execution Policy / profile / dsh tool-pwsh 参数）
- 或改用 DSH 的 `tool-bash`（`@deepseek-ai/dsh-tool-bash` 包存在，bash 通道可能无此问题）
- 修好后重跑验证测试闭环
