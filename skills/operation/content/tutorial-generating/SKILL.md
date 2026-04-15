---
name: tutorial-generating
description: Transform a folder of unnamed screenshots and a rough markdown draft into a polished, illustrated tutorial document. Use when the user has a set of screenshots (e.g., from Snipaste or other tools) with timestamp-based filenames and a brief markdown outline, and wants to produce a complete step-by-step instructional document with images renamed by content and inserted at appropriate positions. Triggers include "整理截图写文档", "screenshots to tutorial", "rename images and write guide", "把截图整理成教程", or when a folder of screenshots and a markdown draft are provided together.
---

# Tutorial Generating

将一组以时间戳命名的截图和一份粗略的 Markdown 草稿，转化为一份完整的、图文并茂的操作指导文档。自动完成截图内容识别、语义化重命名，以及文档结构补全与图片插入。

## Workflow

### 1. 扫描目标文件夹

列出用户指定文件夹中的所有文件，区分图片文件和文档文件：

```bash
# 列出所有文件
ls -la "<target_folder>/"

# 筛选图片文件（支持 png/jpg/jpeg/gif/webp）
find "<target_folder>" -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.gif" -o -name "*.webp" \) | sort

# 筛选 Markdown 文件
find "<target_folder>" -maxdepth 1 -type f -name "*.md"
```

**输出**：
- 图片文件列表（按文件名/时间排序）
- Markdown 草稿文件路径
- 文件数量统计

### 2. 识别图片内容（OCR）

使用 macOS 系统自带的 Vision 框架进行 OCR 文字识别，提取每张图片中的关键文字信息。

#### 2.1 编译 OCR 工具

创建并编译一个 Swift 小工具，调用 macOS Vision 框架：

```swift
// ocr_images.swift
import Foundation
import Vision
import AppKit

let args = CommandLine.arguments
guard args.count > 1 else {
    print("Usage: ocr_images <image_path>")
    exit(1)
}

let imagePath = args[1]
guard let image = NSImage(contentsOfFile: imagePath),
      let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("ERROR: Cannot load image")
    exit(1)
}

let request = VNRecognizeTextRequest { request, error in
    guard let observations = request.results as? [VNRecognizedTextObservation] else { return }
    for observation in observations {
        if let topCandidate = observation.topCandidates(1).first {
            print(topCandidate.string)
        }
    }
}

request.recognitionLevel = .accurate
request.recognitionLanguages = ["zh-Hans", "en-US"]

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
try handler.perform([request])
```

编译命令：

```bash
swiftc -o ocr_tool ocr_images.swift -framework Vision -framework AppKit
```

#### 2.2 批量 OCR 所有图片

对每张图片执行 OCR，记录识别结果：

```bash
for img in "<target_folder>/"*.png; do
    echo "=== $(basename "$img") ==="
    ./ocr_tool "$img"
    echo "---"
done
```

**关键信息提取**：从 OCR 结果中识别：
- UI 元素（按钮文字、菜单项、对话框标题）
- 关键操作（安装、设置、搜索、选择）
- 上下文信息（应用名称、配置项名称）

### 3. 语义化重命名图片

根据 OCR 识别出的内容，为每张图片生成语义化文件名。

#### 3.1 命名规则

文件名格式：`{序号}-{动作}-{对象}.png`

- **序号**：两位数字，按操作流程顺序排列（`01`、`02`、`03`...）
- **动作**：描述截图中的核心操作（如 `install`、`enable`、`open`、`select`、`create`）
- **对象**：描述操作的目标（如 `copilot-extension`、`agent-skills-setting`）
- 使用英文小写和连字符，不使用空格或中文

**命名示例**：

| OCR 关键内容 | 命名结果 |
|-------------|----------|
| GitHub Copilot 扩展安装页面 | `01-install-copilot-extension.png` |
| 设置搜索 chat.useAgentSkills | `04-enable-agent-skills-setting.png` |
| git clone 命令 | `10-git-clone-agent-skills-repo.png` |
| 资源管理器目录结构 | `11-agent-skills-repo-structure.png` |

#### 3.2 执行批量重命名

使用 Python 脚本进行安全的批量重命名（避免 shell 转义问题）：

```python
import os

base = "<target_folder>"
renames = {
    "<原文件名1>.png": "<新文件名1>.png",
    "<原文件名2>.png": "<新文件名2>.png",
    # ...
}

for old, new in renames.items():
    src = os.path.join(base, old)
    dst = os.path.join(base, new)
    if os.path.exists(src):
        os.rename(src, dst)
        print(f"OK: {old} -> {new}")
    else:
        print(f"SKIP: {old} not found")
```

> **注意**：文件夹路径包含空格时，shell 的 heredoc 和链式 `mv` 命令容易出错。推荐使用 Python 脚本文件而非内联命令。

### 4. 阅读并分析 Markdown 草稿

读取用户提供的 Markdown 草稿，理解其结构和意图：

