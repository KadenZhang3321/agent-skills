---
name: Triton-Ascend Version Upgrade
description: Upgrade Triton-Ascend project based on upstream Triton project. This skill automates the version upgrade process, creates a new branch with upgraded code, and performs compilation and basic functionality tests.
---

# Triton-Ascend Version Upgrade Skill

## Overview
This skill automates the process of upgrading the Triton-Ascend project to a new version based on the upstream Triton project. It handles code synchronization, conflict resolution, compilation, and testing.

## When to use this skill
Use this skill when you need to upgrade Triton-Ascend to a new version from the upstream Triton project.

## Input
- **Version number**: The target version to upgrade to (e.g., v3.2.0, v3.3.0, etc.)

## Output
- A new GitHub branch containing:
  - Upgraded code from upstream Triton
  - Resolved conflicts and compatibility fixes
  - Successfully compiled code
  - Passed basic functionality tests

## Workflow

The upgrade process consists of **two merge phases**:
- **Phase 1**: Merge upstream commit at the point when the release branch was created
- **Phase 2**: Merge subsequent commits from the upstream release branch (bugfixes, etc.)

### Phase 1: Initial Release Branch Merge

#### Step 1: Find Upstream Release Branch Creation Commit
Find the commit ID in the upstream Triton repository where the target release branch was created. This is the first commit we need to merge.

**Actions:**
```bash
# Add upstream remote if not already added
git remote add upstream https://github.com/triton-lang/triton.git
git fetch upstream

# Find the merge base (common parent) between main and the release branch
git merge-base upstream/main upstream/release/{version}
```

This command returns the commit ID where the release branch diverged from main - this is the commit we need to merge in Phase 1.

- Document this commit ID for the merge

**Output:** Save the commit ID to `.claude/skills/triton-upgrade/output/{version}/upstream-release-commit.txt`

**Example:**
```bash
# For release/v3.2.0
COMMIT_ID=$(git merge-base upstream/main upstream/release/v3.2.0)
echo $COMMIT_ID > .claude/skills/triton-upgrade/output/v3.2.0/upstream-release-commit.txt
```

#### Step 2: Create Local Release Branch
Create a new release branch in triton-ascend from the current main branch. The branch name should match the upstream release branch name.

**Actions:**
```bash
git checkout main
git pull origin main
git checkout -b release/{version}
```

**Output:** New branch `release/{version}` created

#### Step 3: First Merge - Release Branch Creation Point
Merge the upstream commit from Step 1 into the new release branch.

**Actions:**
```bash
git merge {upstream-commit-id}
```

**Expected:** Merge conflicts will occur because both triton-ascend and upstream Triton may have modified the same files.

#### Step 4: Resolve Merge Conflicts
Analyze and resolve all merge conflicts from the first merge.

**Actions:**
- Use `git status` to identify conflicted files
- For each conflict:
  - Examine the conflicting changes using `git log` and `git show`
  - Understand the context of both triton-ascend changes and upstream changes
  - Decide how to resolve: keep triton-ascend changes, accept upstream changes, or merge both
  - Document the resolution decision and reasoning
- Mark conflicts as resolved with `git add`

**Output:** Save conflict resolution notes to `.claude/skills/triton-upgrade/output/{version}/phase1-conflicts.md`

#### Step 5: Build and Fix Compilation Errors
Build triton-ascend and resolve any compilation errors.

**Actions:**
```bash
# Build command (adjust as needed)
python setup.py build
# or
pip install -e .
```

- Fix compilation errors one by one
- Document each fix and the reason

**Output:** Save build logs and fixes to `.claude/skills/triton-upgrade/output/{version}/phase1-build.log`

#### Step 6: Basic Functionality Test
Run the most basic operator (add) to verify basic functionality.

**Actions:**
- Create or run a simple test script with an add operator
- Verify the test passes
- Document test results

**Test example:**
```python
import triton
import triton.language as tl

# Simple add kernel test
# [Add test code here]
```

**Output:** Save test results to `.claude/skills/triton-upgrade/output/{version}/phase1-test.log`

