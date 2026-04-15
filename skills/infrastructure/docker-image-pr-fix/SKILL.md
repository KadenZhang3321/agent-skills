---
name: docker-image-pr-fix
description: Automatically analyze and fix CI-failed Pull Requests on GitCode/GitHub. Use when a PR has failed CI checks and needs diagnosis and repair. Triggers include "fix this PR", "repair failed CI", "analyze PR failure", or when given a PR URL with CI failures. Works with any Docker-based CI/CD pipeline and automatically creates a new PR with fixes.
---

# Fix Failed CI PR

Automatically diagnose and fix CI failures in Pull Requests, then create a new PR with the solution. Works with GitCode and GitHub repositories using Docker-based CI pipelines.

## Workflow

### 1. Parse Input and Extract Repository Info

Accept PR reference in two formats:
- Full URL: `https://gitcode.com/{owner}/{repo}/pull/{number}`
- PR number only: `{number}` (infers repo from git remotes)

Extract from arguments:
- PR number
- Repository owner and name
- Git platform (GitCode/GitHub)

If only PR number provided, infer from git remotes:

```bash
# Get upstream remote URL
UPSTREAM_URL=$(git remote get-url upstream)
# Example: https://gitcode.com/openeuler/openeuler-docker-images.git
# Parse to extract: owner=openeuler, repo=openeuler-docker-images
```

### 2. Fetch PR Metadata via API

Use platform API to retrieve PR details.

**GitCode API:**
```bash
TOKEN=$(python3 -c "import urllib.parse; line=[l for l in open('/root/.git-credentials') if 'gitcode' in l][0]; token=urllib.parse.urlparse(line.strip()).password; print(token)")
curl -s "https://gitcode.com/api/v5/repos/${OWNER}/${REPO}/pulls/${PR_NUMBER}?access_token=$TOKEN"
```

**GitHub API:**
```bash
TOKEN=$(python3 -c "import urllib.parse; line=[l for l in open('/root/.git-credentials') if 'github' in l][0]; token=urllib.parse.urlparse(line.strip()).password; print(token)")
curl -s -H "Authorization: token $TOKEN" "https://api.github.com/repos/${OWNER}/${REPO}/pulls/${PR_NUMBER}"
```

Extract key information:
- `title`: PR title
- `labels`: Verify failure labels (ci_failed, failing, etc.)
- `head.ref`: Source branch name
- `head.repo.full_name`: Source repository
- `base.ref`: Target branch (master/main)
- `body`: PR description

### 3. Analyze PR Changes

Fetch and examine the source branch:

```bash
# Find the remote for source repository
SOURCE_REMOTE=$(git remote -v | grep "${HEAD_REPO_OWNER}" | head -1 | awk '{print $1}')

# Fetch source branch
git fetch ${SOURCE_REMOTE} "${HEAD_REF}"

# View changed files
git diff upstream/${BASE_BRANCH}...FETCH_HEAD --name-only

# Examine full diff (focus on Dockerfiles)
git diff upstream/${BASE_BRANCH}...FETCH_HEAD
```

### 4. Retrieve CI Failure Logs

Extract CI log links from PR comments:

```bash
# GitCode
curl -s "https://gitcode.com/api/v5/repos/${OWNER}/${REPO}/pulls/${PR_NUMBER}/comments?access_token=$TOKEN&per_page=100"

# GitHub
curl -s -H "Authorization: token $TOKEN" "https://api.github.com/repos/${OWNER}/${REPO}/issues/${PR_NUMBER}/comments?per_page=100"
```

Search for comments containing failure indicators:
- Keywords: `FAILED`, `check_build`, `ci_failed`, `Actions failed`
- Extract Jenkins/GitHub Actions log URLs

Use `WebFetch` to read log content and locate error lines. Focus on:
- First occurrence of `Error:` or `error:`
- Architecture-specific failures (x86_64 vs aarch64)
- Truncated logs (check content before "Content truncated")

### 5. Diagnose Failure Pattern

Analyze the error logs to identify the failure mode:

#### Pattern A: Upstream Binary Package Unavailable

**Symptoms**: Download returns 404, "Not Found" errors

**Verification**:
```bash
curl -sI <package_download_url> | grep "HTTP"
```

**Fix Strategy**: Multi-stage Docker build copying from official image
```dockerfile
ARG VERSION=x.y.z
FROM upstream/official-image:v${VERSION} AS source
FROM base-image:tag
COPY --from=source /path/to/binary /path/to/binary
```

**Validation**:
1. Search DockerHub/Quay for official image
2. `docker pull` and locate binary: `docker run --rm --entrypoint which <image> <binary>`

