#!/usr/bin/env python3
"""Script to analyze commits and categorize them for release notes."""

import re
import csv

def extract_pr_number(title):
    """Extract PR number from commit title."""
    match = re.search(r'#(\d+)', title)
    return match.group(1) if match else ""

def categorize_commit(title):
    """Categorize commit based on title patterns."""
    title_lower = title.lower()

    # Ignore patterns
    ignore_patterns = [
        r'\[ci\](?!.*nightly)',  # CI changes (except nightly)
        r'\[test\].*ut',  # Unit test only
        r'\[ut\]',  # Unit test
        r'bump actions/',  # GitHub actions bumps
        r'revert',  # Reverts
        r'\[misc\].*clean',  # Cleanup
        r'\[refactor\](?!.*user)',  # Pure refactoring
        r'fix.*test',  # Test fixes
        r'cleanup',  # Cleanup
        r'\[lint\]',  # Lint
    ]

    for pattern in ignore_patterns:
        if re.search(pattern, title_lower):
            return "Ignore", "Internal/CI/test change"

    # Highlights patterns
    if any(keyword in title_lower for keyword in [
        'pd disaggregation', 'disaggregated-prefill', 'encoder separation',
        'kv cache offload', 'ucm', 'mooncake', 'kv pool',
        'full_decode_only', 'full graph', 'aclgraph',
        'mtp', 'eagle', 'speculative', 'suffix', 'rejection sampler',
        'pcp', 'dcp', 'context parallel', 'sequence parallel',
        'quantization.*w8a8', 'quantization.*w4a8', 'mxfp8',
        'eplb', 'dynamic eplb',
        'xlite', 'npugraph_ex',
        'pooling', 'cross-attention', 'whisper',
        'kv-sharing', 'kv nz',
    ]):
        return "Highlights", "Major feature"

    # Model support
    if any(keyword in title_lower for keyword in [
        'qwen3-next', 'qwen3-vl', 'qwen2.5-omni', 'qwen2-audio',
        'deepseek-v3', 'deepseek-r1', 'deepseek v3.2',
        'glm-4', 'glm4', 'internvl', 'hunyuan',
        'pangu', 'longcat', 'minimax', 'paddleocr',
        'kimi-k2',
    ]):
        if '[doc]' in title_lower or 'tutorial' in title_lower:
            return "Documentation", "Model tutorial"
        return "Highlights", "Model support"

    # Hardware and Operator Support
    if any(keyword in title_lower for keyword in [
        'a2', 'a3', 'a5', '310p', '950', 'ascend950',
        'custom op', 'operator', 'triton', 'kernel',
        'flash_attention', 'fused', 'fusion',
        'mlapo', 'sfa', 'fia',
    ]):
        if 'fusion' in title_lower or 'fused' in title_lower:
            return "Performance", "Operator fusion"
        return "Hardware and Operator Support", "Operator/hardware support"

    # Performance
    if any(keyword in title_lower for keyword in [
        '[perf]', 'performance', 'optim', 'improve.*performance',
        'async', 'overlap', 'multi-stream', 'flashcomm',
    ]):
        return "Performance", "Performance optimization"

    # Dependencies
    if any(keyword in title_lower for keyword in [
        'upgrade.*cann', 'upgrade.*torch', 'upgrade.*vllm',
        'torch-npu', 'torch_npu', 'triton-ascend',
        'mooncake.*version', 'ray.*version',
        'transformers.*version', 'upgrade.*version',
        'dependency', 'dependencies',
    ]):
        return "Dependencies", "Dependency update"

    # Breaking changes
    if any(keyword in title_lower for keyword in [
        'breaking', 'deprecat', 'drop.*support',
        'remove.*scheduler', 'drop.*scheduler',
    ]):
        return "Deprecation & Breaking Changes", "Breaking change"

    # Documentation
    if any(keyword in title_lower for keyword in [
        '[doc]', 'documentation', 'tutorial', 'readme',
        'user guide', 'developer guide',
    ]):
        return "Documentation", "Documentation update"

    # Features
    if any(keyword in title_lower for keyword in [
        '[feat]', '[feature]', 'support', 'add.*feature',
        'enable', 'implement',
    ]):
        return "Features", "New feature"

    # Bugfixes
    if any(keyword in title_lower for keyword in [
        '[bugfix]', '[fix]', 'fix.*bug', 'fix.*error',
        'fix.*issue', 'fix.*accuracy',
    ]):
        return "Others", "Bug fix"

    return "Others", "Miscellaneous"

def analyze_commits(input_file, output_file):
    """Analyze commits and write to CSV."""
    with open(input_file, 'r') as f:
        lines = f.readlines()

    commits = []
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Use the line as-is (no "- " prefix in this format)
        title = line

        pr_number = extract_pr_number(title)
        category, reason = categorize_commit(title)
        decision = "Ignore" if category == "Ignore" else "Include"

        # Generate user-facing impact
        impact = title.split('(#')[0].strip() if '(#' in title else title

        commits.append({
            'title': title,
            'pr_number': pr_number,
            'user_facing_impact': impact,
            'category': category,
            'decision': decision,
            'reason': reason
        })

    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['title', 'pr_number', 'user_facing_impact', 'category', 'decision', 'reason']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(commits)

    # Print summary
    category_counts = {}
    for commit in commits:
        cat = commit['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1

    print(f"Total commits: {len(commits)}")
    print("\nCategory breakdown:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

if __name__ == '__main__':
    input_file = '0-current-raw-commits.md'
    output_file = '1-commit-analysis-draft.csv'
    analyze_commits(input_file, output_file)
