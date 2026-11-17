# 👝 learning-loop · 学习闭环·六能力加速器

> **六个名词不是六个并列功能，是三层闭环 + 一条回流线。**
> 解决的不是「讲得清楚」，是「当场懂了、隔周忘了、还以为自己会了」。

<p align="center">
  <img src="https://img.shields.io/badge/platform-WorkBuddy%20%2F%20CodeBuddy-9cf" alt="platform">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="license">
  <img src="https://img.shields.io/badge/lang-%E4%B8%AD%E6%96%87-red" alt="lang">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="version">
  <img src="https://img.shields.io/badge/python-%E7%BA%AF%E6%A0%87%E5%87%86%E5%BA%93-blue" alt="python">
</p>

---

## 为什么做这个

大多数学习法只管两件事之一：把内容讲清楚，或者让人当场搞懂。

真正常见的失效是：**当场懂了 → 隔周忘了 → 还以为自己会了**。

这个技能把六个能力组织成一条闭环，并用磁盘档案兜底——卡点不会随对话消失，下一轮任务按卡点动态重排，还强制加上间隔复习和硬通过线。它不是「六个提示词」，是一套能真跑起来的学习机制。

---

## 三层闭环

| 层 | 能力 | 职责 |
|---|---|---|
| 第一层 · 加速进场 | ① 学习曲线破坏者、④ 个人学习路径 | 决定「这一步做什么」，跳过铺垫、按卡点动态排程 |
| 第二层 · 暴露真实卡点 | ② 真实错误模拟器、③ 困惑破碎机、⑤ 隐藏漏洞检测器 | 把「不会」和「以为会了」都逼出来 |
| 第三层 · 输出验证 | ⑥ 强制费曼方法 | 用输出倒逼输入，给通过线 |
| 回流 | ⑥ 讲不下去的地方 → 回写 ④ | 重排下一轮，形成越学越快的闭环 |

右侧那条回流线是整个机制的关键：**讲不下去的地方必须回写并重排下一轮任务**，否则六项就只是六个一次性动作。

---

## 六项能力

| # | 能力 | 实质 | 做到位的标志 |
|---|---|---|---|
| ① | 学习曲线破坏者 | 反「先学完再做」，直接给最小完整任务，缺什么补什么 | 10 分钟内产出过一个能用的东西 |
| ② | 真实错误模拟器 | 用真实失败案例构造「看着对其实错」的现场，先错再归因 | 说得出错在哪个前提，不是只记住正确答案 |
| ③ | 困惑破碎机 | 对「我不懂 X」连续追问，定位断掉的那层前提，只补最小一块 | 学习者自己能说出「我卡的其实是……」 |
| ④ | 个人学习路径 | 按暴露的漏洞重排优先级，不是固定大纲 | 每轮结束后下一轮任务会变 |
| ⑤ | 隐藏漏洞检测器 | 用变式、反向提问、边界条件、换场景迁移戳破流畅性错觉 | 能区分「认得出来」和「能自己生成」 |
| ⑥ | 强制费曼方法 | 禁用术语、不查资料，讲给外行；卡住处立即回炉 | 不经提示讲通，且答对一次变式题 |

**诊断单通道**：用户明说不懂只走 ③，自认懂了只走 ⑤。③ 与 ⑤、② 与 ⑤ 功能有重叠，同轮双开只会重复追问同一件事。

---

## 原设计补齐的两块

| 缺口 | 补齐方式 |
|---|---|
| 只管「当场搞懂」，没有留存 | 通过后进入 1 / 3 / 7 / 14 天间隔复查，任一档失败退回 `open`，失败次数上浮优先级 |
| 只有方法，没有通过分数线 | T1~T4 四条硬判定：不查资料 / 不用术语 / 换场景能讲通 / 过一道变式题，四条全过才判通过 |

---

## 安装

把整个技能文件夹复制到 WorkBuddy 用户级技能目录，重启即可：

```bash
# Windows
xcopy learning-loop  "%USERPROFILE%\.workbuddy\skills\learning-loop\" /E /I
# macOS / Linux
cp -r learning-loop  ~/.workbuddy/skills/
```

---

## 怎么触发

直接对 WorkBuddy 说：

- 「我要学 X」「教我 X」「带我啃 X」
- 「检查我是不是真懂」「我好像懂了」「考我」
- 「费曼一下」「用大白话讲」
- 「我卡住了」「我不懂 X」
- 「我的学习路径」「下一步学什么」「继续学」
- 「复习」「学习闭环」

---

## 状态落盘

`scripts/loop.py` 纯 Python 标准库，档案默认写在技能目录的 `state/learning.json`，可用 `--state <路径>` 覆盖。

```bash
python scripts/loop.py init   --topic "主题" [--goal "目标"]
python scripts/loop.py add    --topic "主题" --text "卡点" --source "②" [--note "归因"]
python scripts/loop.py pass   --topic "主题" --gap 3
python scripts/loop.py due    [--topic "主题"]
python scripts/loop.py review --topic "主题" --gap 3 --result ok|fail
python scripts/loop.py next   --topic "主题"
python scripts/loop.py show   [--topic "主题"]
python scripts/loop.py check
```

- `init` 遇到已有主题自动续作，不覆盖。
- `add` 返回卡点编号，后续 `pass` / `review` 都用这个编号。
- `pass` 只把「声称通过」落盘，**判定权在流程，不在脚本**。
- `check` 校验档案结构、编号唯一、状态合法、日期格式。

---

## 目录结构

```
learning-loop/
├── SKILL.md                        # 主流程、六模式细则、9 条铁律
├── references/
│   ├── 六模式操作手册.md            # 每个模式的开场白与输出模板
│   └── 判定标准与红线.md            # T1~T4、错误四级来源、留存排程、常见误判
├── scripts/
│   └── loop.py                     # 档案落盘工具（纯标准库）
└── state/
    └── learning.json               # 运行后自动生成，不入库
```

---

## 🔴 硬红线

1. 一次只问一个问题，先自己查再问。
2. 诊断单通道：明说不懂 → ③；自认懂了 → ⑤。
3. **真实错误不许现编**——只能取自用户真实产出、用户复盘、可核验历史错误、给出处的公开案例；四级都取不到就先做真实任务从产出里取错，或明确标注「构造练习题」。
4. T1~T4 四条全过才判通过，不接受「大概懂了」。
5. 卡点必须落盘，结论只活在对话里 = 下次从零开始。
6. 不替用户答、不替用户圆。
7. 中文优先，术语出现即打断。
8. 只增不减，不删历史卡点。
9. 通用不绑定领域，不内置行业题库。

---

## 许可证与作者

MIT License，详见 [LICENSE](LICENSE)。

- 维护者：叶徐刚（乾坤袋）
- 公司：武汉宏刚行科技发展有限公司
- GitHub：[@yehuzi2026](https://github.com/yehuzi2026)
- 同系列技能库：[workbuddy-skills-hub](https://github.com/yehuzi2026/workbuddy-skills-hub)（75 个中文实战技能）

---

⭐ 如果这个技能对你有用，点个 Star 就是最好的鼓励。