#### Pattern B: Dependency Compatibility Issues

**Symptoms**: `ImportError`, `AttributeError`, `ModuleNotFoundError`

**Fix Strategy**:
- Pin dependency versions: `RUN pip install package==x.y.z`
- Patch configuration: `RUN sed -i 's/old/new/' script.sh`
- Upgrade/downgrade toolchain

#### Pattern C: CI Infrastructure Issues

**Symptoms**: Error occurs in CI script stage (not Docker build)

**Indicators**:
- Partial architecture success (aarch64 ✓, x86_64 ✗)
- Errors from CI tools themselves (eulerpublisher)

**Fix Strategy**: Comment `/retest` to trigger retry

#### Pattern D: Source Code/Configuration Errors

**Symptoms**: Build errors, syntax errors, configuration format errors

**D1: Missing System Packages**
- **Error**: `command not found: groupadd`, `command not found: make`
- **Fix**: Install required packages
  ```dockerfile
  # Missing groupadd/useradd
  RUN yum install -y shadow-utils

  # Missing make/gcc
  RUN yum install -y make gcc

  # Missing autoconf
  RUN yum install -y autoconf automake
  ```

**D2: Shell Syntax Errors**
- **Error**: Variable expansion issues, command substitution errors
- **Common mistakes**:
  - `$nproc` should be `$(nproc)` for command substitution
  - Unescaped special characters
- **Fix**: Correct shell syntax
  ```dockerfile
  # Wrong
  RUN make -j$nproc

  # Correct
  RUN make -j$(nproc)
  ```

**D3: Dockerfile Logic Errors**
- **Error**: Step ordering issues, path errors, ARG/ENV misuse
- **Fix**: Reorganize Dockerfile structure

### 6. Implement Fix

Create a new branch and apply fixes:

```bash
# Create fix branch based on target branch
git checkout -b fix/<component>-<version> upstream/${BASE_BRANCH}
```

Modify files (common Docker image repository structure):
- `<Category>/<component>/<version>/<base-version>/Dockerfile`
- `<Category>/<component>/<version>/<base-version>/*.yaml`
- `<Category>/<component>/meta.yml`
- `<Category>/<component>/README.md`
- `<Category>/<component>/doc/image-info.yml`

Maintain consistent formatting with other versions in the same directory.

### 7. Commit and Push

```bash
git add <modified_files>

git commit -m "Fix <component> <version> build failure

Fix PR #${ORIGINAL_PR_NUMBER} CI failure: <brief_reason>.

<detailed_fix_description>

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

git push origin fix/<component>-<version>
```

### 8. Create New PR via API

Use platform API to create the fix PR:

```python
import urllib.request, urllib.parse, json

# Read token
with open("/root/.git-credentials") as f:
    for line in f:
        if "gitcode" in line or "github" in line:
            token = urllib.parse.urlparse(line.strip()).password
            platform = "gitcode" if "gitcode" in line else "github"
            break

# Get current user
current_user = $(git config --get user.name)

# Construct API request
if platform == "gitcode":
    api_url = f"https://gitcode.com/api/v5/repos/{owner}/{repo}/pulls"
    data = {
        "access_token": token,
        "title": f"Fix {component} {version} build (fix #{original_pr})",
        "head": f"{current_user}:fix/{component}-{version}",
        "base": base_branch,
        "body": f"{original_body}\n\n## Fix\n{fix_description}"
    }
    headers = {"Content-Type": "application/json", "PRIVATE-TOKEN": token}
else:  # GitHub
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    data = {
        "title": f"Fix {component} {version} build (fix #{original_pr})",
        "head": f"{current_user}:fix/{component}-{version}",
        "base": base_branch,
        "body": f"{original_body}\n\n## Fix\n{fix_description}"
    }
    headers = {"Content-Type": "application/json", "Authorization": f"token {token}"}

req = urllib.request.Request(api_url, data=json.dumps(data).encode(), headers=headers, method="POST")
```

### 9. Verify New PR CI Status

1. Wait 2-3 minutes for CI to start
2. Poll PR comments for CI status
3. If still failing:
   - **CI infrastructure issue**: Comment `/retest`
   - **Code issue**: Return to step 5 for re-analysis

## Failure Pattern Decision Tree

```
CI Failed
├─ Error in CI script stage?
│  ├─ Yes → Pattern C (Infrastructure) → /retest
│  └─ No → Continue
│
├─ Download returns 404?
│  ├─ Yes → Pattern A (Package unavailable) → Multi-stage build
│  └─ No → Continue
│
├─ "command not found"?
│  ├─ Yes → Pattern D1 (Missing package) → yum install
│  └─ No → Continue
│
├─ Shell variable/syntax issue?
│  ├─ Yes → Pattern D2 (Syntax) → Fix syntax
│  └─ No → Continue
│
└─ ImportError / dependency error?
   └─ Yes → Pattern B (Compatibility) → Pin versions/sed fix
```

