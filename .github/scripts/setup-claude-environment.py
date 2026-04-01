#!/usr/bin/env python3
"""
setup-claude-environment.py
============================
为指定仓库创建/验证 GitHub Environment（默认名称 claude-bot），
并配置分支保护规则。

用法：
    uv run https://raw.githubusercontent.com/opensourceways/agent-skills/main/.github/scripts/setup-claude-environment.py <owner/repo> [--force] [--token TOKEN]

示例：
    uv run .github/scripts/setup-claude-environment.py vllm-project/vllm-ascend
    uv run .github/scripts/setup-claude-environment.py vllm-project/vllm-ascend --force
    uv run .github/scripts/setup-claude-environment.py vllm-project/vllm-ascend --token ghp_xxx

依赖：
    requests（标准场景下通过 pip/uv 安装）

# /// script
# requires-python = ">=3.9"
# dependencies = ["requests"]
# ///
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

import requests

# ------------------------------------------------------------------
# 期望的环境配置（可在此处修改默认值）
# ------------------------------------------------------------------
DESIRED_CONFIG: dict[str, Any] = {
    "environment_name": "claude-bot",
    # 受保护分支列表（环境部署规则）
    "protected_branches": ["main", "refs/pull/*/merge"],
    # 等待计时器（分钟），0 表示不等待
    "wait_timer": 0,
    # 是否要求审阅者批准
    "reviewers": [],
    # 是否限制部署分支
    "deployment_branch_policy": {
        "protected_branches": True,
        "custom_branch_policies": False,
    },
}

GITHUB_API = "https://api.github.com"


def get_token(token_arg: str | None) -> str:
    """从参数或环境变量获取 GitHub Token。"""
    token = token_arg or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print(
            "ERROR: GitHub token not found.\n"
            "Provide via --token, GH_TOKEN, or GITHUB_TOKEN environment variable.",
            file=sys.stderr,
        )
        sys.exit(1)
    return token


def github_request(
    method: str,
    path: str,
    token: str,
    json: Any = None,
    expected_statuses: tuple[int, ...] = (200, 201, 204),
) -> tuple[int, Any]:
    """执行 GitHub API 请求，返回 (status_code, response_body)。"""
    url = f"{GITHUB_API}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    resp = requests.request(method, url, headers=headers, json=json, timeout=30)
    if resp.status_code not in expected_statuses:
        print(
            f"  [WARN] {method} {url} -> HTTP {resp.status_code}: {resp.text[:200]}",
            file=sys.stderr,
        )
    body = None
    if resp.content:
        try:
            body = resp.json()
        except Exception:
            body = resp.text
    return resp.status_code, body


def check_admin_permission(repo: str, token: str) -> None:
    """检查当前 token 对应用户是否拥有仓库 admin 权限。"""
    # 获取当前用户
    status, user = github_request("GET", "/user", token)
    if status != 200 or not isinstance(user, dict):
        print("ERROR: Failed to retrieve authenticated user.", file=sys.stderr)
        sys.exit(1)
    username = user["login"]

    # 检查权限
    status, perm = github_request(
        "GET",
        f"/repos/{repo}/collaborators/{username}/permission",
        token,
        expected_statuses=(200, 403, 404),
    )
    if status != 200 or not isinstance(perm, dict):
        print(
            f"ERROR: Cannot check permission for {username} on {repo} (HTTP {status}).\n"
            "Ensure your token has 'repo' scope and you are a collaborator.",
            file=sys.stderr,
        )
        sys.exit(1)

    permission = perm.get("permission", "none")
    if permission != "admin":
        print(
            f"ERROR: You ({username}) have '{permission}' permission on {repo}.\n"
            "Administrator permission is required to manage environments.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"  ✓ Authenticated as {username} with admin permission on {repo}.")


def get_environment(repo: str, env_name: str, token: str) -> dict | None:
    """获取已有 Environment 配置，不存在则返回 None。"""
    status, body = github_request(
        "GET",
        f"/repos/{repo}/environments/{env_name}",
        token,
        expected_statuses=(200, 404),
    )
    if status == 200 and isinstance(body, dict):
        return body
    return None


def create_or_update_environment(
    repo: str,
    env_name: str,
    token: str,
    config: dict[str, Any],
) -> dict:
    """
    创建或更新 GitHub Environment。
    API 文档：https://docs.github.com/en/rest/deployments/environments
    """
    payload: dict[str, Any] = {
        "wait_timer": config.get("wait_timer", 0),
        "reviewers": config.get("reviewers", []),
        "deployment_branch_policy": config.get("deployment_branch_policy"),
    }

    status, body = github_request(
        "PUT",
        f"/repos/{repo}/environments/{env_name}",
        token,
        json=payload,
        expected_statuses=(200, 201),
    )
    if status not in (200, 201) or not isinstance(body, dict):
        print(
            f"ERROR: Failed to create/update environment '{env_name}' (HTTP {status}).",
            file=sys.stderr,
        )
        sys.exit(1)
    return body


def diff_config(existing: dict, desired: dict[str, Any]) -> list[str]:
    """对比现有配置与期望配置，返回差异描述列表。"""
    diffs: list[str] = []

    # 等待计时器
    existing_wait = existing.get("wait_timer", 0)
    desired_wait = desired.get("wait_timer", 0)
    if existing_wait != desired_wait:
        diffs.append(f"  wait_timer: {existing_wait} -> {desired_wait}")

    # 部署分支策略
    existing_policy = existing.get("deployment_branch_policy") or {}
    desired_policy = desired.get("deployment_branch_policy") or {}
    for key in ("protected_branches", "custom_branch_policies"):
        ev = existing_policy.get(key)
        dv = desired_policy.get(key)
        if ev != dv:
            diffs.append(f"  deployment_branch_policy.{key}: {ev} -> {dv}")

    return diffs


def print_environment_summary(env: dict) -> None:
    """打印 Environment 摘要。"""
    name = env.get("name", "?")
    url = env.get("html_url", "")
    policy = env.get("deployment_branch_policy") or {}
    print(f"  Name             : {name}")
    print(f"  URL              : {url}")
    print(f"  Protected branches: {policy.get('protected_branches', False)}")
    print(f"  Custom policies  : {policy.get('custom_branch_policies', False)}")
    print(f"  Wait timer (min) : {env.get('wait_timer', 0)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Create or verify GitHub Environment 'claude-bot' for a repository.\n\n"
            "This script is designed to be used with the vllm-project Claude Bot integration."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "repository",
        help="Target repository in 'owner/repo' format (e.g. vllm-project/vllm-ascend)",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="GitHub Personal Access Token (overrides GH_TOKEN / GITHUB_TOKEN env var)",
    )
    parser.add_argument(
        "--env-name",
        default=DESIRED_CONFIG["environment_name"],
        help=f"Environment name to create/verify (default: {DESIRED_CONFIG['environment_name']})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite existing environment configuration with desired state",
    )
    args = parser.parse_args()

    repo = args.repository
    env_name = args.env_name
    token = get_token(args.token)

    # 覆盖期望配置中的环境名称
    desired = dict(DESIRED_CONFIG)
    desired["environment_name"] = env_name

    print(f"\n{'='*60}")
    print(f"  Claude Bot Environment Setup")
    print(f"  Repository : {repo}")
    print(f"  Environment: {env_name}")
    print(f"{'='*60}\n")

    # 1. 检查管理员权限
    print("[1/4] Checking admin permission...")
    check_admin_permission(repo, token)

    # 2. 检查 Environment 是否已存在
    print(f"\n[2/4] Checking environment '{env_name}'...")
    existing = get_environment(repo, env_name, token)

    if existing:
        print(f"  Environment '{env_name}' already exists:")
        print_environment_summary(existing)

        # 3. 对比差异
        print(f"\n[3/4] Comparing with desired configuration...")
        diffs = diff_config(existing, desired)

        if not diffs:
            print("  ✓ Environment configuration matches desired state. No changes needed.")
            if not args.force:
                print("\nDone.")
                return
        else:
            print("  Differences found:")
            for d in diffs:
                print(d)
            if not args.force:
                print(
                    "\n  To apply these changes, re-run with --force flag:\n"
                    f"    uv run .github/scripts/setup-claude-environment.py {repo} --force"
                )
                sys.exit(0)
    else:
        print(f"  Environment '{env_name}' does not exist. It will be created.")
        print("\n[3/4] Skipping diff (environment not found).")

    # 4. 创建或强制更新
    action = "Updating" if existing else "Creating"
    print(f"\n[4/4] {action} environment '{env_name}'...")
    result = create_or_update_environment(repo, env_name, token, desired)
    print(f"  ✓ Environment '{env_name}' has been {action.lower()}d:")
    print_environment_summary(result)

    print(f"\n{'='*60}")
    print("  Setup complete!")
    print(f"  View at: https://github.com/{repo}/settings/environments")
    print(f"{'='*60}\n")
    print(
        "Next steps:\n"
        f"  1. Copy .github/workflows/example-caller.yml to {repo}/.github/workflows/\n"
        "  2. Set required secrets (CLAUDE_API_KEY or OIDC config, USAGE_PAT)\n"
        "  3. Commit and push to trigger on the next @claude mention\n"
    )


if __name__ == "__main__":
    main()
