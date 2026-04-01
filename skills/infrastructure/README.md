# Infrastructure Team Skills

这个目录包含 Infrastructure 团队（技术设施建设团队）专属的 skills。

## 团队职责

Infrastructure 团队负责技术设施建设，包括：

- 基础设施搭建和维护
- DevOps 工具链建设
- CI/CD 流水线优化
- 监控和日志系统
- 容器化和云原生技术

## 目录结构建议

```text
infrastructure/
├── README.md           # 本文件
├── devops/            # DevOps 相关
├── monitoring/        # 监控和告警
├── deployment/        # 部署相关
└── automation/        # 自动化工具
```

## Skills 列表

当前目录下的 skills：

<!-- 在此列出你的 skills，保持更新 -->

| 名字 | 功能 |
| --- | --- |
| [github-action-diagnose](./github-action-diagnose/SKILL.md) | 诊断昇腾 CI GitHub Action 失败，定位基础设施故障与根因 |
| [claude-bot](./claude-bot/claude.md) | GitHub Issues/PR 中响应 `@claude` 的 AI 助手 |

### Github-action-diagnose

#### 使用示例

#### 示例 1：通过 GitHub Actions Job URL 诊断（推荐，精确到单个 Job）

```text
/github-action-diagnose https://github.com/vllm-project/vllm-ascend/actions/runs/23656949484/job/68954806226
```

#### 示例 2：通过 Run URL 诊断（自动分析所有失败 Job）

```text
/github-action-diagnose https://github.com/vllm-project/vllm-ascend/actions/runs/23282406275
```

#### 示例 3：通过 Run ID 诊断

```text
/github-action-diagnose 23282406275
```

---

#### 示例输出 A：基础设施故障（Artifact 上传超时）

```text
# CI 故障诊断报告

**Run**: Nightly-A3 #23656949484
**PR**: vllm-project/vllm-ascend (main)
**时间**: 2026-03-27T21:21:23Z ~ 2026-03-27T21:48:37Z

## 故障一：DeepSeek-V3.1-BF16.yaml (multi-node-deepseek-v3.1)

- **定性**: 环境问题（基础设施）
- **根因**: Upload logs 步骤上传 Artifact 时网络超时，实际测试已成功完成
- **关键标识**: `Failed to CreateArtifact: Unable to make request: ETIMEDOUT`
- **责任方**: 基础设施团队
- **建议**: 重跑；检查 Runner 到 GitHub 的出口网络
```

#### 示例输出 B：代码 Bug

```text
# CI 故障诊断报告

**Run**: PR CI #xxx
**PR**: vllm-project/vllm-ascend#1234 (feature/xxx)
**时间**: ...

## 故障一：e2e-singlecard-light

- **定性**: 代码 Bug（PR 引入）
- **根因**: UnboundLocalError，PR 修改了 import 路径但未处理 ImportError 分支
- **关键标识**: `UnboundLocalError: cannot access local variable 'huggingface_hub'`
- **责任方**: PR 作者
- **建议**: 修改 vllm_ascend/xxx.py，在 except ImportError 分支设置默认值
```

## 团队规范

请在此添加团队特定的规范或约定。

## 联系方式

Infrastructure Team 负责人：[添加联系方式]
