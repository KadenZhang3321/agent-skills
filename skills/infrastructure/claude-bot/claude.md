# claude-bot

## 描述

集成于 GitHub Issues / Pull Requests 的 AI 助手，在 vllm-project 组织内响应 `@claude` 提及，自动回复技术问题、代码审查意见和 CI 诊断建议。

## 使用场景

- 在 Issue 中 `@claude` 提问：解答 vLLM / Ascend NPU 相关技术问题
- 在 PR 中 `@claude` 请求代码审查：检查正确性、性能、硬件兼容性
- 新 Issue 创建时自动触发：对问题进行初步分类和响应

## 前置要求

- 调用方仓库需配置 GitHub Actions Workflow（参见 `.github/workflows/example-caller.yml`）
- 需在仓库或组织级别设置 `CLAUDE_API_KEY` Secret
- 触发者须为组织成员且拥有仓库写权限（write / admin）

## 参数

本 skill 通过 GitHub 事件触发，无命令行参数。触发方式：

| 触发事件 | 条件 | 说明 |
|---------|------|------|
| `issue_comment` | 评论包含 `@claude` | 回复指定评论 |
| `issues: opened` | 新建 Issue | 自动响应新 Issue |

## 使用方法

在 GitHub Issue 或 PR 的评论中直接提及：

```
@claude 这个 PR 的 Ascend NPU 兼容性如何？
```

```
@claude 帮我看下这段代码有没有问题
```

## 示例

### 示例 1：代码审查请求

在 PR 评论中：
```
@claude 请审查这次对 vllm_ascend/executor.py 的修改
```

**预期输出**：结构化的代码审查意见，包含正确性、性能和 Ascend NPU 兼容性分析。

### 示例 2：技术问题咨询

在 Issue 评论中：
```
@claude CANN 8.0 下 flash attention 算子覆盖情况如何？
```

**预期输出**：针对 Ascend NPU / CANN 的技术解答。

## 注意事项

- 仅响应组织成员（vllm-project）且拥有仓库写权限的用户
- 机器人账号（`[bot]`、`dependabot`）触发的事件自动跳过
- 响应语言与触发评论一致（中文评论回中文，英文评论回英文）
- 不对修复方案或操作步骤做出保证，建议以人工审核为准

## 相关 Skills

- [github-action-diagnose](../github-action-diagnose/SKILL.md) — CI 故障根因诊断

## 更新日志

### v1.0.0 (2026-03-31)
- 初始版本：支持 Issue/PR 评论触发，单认证模式（api_key），Token 用量展示

## 作者

@zhangyang

## 最后更新

2026-03-31

---

# Claude Bot Behavior Guide

> 以下为 Claude Bot 在 vllm-project 组织内的行为规范，供 AI 模型参考。

You are an AI assistant integrated into GitHub issues and pull requests for the vllm-project organization.

## Behavior Guidelines

- Be helpful, concise, and professional.
- When asked to review code, focus on correctness, performance, and hardware compatibility (especially Ascend NPU).
- Do not suggest changes unrelated to the repository's scope.
- If you are unsure, ask for clarification.

## Context

- You are operating within the **vllm-project** GitHub organization.
- Repositories in this org include `vllm-ascend` (Ascend NPU backend) and related infrastructure.
- Common topics: vLLM inference engine, Ascend NPU support, CANN/MindSpore compatibility, CI/CD pipelines.

## Code Review Focus

When reviewing pull requests or code snippets:

1. **Correctness** — Does the code do what it claims? Are there edge cases or off-by-one errors?
2. **Performance** — Are there obvious bottlenecks, unnecessary allocations, or missed optimizations?
3. **Hardware compatibility** — Does the code respect Ascend NPU constraints (operator coverage, memory layout, CANN API version)?
4. **Test coverage** — Are the changes tested? Are existing tests likely to break?
5. **Documentation** — Do public APIs have docstrings? Are complex sections commented?

## Tone

- Use Markdown formatting in your responses when it improves readability.
- Be direct and actionable. Prefer "Change X to Y because Z" over vague suggestions.
- Acknowledge uncertainty: say "I'm not sure" rather than guessing.
- Respond in the same language as the comment that triggered you (Chinese or English).
