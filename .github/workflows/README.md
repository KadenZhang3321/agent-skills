# Claude Code 工作流集成指南

在任意仓库中集成 Claude Code，通过 `@claude` 触发代码审查，或在 CI 中自动分析 PR。
API Key 集中存储在 `KadenZhang3321/agent-skills`，调用方无需配置。

## 前置条件（每个调用方仓库做一次）

1. 向 agent-skills 管理员申请一个 PAT（`repo` scope）
2. 在调用方仓库添加 Secret：  
   **Settings → Secrets and variables → Actions → New repository secret**  
   - Name: `DISPATCH_TOKEN`  
   - Value: 申请到的 PAT

---

## 快速开始

### 方式一：手动触发（`@claude` 评论）

复制 [example-caller.yml](./example-caller.yml) 到目标仓库：

```bash
mkdir -p .github/workflows
curl -sSL https://raw.githubusercontent.com/opensourceways/agent-skills/main/.github/workflows/example-caller.yml \
  -o .github/workflows/claude-bot.yml
git add .github/workflows/claude-bot.yml
git commit -m "ci: add Claude Bot workflow"
git push
```

使用：在任意 PR 或 Issue 评论区输入 `@claude <你的问题>`，Claude 会自动回复。

---

### 方式二：PR 自动触发

复制 [embeddable-caller.yml](./embeddable-caller.yml) 到目标仓库：

```bash
curl -sSL https://raw.githubusercontent.com/opensourceways/agent-skills/main/.github/workflows/embeddable-caller.yml \
  -o .github/workflows/claude-auto.yml
```

使用：每次 PR 开启或更新时，Claude 自动分析代码并发评论。

---

## 参数说明

在 caller 文件的 `payload` 中配置以下参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `allow_code_change` | `'false'` | `'true'` 允许 Claude 修改文件并直接 commit 到当前 PR 分支；`'false'` 只分析 |
| `skill_name` | `''` | 指定 Skill 路径（见下方说明），留空不使用 |
| `model` | `'claude-sonnet-4-20250514'` | Claude 模型名称 |
| `caller_image` | `''` | 调用方提供的镜像（仅工作流自动触发使用），留空使用 `ubuntu-latest` |
| `verify_command` | `''` | 验证命令（仅工作流自动触发使用），验证失败则不 push 代码 |

### caller_image 示例（仅工作流自动触发）

```yaml
# 调用方提供的镜像，镜像需要预装 Node.js、Git、依赖已安装
'caller_image': 'ghcr.io/caller/project:main',

# 使用 ubuntu-latest（默认）
'caller_image': '',
```

### verify_command 示例（仅工作流自动触发）

```yaml
# 验证命令，验证失败则 job 失败，不 push 代码
'verify_command': 'npm run build && npm test',

# 不验证（默认）
'verify_command': '',
```

> 注意：`caller_image` 和 `verify_command` 仅在 **工作流自动触发**（embeddable-caller.yml）时使用，手动 `@claude` 触发时不传这两个参数。

### allow_code_change 示例

```yaml
# 只审查，不改代码（推荐用于自动触发）
'allow_code_change': 'false',

# 允许改代码，直接 commit 到当前 PR 分支
'allow_code_change': 'true',
```

### skill_name 示例

Skill 按以下顺序查找，优先使用调用方仓库自己的：

1. **调用方仓库**：`.github/skills/<skill_name>/SKILL.md`
2. **agent-skills**：`skills/<skill_name>/SKILL.md`

```yaml
# 使用 agent-skills 内置 Skill
'skill_name': 'infrastructure/github-action-diagnose',
'skill_name': 'infrastructure/docker-image-pr-fix',
'skill_name': 'upstream/vllm-ascend-releasing-note',

# 使用调用方仓库自定义 Skill
# 在调用方仓库创建 .github/skills/my-skill/SKILL.md，然后：
'skill_name': 'my-skill',

# 不使用 Skill
'skill_name': '',
```

agent-skills 内置 Skill 列表见 [skills/](../../skills/)。

### model 示例

```yaml
# 默认（速度与能力均衡，推荐）
'model': 'claude-sonnet-4-20250514',

# 最强模型，适合复杂分析
'model': 'claude-opus-4-20251114',

# 最快，适合轻量任务
'model': 'claude-haiku-4-5-20251001',
```

---

## 白名单管理

允许访问的组织和仓库在 [../.github/allowed-callers.json](../allowed-callers.json) 中配置：

```json
{
  "allowed_orgs": [
    "opensourceways"
  ],
  "allowed_repos": [
    "KadenZhang3321/agent-skills",
    "KadenZhang3321/hello-world"
  ]
}
```

- `allowed_orgs`：整个组织下所有仓库都可以使用
- `allowed_repos`：单独授权某个仓库（不在上述组织内也可以）

新增仓库或组织，修改此文件并合并到 main 即可，无需其他改动。

---

## 工作原理

```
调用方仓库                         agent-skills
─────────────────                 ────────────────────────────────
@claude 评论触发
  └─ example-caller.yml
       └─ 发送 repository_dispatch ──→ _claude-code.yml
                                          1. 白名单校验
                                          2. 用户权限校验
                                          3. 使用 caller_image 创建容器（如未传则用 ubuntu-latest）
                                          4. 安装 Claude Code
                                          5. Checkout 调用方仓库
                                          6. 拉取 PR Diff
                                          7. 构建 Prompt（含 Skill）
                                          8. 调用 Claude（使用集中的 API Key）
                                          9. verify_command 不为空？
                                             ├─ 否 → 直接 push
                                             └─ 是 → 执行验证命令
                                                    ├─ 成功 → push
                                                    └─ 失败 → 不 push
                                          10. 在原 PR/Issue 发布评论
```

---

## agent-skills 需配置的 Secrets

| Secret | 用途 |
|--------|------|
| `CLAUDE_API_KEY` | Anthropic API Key，用于调用 Claude |
| `AGENT_PAT` | PAT（`repo` scope），用于读写调用方仓库、发评论、创建 PR |

---

## 故障排查

**agent-skills Actions 没有触发**
- 检查 `DISPATCH_TOKEN` 是否配置了 `repo` scope（`public_repo` 不够）
- 确认 agent-skills 的 Actions 已开启

**白名单拒绝**
- 在 `allowed-callers.json` 中添加对应的 org 或 repo

**Claude 没有发评论**
- 检查 `AGENT_PAT` 是否有目标仓库的写权限
- 查看 agent-skills Actions 中该次 run 的 `Post comment` 步骤日志

**Token/Cost 显示 N/A**
- 检查 `CLAUDE_API_KEY` 是否正确配置
