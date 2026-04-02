# Claude Code 工作流集成指南

本节介绍如何在任意仓库中集成 Claude Code 工作流，支持通过 `@claude` 触发或在其他工作流中直接调用。

## 概述

可复用工作流（`_claude-code.yml`）提供：
- Claude Code CLI 调用（可读取 skill 和修改代码）
- 白名单检查（组织和仓库）
- 安全检查（组织成员 + 仓库写权限）
- 自动提交代码变更（可选）

## 快速开始

### 方式一：在其他工作流中嵌入调用（推荐）

将以下代码嵌入到你的工作流中：

```yaml
jobs:
  claude-code:
    uses: opensourceways/agent-skills/.github/workflows/_claude-code.yml@main
    secrets: inherit
    with:
      allowed_orgs: 'opensourceways'
      model: 'claude-sonnet-4-20250514'
```

完整参数说明见 [embeddable-caller.yml](./embeddable-caller.yml)。

### 方式二：复制示例工作流

将 [example-caller.yml](./example-caller.yml) 复制到目标仓库：

```bash
mkdir -p .github/workflows
curl -sSL https://raw.githubusercontent.com/opensourceways/agent-skills/main/.github/workflows/example-caller.yml \
  -o .github/workflows/claude-bot.yml
git add .github/workflows/claude-bot.yml
git commit -m "ci: add Claude Code workflow"
git push
```

## 触发方式

| 触发方式 | 说明 |
|---------|------|
| `@claude` 提及 | 在 Issue/PR 评论中包含 `@claude` 时触发 |
| 新建 Issue | 创建新 Issue 时自动触发（无需 @claude） |
| `workflow_call` | 在其他工作流中调用时触发 |

## 参数说明

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `allowed_orgs` | 否 | opensourceways | 白名单组织（逗号分隔） |
| `allowed_repos` | 否 | - | 白名单仓库（逗号分隔，如 org/repo1,org/repo2） |
| `model` | 否 | claude-sonnet-4-20250514 | Claude 模型名称 |
| `timeout_minutes` | 否 | 60 | 超时时间（分钟） |
| `org_name` | 否 | - | 组织成员检查（留空则跳过） |
| `allow_code_change` | 否 | false | 是否允许 Claude 修改代码 |
| `setup_script` | 否 | - | 初始化脚本（shell 命令） |
| `additional_claude_args` | 否 | - | 传给 Claude 的额外参数 |

### 使用 Skill

在调用方的仓库中创建 skill：

```
my-repo/
├── .claude/
│   └── skills/
│       └── my-skill/
│           └── SKILL.md
```

然后在 `additional_claude_args` 中指定：

```yaml
additional_claude_args: '--skill my-skill'
```

## 权限要求

调用方需在 workflow 级别声明以下权限：

```yaml
permissions:
  contents: read          # 读取代码
  pull-requests: write   # 写入 PR 评论
  issues: write          # 写入 Issue 评论
  # 如果 allow_code_change: true，需要：
  # contents: write      # 允许 Claude 修改并提交代码
```

## 安全检查

工作流内置以下安全检查：

1. **白名单检查** - 验证调用仓库在白名单中
2. **组织成员检查** - 触发者必须是目标组织成员
3. **仓库写权限检查** - 触发者需拥有 `write` 或 `admin` 权限
4. **机器人过滤** - 自动跳过 `*[bot]` 和 `dependabot`

## API 密钥管理

`CLAUDE_API_KEY` 由 `opensourceways/agent-skills` 仓库统一管理，通过 `secrets: inherit` 传递给调用方。

调用方无需在自身仓库配置 secrets。

## 故障排查

**问题：工作流不触发**
- 检查评论中是否包含 `@claude`（区分大小写）
- 确认调用仓库在白名单中
- 查看 Actions 页面的工作流运行日志

**问题：白名单拒绝**
- 检查 `allowed_orgs` 和 `allowed_repos` 配置
- 确认仓库名称格式正确（如 `org/repo`）

**问题：`CLAUDE_API_KEY secret is not set`**
- 确认调用方使用了 `secrets: inherit`
- 检查 opensourceways/agent-skills 仓库的 secrets 配置

**问题：Claude 无法修改代码**
- 确认 `allow_code_change: true`
- 确认 workflow 声明了 `contents: write` 权限