```bash
cat "<target_folder>/instruction.md"
```

**分析要点**：
- 识别文档主题和目标读者
- 提取关键步骤的概要（通常是简短的要点列表）
- 确定步骤之间的逻辑顺序
- 将草稿中的简略描述与 OCR 识别出的截图内容进行对应

### 5. 补全 Markdown 文档

将草稿扩展为完整的操作指导文档，遵循以下结构规范。

#### 5.1 文档结构模板

```markdown
# [文档标题]

[一段简介，说明文档目的和适用对象]

---

## 前置准备

[列出开始操作前需要满足的条件]

### 1. [准备项1]
[详细说明 + 截图]

### 2. [准备项2]
[详细说明 + 截图]

---

## 步骤 N：[步骤标题]

[简要说明本步骤的目的]

### N.1 [子步骤]
[操作说明]

![图片描述](xx-image-name.png)

### N.2 [子步骤]
[操作说明]

> **说明/提示：** [补充说明]

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| ... | ... |
```

#### 5.2 文档编写原则

- **标题层级**：使用 `#` 到 `####`，层级不超过4级
- **步骤编号**：主步骤使用 "步骤 N"，子步骤使用 "N.1"、"N.2"
- **操作描述**：具体、明确，包含 **UI 路径**（如"点击左下角齿轮图标 → 设置"）
- **关键词加粗**：菜单名、按钮名、配置项用 `**粗体**` 标注
- **代码块**：命令行操作使用 ` ```bash ``` ` 包裹
- **引用提示**：使用 `> **说明：**` 或 `> **注意：**` 添加补充信息
- **分隔线**：主要章节之间使用 `---` 分隔

### 6. 在文档中插入图片

将重命名后的图片以 Markdown 语法插入到文档的对应位置。

#### 6.1 图片插入语法

```markdown
![图片的中文描述](图片文件名.png)
```

#### 6.2 图片放置原则

- **紧跟操作说明之后**：先写文字描述操作步骤，紧接着插入对应截图
- **一图一步**：每个关键操作步骤配一张截图，不堆叠多张
- **描述文字有意义**：`![]()` 中的 alt 文字应准确描述图片内容，方便搜索和无障碍访问
- **按操作流程排列**：图片顺序与步骤顺序严格一致

#### 6.3 图片与步骤对应示例

```markdown
### 2. 安装 GitHub Copilot 扩展

在 VS Code 的扩展市场中搜索 **GitHub Copilot** 并安装：

![安装 GitHub Copilot 扩展](01-install-copilot-extension.png)
```

### 7. 最终检查与输出

完成文档后进行以下检查：

#### 7.1 完整性检查
- [ ] 所有截图均已在文档中引用
- [ ] 文档中所有图片引用的文件名与实际文件名一致
- [ ] 无遗漏的操作步骤

#### 7.2 格式检查
- [ ] Markdown 语法正确（标题层级、列表、代码块等）
- [ ] 图片 alt 文字完整且有描述性
- [ ] 表格格式正确
- [ ] 无多余空行或格式错误

#### 7.3 验证图片引用

```bash
# 提取文档中所有图片引用
grep -oP '!\[.*?\]\(\K[^)]+' "<target_folder>/instruction.md"

# 对比实际图片文件
ls "<target_folder>/"*.png

# 检查是否有孤立图片（未被文档引用）或断链引用（文件不存在）
```

## 处理特殊情况

### 文件夹路径含空格
路径含空格时（如 `skill instruction/`），shell 命令容易出错。应对策略：
- 使用 Python 脚本替代 shell 批量操作
- 所有路径用双引号包裹
- 避免 shell heredoc 内使用复杂路径

### 图片无法 OCR
某些截图可能是纯图形、图标或高度风格化的文字，OCR 无法识别。处理方式：
- 结合图片尺寸和时间戳推断在流程中的位置
- 参照草稿中的步骤描述进行人工匹配
- 使用通用描述命名（如 `05-step5-ui-overview.png`）

### 草稿过于简略
如果草稿仅有几个关键词，需要：
1. 优先依赖 OCR 结果理解完整流程
2. 结合工作空间中的相关文件（README、其他文档）补充上下文
3. 按截图的时间顺序还原操作流程
4. 用行业通用的操作指导文档写法补全

### 非 macOS 环境
Vision 框架仅限 macOS。在其他平台上：
- Linux/Windows：安装 `tesseract` 和 `pytesseract`
- 替代方案：`brew install tesseract`（macOS 备选）或使用在线 OCR API

## 注意事项

- OCR 工具编译后的二进制文件和 Python 重命名脚本属于临时文件，完成后应清理
- 重命名前建议备份原始图片，以防命名出错需要回溯
- 文档中图片路径使用相对路径，确保文档和图片在同一目录下可正常显示
- 对于包含敏感信息的截图（如 token、密码），应在文档中提醒脱敏处理
