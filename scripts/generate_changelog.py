#!/usr/bin/env python3
"""
生成 ChangeLog 脚本

用法:
    python3 generate_changelog.py <起始commit> <结束commit> [版本号]

示例:
    python3 generate_changelog.py cc85cc458b49efcd07f9c5ef5f3f382545e00292 HEAD "1.1"
    python3 generate_changelog.py v1.0..main "1.2"
"""

import subprocess
import sys
import re
from datetime import datetime


def run_command(cmd):
    """执行shell命令并返回输出"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def get_commits(start_sha, end_sha):
    """获取两个commit之间的所有commit"""
    cmd = f"git log --format='%h %s' {start_sha}..{end_sha}"
    output = run_command(cmd)
    if not output:
        return []
    return output.split('\n')


def get_diff_stats(start_sha, end_sha):
    """获取变更统计"""
    cmd = f"git diff --stat {start_sha}..{end_sha}"
    return run_command(cmd)


def get_commit_details(sha):
    """获取单个commit的详细信息"""
    cmd = f"git show {sha} --stat --format='%ai %s'"
    return run_command(cmd)


def generate_changelog(start_sha, end_sha, version, output_file=None):
    """生成变更日志"""
    
    # 获取commits
    commits = get_commits(start_sha, end_sha)
    if not commits:
        print("未找到commit历史")
        return
    
    # 获取变更统计
    stats = get_diff_stats(start_sha, end_sha)
    
    # 解析commit信息，按功能分组
    features = {
        "新增功能": [],
        "优化改进": [],
        "问题修复": [],
        "其他变更": []
    }
    
    # commit消息关键词映射
    feature_keywords = {
        "新增": "新增功能",
        "优化": "优化改进",
        "修复": "问题修复",
        "解决": "问题修复",
        "bug": "问题修复",
        "fix": "问题修复",
        "适配": "优化改进",
        "完善": "优化改进",
        "补全": "优化改进",
        "流畅": "优化改进",
        "卡顿": "问题修复"
    }
    
    for commit in commits:
        if not commit.strip():
            continue
        
        # 跳过merge commit
        if commit.startswith('Merge'):
            continue
            
        # 分类commit
        categorized = False
        msg = commit
        for keyword, category in feature_keywords.items():
            if keyword in msg:
                features[category].append(msg)
                categorized = True
                break
        
        if not categorized:
            features["其他变更"].append(msg)
    
    # 生成变更日志
    today = datetime.now().strftime('%Y年, %m月%d日')
    
    changelog = []
    changelog.append(f"版本 {version}    （{today}）")
    changelog.append("-" * 30)
    
    # 添加功能新增
    if features["新增功能"]:
        changelog.append("* 新增功能:")
        for item in features["新增功能"]:
            # 去掉commit hash
            msg = re.sub(r'^[a-f0-9]+\s+', '', item)
            changelog.append(f"  - {msg}")
        changelog.append("")
    
    # 添加优化改进
    if features["优化改进"]:
        changelog.append("* 优化改进:")
        for item in features["优化改进"]:
            msg = re.sub(r'^[a-f0-9]+\s+', '', item)
            changelog.append(f"  - {msg}")
        changelog.append("")
    
    # 添加问题修复
    if features["问题修复"]:
        changelog.append("* 问题修复:")
        for item in features["问题修复"]:
            msg = re.sub(r'^[a-f0-9]+\s+', '', item)
            changelog.append(f"  - {msg}")
        changelog.append("")
    
    # 添加其他变更
    if features["其他变更"]:
        changelog.append("* 其他变更:")
        for item in features["其他变更"]:
            msg = re.sub(r'^[a-f0-9]+\s+', '', item)
            changelog.append(f"  - {msg}")
        changelog.append("")
    
    # 添加统计信息
    changelog.append("-" * 30)
    changelog.append("变更统计:")
    changelog.append(stats)
    
    result = '\n'.join(changelog)
    
    # 输出到文件或控制台
    if output_file:
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write('\n\n')
            f.write(result)
        print(f"变更日志已追加到: {output_file}")
    else:
        print(result)
    
    return result


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    start_sha = sys.argv[1]
    end_sha = sys.argv[2]
    version = sys.argv[3] if len(sys.argv) > 3 else "1.0"
    
    generate_changelog(start_sha, end_sha, version)


if __name__ == "__main__":
    main()