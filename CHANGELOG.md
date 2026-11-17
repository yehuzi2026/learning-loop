# 仓库变更记录（只增不减）

## v1.1 — 2026-11-17

- **本次新增**：技能首发开源。`SKILL.md` 定义三层闭环 + 六模式 + 9 条铁律；`references/` 两份操作与判定手册；`scripts/loop.py` 学习档案落盘工具。
- **本次落实改进**（相对 v1.0 基线）：
  - I-6 封面改用**矢量 SVG**（`assets/hero.svg`），GitHub 原生渲染、任意缩放不失真、零生成积分，同时兼作 Social Preview 尺寸（1280×640）。
  - I-7 打 Release 前先跑 `gh release view <tag>` 查重，避免同 tag 重复创建。
  - I-8 仓库内置 `CHANGELOG.md`，版本变更随技能一起分发，不再只留在本地技能目录。
  - I-9 增加 `.github/ISSUE_TEMPLATE`，提升开源协作观感。
- **新踩坑**：WorkBuddy 的 GitHub MCP token 无建仓权限（`403 Resource not accessible by integration`），但本机 `gh` CLI 已登录且带 `repo` scope —— 建仓/推送改走 `gh`，读写文件仍可用 MCP。
- **仓库**：https://github.com/yehuzi2026/learning-loop

## v1.0 — 2026-11-17（基线）

- 来源：2026-10-02 实战（75 技能 → 10 分类 → `workbuddy-skills-hub` → Release v1.0）。
- 固化 I-1~I-5：脱敏规则化 / README 简介也脱敏 / 脚本收拢 / CHANGELOG + rules.json / 私有化分支。