#### Step 7: Commit Phase 1 Changes
Commit all changes from Phase 1.

**Actions:**
```bash
git add .
git commit -m "Merge upstream release/{version} creation point

- Merged upstream commit {commit-id}
- Resolved conflicts in [list files]
- Fixed compilation errors
- Verified basic functionality with add operator test"
```

### Phase 2: Merge Release Branch Updates

#### Step 8: Merge Remaining Release Branch Commits
Merge the remaining commits from the upstream release branch (bugfixes and updates after branch creation).

**Actions:**
```bash
# Add upstream remote if not already added
git remote add upstream https://github.com/triton-lang/triton.git
git fetch upstream

# Merge the release branch
git merge upstream/release/{version}
```

**Expected:** Additional merge conflicts may occur.

#### Step 9: Resolve Additional Conflicts
Resolve conflicts from the second merge, similar to Step 4.

**Actions:**
- Identify and resolve all conflicts
- Document resolution decisions

**Output:** Save conflict resolution notes to `.claude/skills/triton-upgrade/output/{version}/phase2-conflicts.md`

#### Step 10: Rebuild and Fix Compilation Errors
Build again and fix any new compilation errors.

**Actions:**
- Run build command
- Fix any new compilation errors
- Document fixes

**Output:** Save build logs to `.claude/skills/triton-upgrade/output/{version}/phase2-build.log`

#### Step 11: Re-test Basic Functionality
Run the add operator test again to ensure functionality still works.

**Actions:**
- Run the same basic test from Step 6
- Verify it passes
- Document results

**Output:** Save test results to `.claude/skills/triton-upgrade/output/{version}/phase2-test.log`

#### Step 12: Final Commit and Push
Commit all Phase 2 changes and push the branch to GitHub.

**Actions:**
```bash
git add .
git commit -m "Complete merge of upstream release/{version}

- Merged all commits from upstream release/{version} branch
- Resolved conflicts in [list files]
- Fixed compilation errors
- Verified basic functionality"

git push origin release/{version}
```

**Output:** GitHub branch `release/{version}` with all upgraded code

## Directory Structure
```
.claude/skills/triton-upgrade/
├── SKILL.md                    # This file
├── scripts/                    # Automation scripts
├── references/                 # Reference documents and guides
└── output/                     # Output files for each upgrade
    └── {version}/              # Version-specific output
```

## Important Notes

### Two-Phase Merge Strategy
This upgrade process uses a two-phase merge approach:
1. **Phase 1**: Merge the upstream commit at the exact point where the release branch was created
2. **Phase 2**: Merge all subsequent commits from the upstream release branch

This approach helps isolate conflicts and makes it easier to understand and resolve issues.

### Conflict Resolution Guidelines
When resolving conflicts:
- **Examine commit history**: Use `git log` and `git show` to understand why each change was made
- **Preserve triton-ascend features**: Keep Ascend-specific modifications unless they conflict with critical upstream changes
- **Document decisions**: Always document why you chose a particular resolution
- **Test after resolution**: Ensure the code compiles and basic functionality works

### Build and Test Requirements
- **Compilation**: Must successfully build without errors
- **Basic test**: The add operator test must pass before proceeding
- **Documentation**: All build logs, test results, and conflict resolutions must be documented

### Output Files
All output files should be saved under `.claude/skills/triton-upgrade/output/{version}/`:
- `upstream-release-commit.txt` - The upstream commit ID for the release branch creation
- `phase1-conflicts.md` - Conflict resolution notes for Phase 1
- `phase1-build.log` - Build logs for Phase 1
- `phase1-test.log` - Test results for Phase 1
- `phase2-conflicts.md` - Conflict resolution notes for Phase 2
- `phase2-build.log` - Build logs for Phase 2
- `phase2-test.log` - Test results for Phase 2

### Branch Naming
- Release branch: `release/{version}` (e.g., `release/v3.2.0`)
- Must match the upstream release branch name

### Success Criteria
The upgrade is considered complete when:
1. All merge conflicts are resolved
2. Code compiles successfully
3. Basic add operator test passes
4. All changes are committed and pushed to GitHub
5. All documentation is complete
