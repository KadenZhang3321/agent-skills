# Claude Bot 集成指南

本节介绍如何将 Claude Bot 集成到 vllm-project 组织下的任意仓库，
使成员可以通过 Issue/PR 评论中的 `@claude` 触发 AI 响应。

## 前置条件

| 条件 | 说明 |
|------|------|
| 组织成员资格 | 触发者必须是 `vllm-project` 组织成员 |
| 仓库写权限 | 触发者需拥有目标仓库的 `write` 或 `admin` 权限 |
| 认证配置 | `CLAUDE_API_KEY` 由组织级 Secret 统一提供，无需目标仓库单独配置 |
| Token 用量 | 每次调用后自动显示在 Actions Job Summary 中 |

## 快速开始

### 第一步：运行环境配置脚本

在本地执行以下命令为目标仓库创建 `claude-bot` Environment：

```bash
# 需要安装 uv（https://docs.astral.sh/uv/getting-started/installation/）
# 并设置 GH_TOKEN 环境变量（需要 repo 管理权限）

export GH_TOKEN=ghp_your_token_here

# 基础运行（检查并创建 claude-bot environment）
uv run https://raw.githubusercontent.com/opensourceways/agent-skills/main/.github/scripts/setup-claude-environment.py vllm-project/vllm-ascend

# 强制覆盖现有配置
uv run https://raw.githubusercontent.com/opensourceways/agent-skills/main/.github/scripts/setup-claude-environment.py vllm-project/vllm-ascend --force
```

脚本会自动：
- 检查当前用户是否有管理员权限
- 创建或验证 `claude-bot` Environment
- 输出差异对比（若已存在）并建议修复

### 第二步：复制调用方工作流

将 [example-caller.yml](./example-caller.yml) 复制到目标仓库：

```bash
# 在目标仓库中执行
mkdir -p .github/workflows
curl -sSL https://raw.githubusercontent.com/opensourceways/agent-skills/main/.github/workflows/example-caller.yml \
  -o .github/workflows/claude-bot.yml

# 根据实际情况修改配置后提交
git add .github/workflows/claude-bot.yml
git commit -m "ci: add Claude Bot workflow"
git push
```

关键配置项：
```yaml
with:
  model: 'claude-sonnet-4'          # 使用的 Claude 模型
  org_name: 'vllm-project'         # 组织名称（权限检查用）
```

### 第三步：配置必要的 Secrets

**API Key 模式**：在调用方仓库**所在组织**的 **Settings → Secrets and variables → Actions** 中添加组织级 Secret `CLAUDE_API_KEY`，组织内所有仓库通过 `secrets: inherit` 自动继承，无需在每个仓库单独设置。

> 如果调用方是个人仓库（无组织），则在该仓库的 **Settings → Secrets and variables → Actions** 中单独添加 `CLAUDE_API_KEY`。

## 安全说明

Claude Bot 内置三层安全检查，**所有检查均通过**后才会调用模型：

1. **`@claude` 提及检查**：仅当 Issue/PR 评论中包含 `@claude` 时触发（`issue_comment` 事件）
2. **组织成员检查**：触发者必须是目标组织（默认 `vllm-project`）的成员
3. **仓库写权限检查**：触发者必须拥有仓库的 `write` 或 `admin` 权限

此外，工作流会自动跳过机器人账号（如 `dependabot`、`github-actions[bot]`）的触发。

## 如何查看 Token 用量

每次调用后，Token 用量自动显示在对应 Actions 运行的 **Summary** 页面：

1. 前往目标仓库的 **Actions** 页面
2. 点击对应的工作流运行记录
3. 在 **Summary** 标签页查看 Claude Token Usage 表格，包含模型名称、输入/输出/总 Token 数

## 故障排查

**问题：工作流不触发**
- 检查评论中是否包含 `@claude`（区分大小写）
- 确认触发者是组织成员且拥有仓库写权限
- 查看 Actions 页面的工作流运行日志

**问题：`CLAUDE_API_KEY secret is not set`**
- 在仓库 Settings → Secrets 中添加 `CLAUDE_API_KEY`

**问题：Token 用量不显示**
- 前往 Actions → 对应运行记录 → **Summary** 标签页查看
- 若 Claude 调用步骤失败（exit code 1），Token 为 0 属正常，需先解决调用失败的问题

**问题：评论发布失败**
- 检查 `GITHUB_TOKEN` 权限是否包含 `issues: write` 和 `pull-requests: write`
- 确认调用方 workflow 中已正确声明 `permissions`