## Error Message Quick Reference

| Error Message | Pattern | Typical Fix |
|--------------|---------|-------------|
| `404 Not Found` (download failure) | A | Multi-stage build from official image |
| `command not found: groupadd` | D1 | `yum install -y shadow-utils` |
| `command not found: make` | D1 | `yum install -y make` |
| `ImportError: cannot import` | B or C | Check if eulerpublisher issue; else fix deps |
| `$nproc` not expanded | D2 | Change to `$(nproc)` |
| `pip install` compatibility | B | Pin version or sed fix script |
| Single arch failure + eulerpublisher | C | `/retest` |
| `autoreconf: command not found` | D1 | `yum install -y autoconf automake` |

## Handling Special Cases

### Different Architecture Failures

**Both architectures fail**: Indicates code/dependency issue
**Single architecture fails**: Likely CI infrastructure problem

Compare logs from both architectures to identify patterns.

### Log Truncation

Jenkins logs may be truncated due to length. When using WebFetch:
- Focus on lines before "Content truncated"
- Search for keywords: `Error`, `error`, `FAILED`, `命令未找到`
- Check both architecture-specific logs

### Complex Errors Requiring Manual Intervention

If automated diagnosis is inconclusive:
1. Document findings from log analysis
2. Suggest potential approaches
3. Request user decision before implementing fixes

### Shell Variable Expansion

Distinguish between:
- `$var` - Variable reference
- `$(cmd)` - Command substitution
- `${var}` - Variable expansion (recommended, more explicit)

## Prerequisites

### Environment
- Target repository cloned locally
- Git remotes configured:
  - `origin`: Your fork repository
  - `upstream`: Main repository (merge target)

### Credentials
- GitCode/GitHub token stored in `~/.git-credentials`
- Format: `https://username:token@gitcode.com` or `https://username:token@github.com`
- File permissions: 600

### Tools
- `curl`: API requests
- `python3`: JSON parsing and API calls
- `docker`: Image verification (optional)
- `git`: Version control

## Output Format

After completion, output:

```
✅ PR Fix Complete

📋 Original PR: #<number> - <title>
🔍 Root Cause: <root_cause>
🛠️ Fix Strategy: <fix_strategy>

🔗 New PR: #<new_number>
   URL: <pr_url>

⏳ CI Status: <ci_status>
   - x86_64: <status>
   - aarch64: <status>

💡 Suggestion: <next_steps_if_needed>
```

## Success Stories

| PR # | Application | Issue Type | Fix PR | Status |
|------|-------------|------------|--------|--------|
| #1838 | grafana-agent 0.44.7 | Pattern A - RPM unavailable | #1857 | ✅ Success (aarch64 ✓, x86_64 needs retest) |
| #1837 | mlflow 3.9.0 | Pattern D1 - Missing shadow-utils | #1858 | ⏳ CI running |
| #1835 | snort3 3.10.2.0 | Pattern D2 - Shell syntax error | #1859 | ⏳ CI running |

## Important Notes

- **Permissions**: Requires push access to fork repository
- **Token Security**: Ensure `~/.git-credentials` has 600 permissions
- **Parallel Builds**: Different architectures may have different results
- **Automation Limits**: Complex errors may need manual intervention
- **Log Analysis**: Prioritize failed architecture logs; compare both when both fail

## Troubleshooting Tips

### Quick Error Type Identification

1. **Check error stage**:
   - CI script stage (eulerpublisher errors) → Pattern C
   - Docker build stage → Continue diagnosis

2. **Check architecture failure pattern**:
   - Both architectures fail → Code/dependency issue
   - Single architecture fails → Possible CI infrastructure issue

3. **Find key error messages**:
   ```
   command not found     → Missing system package (Pattern D1)
   HTTP 404             → Upstream package unavailable (Pattern A)
   ImportError          → Dependency compatibility (Pattern B)
   syntax error         → Shell/Dockerfile syntax (Pattern D2)
   $variable unexpanded  → Command substitution syntax (Pattern D2)
   ```

### Common Pitfalls

1. **Don't only check the last line**: Real error may be earlier. Look for first `Error:` occurrence.

2. **Watch for log truncation**: Use WebFetch to get critical sections.

3. **Verify fixes before pushing** (optional):
   ```bash
   cd <Dockerfile_directory>
   docker build -t test:local .
   ```
