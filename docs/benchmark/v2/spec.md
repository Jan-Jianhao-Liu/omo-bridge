# MiniMarkdown — 软件设计规格书（v2 基准实验用）

实现一个 **Markdown → HTML 转换器**（库 + CLI）。以下为完整需求，按此施工，不增不减。

## 1. 项目结构与入口

```
<工作目录>/
├── package.json        # name: minimarkdown；scripts.test: "node --test"
├── src/
│   ├── index.js        # 导出 convertMarkdown(md)
│   └── cli.js          # CLI 入口
├── tests/
│   └── index.test.js   # 你自己的测试（≥10 个用例）
└── README.md           # 简单说明：API 用法 + CLI 用法
```

- 库 API：`convertMarkdown(md: string) → string`（输入 markdown 文本，返回 HTML 字符串，**默认导出或命名导出均可**，但必须能从 `src/index.js` 引入）
- CLI：`node src/cli.js <input.md> [-o <output.html>]`
  - 有 `<input.md>`：读取文件、转换、`-o` 存在则写入文件并打印 `written: <path>`，否则打印 HTML 到 stdout
  - 缺参数：打印用法说明（usage），退出码非 0
  - 输入文件不存在：打印错误信息，退出码非 0

## 2. 支持的语法（验收清单，输出格式已固定）

| 语法 | 输入 | 必须输出 |
|---|---|---|
| 段落 | `hello world` | `<p>hello world</p>` |
| 标题 | `# Hi` / `## Sub` / `### Sub3` | `<h1>Hi</h1>` / `<h2>Sub</h2>` / `<h3>Sub3</h3>` |
| 粗体 | `**bold**`（独立成行） | `<p><strong>bold</strong></p>`（独立行内内容按真实 markdown 语义包裹在段落中） |
| 斜体 | `*it*`（独立成行） | `<p><em>it</em></p>` |
| 行内代码 | `` `code` ``（独立成行） | `<p><code>code</code></p>` |
| 代码块 | ```` ```js\nconst a=1;\n``` ```` | `<pre><code class="language-js">const a=1;</code></pre>` |
| 链接 | `[text](https://x.com)`（独立成行） | `<p><a href="https://x.com">text</a></p>` |
| 图片 | `![alt](img.png)`（独立成行） | `<p><img src="img.png" alt="alt"></p>` |
| 无序列表 | `- a` / `- b` | `<ul><li>a</li><li>b</li></ul>` |
| 有序列表 | `1. a` / `2. b` | `<ol><li>a</li><li>b</li></ol>` |
| 块引用 | `> quote` | `<blockquote>quote</blockquote>` |
| 空行 | 段落间空行 | 段落以空行分隔（不合并） |

## 3. 安全要求（必须）

- 普通文本中的 HTML 特殊字符必须转义：`<` `>` `&` `"` `'`
- 行内代码与代码块内容同样必须转义（防 XSS）——例如输入含 `</script>` 的文本，输出必须是转义后的实体，绝不能原样输出可执行的 HTML
- 链接/图片的 href/src 不强制转义规则，但输出必须是合法的属性值（引号不破坏结构）

## 4. 边界行为

- 空字符串输入 → 输出空字符串（或空段落不可行时返回 `''`）
- CRLF 行尾（`\r\n`）必须正常处理（视为行分隔）
- 未闭合的代码围栏（只有开头的 ```）→ 按代码块处理剩余内容
- 超长行（如 10 万字符单行）不得崩溃
- 链接文本或 URL 含括号/引号时输出结构不被破坏

## 5. 自测要求

- 你自己的 `tests/index.test.js`：≥10 个用例，覆盖验收清单中的每种语法 + 至少 2 个安全转义用例 + 1 个边界用例
- `node --test` 全绿才算完成

## 6. 完成定义

- 上述全部文件存在；`node --test` 全绿；CLI 手动验证一次（示例文件转换输出正确）
- 硬约束：只在指定工作目录内施工；不修改目录外任何文件；不引入第三方依赖（只用 Node 内置模块）

## 7. 最后报告

报告你做了什么（文件清单）、你的测试输出（真实粘贴）、CLI 验证示例（真实输出）。
