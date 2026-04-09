# Claude Code 调用模板

本模板用于调用 [agent-skills](https://github.com/KadenZhang3321/agent-skills) 仓库中的 Claude Code 工作流。

## 前置条件

### 1. 在调用方仓库配置 Secrets

在你的仓库中设置以下 **Secrets**（Settings → Secrets and variables → Actions）：

| Secret 名称 | 说明 |
|-------------|------|
| `CLAUDE_API_KEY` | Anthropic API Key（如果由 agent-skills 集中管理，调用方可不配置） |
| `AGENT_PAT` | 具备 `repo` 权限的 Personal Access Token，用于读写仓库、发布评论、创建 PR |

### 2. 将调用方仓库加入白名单

在 [agent-skills](https://github.com/KadenZhang3321/agent-skills) 仓库的 `.github/allowed-callers.json` 文件中添加你的组织或仓库：

```json
{
  "allowed_orgs": ["your-org-name"],
  "allowed_repos": ["your-org/your-repo"]
}
```

---

## 使用方法

### 方式一：通过 Issue/PR 评论触发（推荐）

在你的仓库中创建一个工作流文件 `.github/workflows/claude-code-trigger.yml`：

```yaml
name: Claude Code Trigger

on:
  issue_comment:
    types: [created]

jobs:
  trigger-claude:
    runs-on: ubuntu-latest
    if: |
      contains(github.event.comment.body, '@claude') &&
      (github.event.issue.pull_request != null || github.event.issue.number != null)
    
    steps:
      - name: Trigger Claude Code
        env:
          GH_TOKEN: ${{ secrets.AGENT_PAT }}
        run: |
          python3 - <<'PYEOF'
          import json
          import os
          import urllib.request

          # 从评论中提取参数
          comment_body = "${{ github.event.comment.body }}"
          
          # 解析 @claude 后面的命令
          # 例如：@claude review this PR 或 @claude fix the bug --skill code-review --allow-code-change
          parts = comment_body.split('@claude', 1)
          if len(parts) < 2:
              print("No command found after @claude")
              exit(0)
          
          command = parts[1].strip()
          
          # 解析参数
          skill_name = ""
          allow_code_change = "false"
          model = ""
          verify_command = ""
          custom_prompt = ""
          
          if "--skill" in command:
              idx = command.find("--skill") + 7
              rest = command[idx:].strip()
              skill_name = rest.split()[0] if rest.split() else ""
          
          if "--allow-code-change" in command or "--allow-code-changes" in command:
              allow_code_change = "true"
          
          if "--model" in command:
              idx = command.find("--model") + 7
              rest = command[idx:].strip()
              model = rest.split()[0] if rest.split() else ""
          
          if "--verify" in command:
              idx = command.find("--verify") + 8
              rest = command[idx:].strip()
              verify_command = rest.split("--")[0].strip() if "--" in rest else rest.strip()
          
          # 提取用户请求（去掉参数部分）
          user_request = command
          for flag in ["--skill", "--allow-code-change", "--allow-code-changes", "--model", "--verify", "--prompt"]:
              if flag in user_request:
                  user_request = user_request.split(flag)[0].strip()
          
          if "--prompt" in command:
              idx = command.find("--prompt") + 8
              custom_prompt = command[idx:].strip()

          # 构建 repository_dispatch payload
          caller_repo = "${{ github.repository }}"
          issue_number = "${{ github.event.issue.number }}"
          pr_number = ""
          
          # 如果是 PR 评论，获取 PR 号
          pr_data = ${{ toJSON(github.event.issue.pull_request) }}
          if pr_data and pr_data.get('url'):
              pr_number = str("${{ github.event.issue.number }}")

          payload = {
              "event_type": "claude-request",
              "client_payload": {
                  "caller_repo": caller_repo,
                  "issue_number": issue_number,
                  "pr_number": pr_number,
                  "comment_body": user_request,
                  "comment_author": "${{ github.event.comment.user.login }}",
                  "skill_name": skill_name,
                  "skill_url": "",
                  "custom_prompt": custom_prompt,
                  "allow_code_change": allow_code_change,
                  "model": model or "claude-sonnet-4-20250514",
                  "verify_command": verify_command,
                  "caller_image": "",
                  "caller_env_vars": "",
                  "dangerously_skip_permissions": "false",
                  "allowed_tools": "",
                  "show_full_output": "false"
              }
          }

          # 发送到 agent-skills 仓库
          req = urllib.request.Request(
              "https://api.github.com/repos/KadenZhang3321/agent-skills/dispatches",
              data=json.dumps(payload).encode(),
              headers={
                  "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
                  "Accept": "application/vnd.github+json",
                  "X-GitHub-Api-Version": "2022-11-28"
              },
              method="POST"
          )
          
          try:
              response = urllib.request.urlopen(req)
              print(f"Triggered successfully! Status: {response.status}")
          except Exception as e:
              print(f"Error triggering: {e}")
              exit(1)
          PYEOF
```

#### 使用示例

在 PR 或 Issue 中评论：

```
@claude Please review this PR and suggest improvements

@claude Fix the bug in the login function --skill bug-fix --allow-code-change

@claude Add unit tests for the auth module --verify "npm test" --allow-code-change

@claude Explain this code --model claude-opus-4-20250514
```

---

### 方式二：手动触发工作流（带输入参数）

创建 `.github/workflows/claude-code-manual.yml`：

```yaml
name: Claude Code Manual Trigger

on:
  workflow_dispatch:
    inputs:
      request:
        description: 'Your request to Claude'
        required: true
        type: string
      skill_name:
        description: 'Skill name (optional)'
        required: false
        type: string
        default: ''
      allow_code_change:
        description: 'Allow Claude to modify code'
        required: false
        type: boolean
        default: false
      model:
        description: 'Model to use'
        required: false
        type: choice
        options:
          - claude-sonnet-4-20250514
          - claude-opus-4-20250514
          - claude-haiku-4-20250514
        default: claude-sonnet-4-20250514
      verify_command:
        description: 'Command to verify changes (optional)'
        required: false
        type: string
        default: ''

jobs:
  trigger-claude:
    runs-on: ubuntu-latest
    
    steps:
      - name: Trigger Claude Code
        env:
          GH_TOKEN: ${{ secrets.AGENT_PAT }}
        run: |
          python3 - <<'PYEOF'
          import json
          import os
          import urllib.request

          payload = {
              "event_type": "claude-request",
              "client_payload": {
                  "caller_repo": "${{ github.repository }}",
                  "issue_number": "",
                  "pr_number": "",
                  "comment_body": "${{ inputs.request }}",
                  "comment_author": "${{ github.actor }}",
                  "skill_name": "${{ inputs.skill_name }}",
                  "skill_url": "",
                  "custom_prompt": "",
                  "allow_code_change": "${{ inputs.allow_code_change }}",
                  "model": "${{ inputs.model }}",
                  "verify_command": "${{ inputs.verify_command }}",
                  "caller_image": "",
                  "caller_env_vars": "",
                  "dangerously_skip_permissions": "false",
                  "allowed_tools": "",
                  "show_full_output": "false"
              }
          }

          req = urllib.request.Request(
              "https://api.github.com/repos/KadenZhang3321/agent-skills/dispatches",
              data=json.dumps(payload).encode(),
              headers={
                  "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
                  "Accept": "application/vnd.github+json",
                  "X-GitHub-Api-Version": "2022-11-28"
              },
              method="POST"
          )
          
          try:
              response = urllib.request.urlopen(req)
              print(f"Triggered successfully! Status: {response.status}")
          except Exception as e:
              print(f"Error triggering: {e}")
              exit(1)
          PYEOF
```

---

### 方式三：在其他工作流中调用

```yaml
- name: Trigger Claude Code
  env:
    GH_TOKEN: ${{ secrets.AGENT_PAT }}
  run: |
    curl -X POST \
      -H "Authorization: Bearer $GH_TOKEN" \
      -H "Accept: application/vnd.github+json" \
      https://api.github.com/repos/KadenZhang3321/agent-skills/dispatches \
      -d '{
        "event_type": "claude-request",
        "client_payload": {
          "caller_repo": "${{ github.repository }}",
          "issue_number": "",
          "pr_number": "",
          "comment_body": "Please analyze this code and suggest improvements",
          "comment_author": "${{ github.actor }}",
          "skill_name": "code-review",
          "allow_code_change": false,
          "model": "claude-sonnet-4-20250514"
        }
      }'
```

---

## client_payload 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `caller_repo` | string | ✅ | 调用方仓库（格式：`owner/repo`） |
| `issue_number` | string | ❌ | Issue/PR 号码（评论触发时填写） |
| `pr_number` | string | ❌ | PR 号码（如果是 PR 评论） |
| `comment_body` | string | ✅ | 用户请求内容 |
| `comment_author` | string | ✅ | 触发者用户名 |
| `skill_name` | string | ❌ | Skill 名称（从 `skills/` 目录加载） |
| `skill_url` | string | ❌ | 远程 Skill 文件 URL |
| `custom_prompt` | string | ❌ | 自定义 prompt（优先级最高） |
| `allow_code_change` | boolean | ❌ | 是否允许修改代码（默认 `false`） |
| `model` | string | ❌ | Claude 模型（默认 `claude-sonnet-4-20250514`） |
| `verify_command` | string | ❌ | 验证命令（代码修改后执行） |
| `caller_image` | string | ❌ | 自定义容器镜像 |
| `caller_env_vars` | string | ❌ | JSON 格式的环境变量 |
| `dangerously_skip_permissions` | boolean | ❌ | 跳过权限检查（谨慎使用） |
| `allowed_tools` | string | ❌ | 允许的工具列表 |
| `show_full_output` | boolean | ❌ | 显示完整输出 |

---

## 注意事项

1. **权限要求**：触发者需要在调用方仓库具有 `write`/`admin`/`maintain` 权限
2. **白名单**：调用方仓库必须在 `allowed-callers.json` 中
3. **PAT 权限**：`AGENT_PAT` 需要 `repo` 完整权限
4. **成本**：Claude API 调用会产生费用，请合理使用

---

## 常见问题

**Q: 如何查看执行结果？**  
A: 执行结果会以评论形式发布到对应的 Issue/PR 中，也可以在 agent-skills 仓库的 Actions 中查看详细日志。

**Q: 如何自定义 Skill？**  
A: 在调用方仓库创建 `.github/skills/<skill-name>/SKILL.md` 或 `.ai/skills/<skill-name>/SKILL.md`，或通过 `skill_url` 指定远程文件。

**Q: 代码修改后如何处理？**  
A: 代码修改会生成 patch 文件并上传为 artifact，同时会在评论中通知。如需自动创建 PR，可在调用方工作流中处理。
