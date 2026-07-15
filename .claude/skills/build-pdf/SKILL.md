---
name: build-pdf
description: 重新生成 plan-3 下的新疆自驾攻略 PDF。封装三个 _build_pdf_*.py 脚本,支持 15d / amap / food / combined / all 子命令。用法:/build-pdf <subcommand>。
---

# /build-pdf

重新生成 `plan-3/` 下的新疆自驾攻略 PDF。所有脚本以 `plan-3/` 为 cwd。

## 用法

```
/build-pdf 15d         # 15 天独库版方案(单方案)
/build-pdf combined    # 15 天独库版方案 + 通用信息(默认)
/build-pdf amap        # 高德导航信息 PDF
/build-pdf food        # 按路线美食 PDF
/build-pdf all         # 跑以上全部
```

## 子命令实现

每个子命令对应一个 Python 脚本 + Chrome headless。**直接调脚本,不复制逻辑。**

### `15d` / `combined`

- 脚本:`plan-3/_build_pdf_15d.py`
- 通过 `MODE` 环境变量切换:
  - `MODE=plan` → `15天独库版方案.pdf`
  - `MODE=combined`(默认)→ `15天独库版方案+通用信息.pdf`

```bash
cd /Users/goutian/ai/claude/travel/xinjiang/plan-3
MODE=combined python3 _build_pdf_15d.py
# 或
MODE=plan python3 _build_pdf_15d.py
```

### `amap` / `food`

- 脚本:`plan-3/_build_pdf_amap.py <mode>`
- 参数:`amap` / `food` / `both`(默认)

```bash
cd /Users/goutian/ai/claude/travel/xinjiang/plan-3
python3 _build_pdf_amap.py amap
python3 _build_pdf_amap.py food
python3 _build_pdf_amap.py both
```

### 原始三方案合集(legacy)

- 脚本:`plan-3/_build_pdf.py`
- 输出:`新疆自驾攻略·15天+20天.pdf`

```bash
cd /Users/goutian/ai/claude/travel/xinjiang/plan-3
python3 _build_pdf.py
```

## 已知坑

- 脚本依赖 `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`,Linux/CI 需替换路径
- 临时 HTML 写到 `/tmp/xinjiang*.html`,`Stop` 钩子会提醒清理
- `.pdf` 文件被 `PreToolUse` 钩子保护,直接 Edit/Write 会被阻断 → 应改对应 `.md` 再跑本 skill

## 工作流建议

1. 改 `plan-3/*.md` → 编辑后钩子会提醒重跑
2. `/build-pdf combined` → 重新生成主 PDF
3. `/build-pdf amap` / `food` → 生成专题 PDF
4. 如需对比 15/20 天差异 → `python3 _build_pdf.py`(legacy 路径)

## 不要做的事

- 不要手工改 `*.pdf` 文件 → 钩子会拦截
- 不要 `rm` 带 emoji 的 `.md` 源文件 → 钩子会拦截
- 不要在 `plan-2/` 用本 skill → 那是早期项目,无对应脚本
