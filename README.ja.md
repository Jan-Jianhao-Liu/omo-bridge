<div align="center">

# omo-deepseek-harness

**oh-my-openagent（OMO）のディシプリン・エージェント編成を DeepSeek Harness へ。**

[English](README.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md)

</div>

## これは何？

`omo-deepseek-harness` は [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent)（OMO）の **ディシプリン・エージェント + マルチモデルルーティング + ultrawork** という哲学を [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)（DSH）に運ぶ、軽量で独立実装されたアダプタです（**CC0-1.0** パブリックドメイン）。

`ultrawork` と入力するだけで、Sisyphus が編成を開始します：意図解析 → コードベース評価 → カテゴリ別委任 → 独立検証。完了するまで止まりません。

## 特徴

- **一言トリガー** — `ultrawork`（または `ulw`）と入力するだけで、Sisyphus がタスクを完了まで推進します。
- **ディシプリン・エージェント委任** — プリ登録されたロール・サブエージェント（`subagent_hephaestus` / `subagent_explore` / `subagent_oracle`）を DSH ネイティブの `tool-subagent` 上で利用。
- **ultrawork 4 フェーズプロトコル** — 意図ゲート → コードベース評価 → カテゴリ別スマート委任 → 独立検証。
- **完了まで止まらない契約** — `tool-todo` / `tool-goal` による Todo 永続化で再開；中断後もチェックポイントから続行。
- **エンジンの再発明なし** — DSH のネイティブ機能の上に載せる薄いアダプタであり、新しいオーケストレーションランタイムではありません。

## 帰属（Attribution）

[oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent)（作者 [code-yeongyu](https://github.com/code-yeongyu)、**SUL** ライセンス）に着想を得ています。

- 本プロジェクトは OMO のソースコードを**一切使用していません**。アーキテクチャの*理念*（ディシプリン・エージェント / カテゴリルーティング / ultrawork プロトコル）をゼロから再実装しています。
- エージェント名（Sisyphus、Hephaestus、Prometheus ...）は概念的なオマージュとして使用しています。
- OMO の完全な能力（11 エージェント + 54 hooks + Hashline + Team Mode）が必要な場合はオリジナルを：`bunx oh-my-openagent install`（OpenCode ホストが必要）。

## なぜ OMO をそのまま使わないのか？

**OMO は DeepSeek Harness をネイティブにサポートしていません。** OMO は OpenCode プラグインであり、その中核価値は OpenCode の 54+ ライフサイクルフック、ツール呼び出しチャネル、セッション/ToDo 永続化に依存しています——DSH には等価物がありません。OMO をそのまま移植するのは実質リライトであり、SUL + CLA の制約も受けます。

本プロジェクトは「頭脳」（エージェント定義 + カテゴリルーティング + ultrawork プロトコル）だけをプラットフォーム非依存の `core/` に抽出し、DSH のネイティブ能力（`tool-subagent` / `tool-todo` / `tool-goal` ...）にマッピングする薄いアダプタを加えたものです——**エンジンの再発明はしません**。

## アーキテクチャ

```
omo-deepseek-harness/
├── core/                  # プラットフォーム非依存の「頭脳」
│   ├── agents.yaml        # 11 ディシプリン・エージェント（role / category / needs_tools / desc）
│   ├── categories.yaml    # タスクカテゴリ → モデル能力要件
│   ├── prompts/           # エージェントシステムプロンプト（{{platform_tools}} プレースホルダ）
│   └── ultrawork.md       # ultrawork プロトコル：4 フェーズ + ToDo 継続 + 完了まで止まらない
├── adapters/dsh/          # DeepSeek Harness アダプタ（薄層）
│   ├── ultrawork-trigger.md      # クイックエントリ：DSH セッションに貼り付けて Sisyphus を起動
│   ├── AGENTS.md                 # Sisyphus プロンプト：~/.dsh/AGENTS.md にコピー（ホットリロード）
│   ├── category-model-map.yaml   # category → deepseek-v4-flash ルーティング
│   └── cordis.patch.yml          # 任意：OMO ロール・サブエージェントツール（スキーマ校正済み）
└── docs/architecture.md   # 設計判断 + OMO 機能デグラデーションマップ
```

## クイックスタート（DSH）

前提：DSH インストール済み（`DSH_HOME=~/.dsh`）、デフォルトエージェントモデル `deepseek-v4-flash`、`~/.dsh/cordis.patch.yml` でコアツール（`tool-fs` / `tool-todo` / `tool-subagent` ...）有効。

### インタラクティブ

```bash
dsh    # または dsh-web

# adapters/dsh/ultrawork-trigger.md の内容（--- の間）をセッションに貼り付け、次に：
#   ultrawork build a Node.js hello-world project in ./demo, write tests, run them
```

### Headless（自動化 / CI）

```bash
"$DSH" --profile headless "タスク"
```

## ライセンス

**CC0 1.0 Universal（パブリックドメイン）** — [LICENSE](./LICENSE) 参照。著作権者を主張せず、帰属も不要です。

本プロジェクトは oh-my-openagent のソースコードを含みません。oh-my-openagent の全権利は原作者に帰属し、SUL ライセンスの下で提供されます。
