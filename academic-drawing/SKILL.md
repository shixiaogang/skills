---
name: academic-drawing
description: 为论文、教材和技术报告设计、生成、修订和评审静态科研图片。框架图走"图像模型出设计稿 → TikZ 还原（必要时裁剪或嵌入模型片段）→ 评审"的串联流水线；定量数据图用 Matplotlib；不用于正文写作、交互式仪表盘或伪造实验影像。
---

# 科技绘图

本 skill 按**数据图 vs 框架图**两类组织。框架图使用统一的视觉语言（见 [diagram-visual-style](references/diagram/diagram-visual-style.md)）。

- **数据图**（chart）：定量编码，Matplotlib 路径。详见 [references/chart/](references/chart/)。
- **框架图**（diagram）：架构、流程、对照、神经网络等解释图，走"**图像模型设计 → TikZ 还原 → 评审**"流水线。

## 框架图流水线

```
事实 + 视觉要求 + 参考图
        │
        ▼
   ① 图像模型出设计稿           ← diagram-model
   （prompt + PNG，构图自由）
        │
        ▼
   ② TikZ 还原                  ← diagram-tikz
   （对照设计稿重建矢量；
     无法实现的部分裁剪设计稿
     或请模型补生成局部，
     以图片形式嵌入 TikZ）
        │
        ▼
   ③ 评审                       ← diagram-review
   （科学 / 读者 / 视觉三通道）
```

**路径说明**：

- **① 图像模型只做设计**：拿事实清单、视觉风格、参考图喂模型，让模型自主决定构图、分组节奏、色彩比例。输出 PNG 作为**设计稿**，不是最终交付图。
- **② TikZ 还原是主交付**：对照设计稿按本 skill 视觉语言（Lancet 2024-07 调色板、思源黑体 Medium + 霞鹜文楷、细 Latex 大头箭头）重建成矢量图。保证可编辑、可嵌入 LaTeX、字体正确嵌入。
- **TikZ 搞不定的部分允许混合**：复杂插画、手绘风机制示意、不规则曲面、复杂图标用 TikZ 画会很笨拙 → 从设计稿**裁剪**该区域，或请模型**单独生成一张**该元素，以 `\includegraphics` 形式嵌入 TikZ 版面；外壳结构（节点、连线、文字、分组）仍用 TikZ 维护。
- **样式对齐**：TikZ 还原必须符合设计稿的样式气质。调色板、字重、节点形态、箭头粗细、留白节奏都要和设计稿一致，不是另起一套"学术线稿"。

## 数据图路径

数据图始终走 Matplotlib：保留数据、代码与真实矢量输出。详细 [chart-draw](references/chart/chart-draw.md)；评审 [chart-review](references/chart/chart-review.md)。

## 流水线详细步骤

### 1. 核实内容

- 读者要理解什么：机制、变化、对比还是结构。
- 核实对象、必需关系、方向、条件和数量。
- 未在方法描述、代码或用户输入中出现的层、维度和连接标记 `[待作者确认]`。

缺失关键拓扑或数值时不得按领域习惯补齐；计数和数值先用代码或记录核验再写进 prompt。

### 2. 选路径

| 任务 | 路径 |
|---|---|
| 位置、长度、面积或颜色需要准确编码数值的曲线、统计图、热图 | Matplotlib（[chart-draw](references/chart/chart-draw.md)） |
| 架构、流程、对照、神经网络等解释图 | 图像模型设计 + TikZ 还原（本流水线） |
| 机制图与定量结果组合 | 分面板制作后合成（[multipanel-figures](references/multipanel-figures.md)） |

### 3. 挑参考图

从 [参考图库](examples/index.md) 挑 1-2 张结构或气质相近的参考图：

- **架构**：[examples/architecture/](examples/architecture/)
- **流程**：[examples/flow/](examples/flow/)
- **对照**：[examples/comparison/](examples/comparison/)
- **神经网络**：[examples/neural-network/](examples/neural-network/)

本地库之外，优先去 **[topconf-paper-figure-gallery](https://github.com/qwdwqfwq/topconf-paper-figure-gallery)**（ICLR/ICML/NeurIPS/CVPR/ACL/AAAI 2023-2026 的 Figure 1 / teaser 合集，按 conceptual / framework / pipeline / architecture / taxonomy / teaser 筛选）找更新的真实论文首图作参考。

参考图在两个阶段都用：

- **第 ①步给图像模型**：作为布局方向和品质示范，让模型基于参考自主构图。
- **第 ②步给 TikZ 还原**：作为版式决策依据（本设计稿属于架构 / 流程 / 对照 / 神经网络哪一类，哪种布局方案更对应）。

### 4. 图像模型出设计稿

按 [diagram-model](references/diagram/diagram-model.md) 的四段式写 prompt（场景 + 事实 + 视觉风格 + 参考作用），通过工具真实接口把参考图传给模型，保存 `prompts/draft.txt` + `drafts/figure-draft.png`。

**产物**：一张 PNG 设计稿 + 完整 prompt 记录。设计稿是**中间产物**，不是最终交付。如模型工具不可用，可直接基于参考图手绘线框作为设计稿，或者跳到步骤 5 由作者自行规划布局。

### 5. TikZ 还原

按 [diagram-tikz](references/diagram/diagram-tikz.md) 对照设计稿重建成矢量图：

1. **读设计稿**：识别节点、连线、分组、关键文字标签、彩色强调区域；用笔或注释在稿上标 TikZ 坐标草图。
2. **按本 skill 视觉语言重建**：复制 `tikz_template.tex`，用 Lancet 2024-07 的 11 种 role box 填节点、`flow` 画箭头、`badge` 做编号圆点；节点标题思源黑体 Medium，描述霞鹜文楷灰色；图标按需添加。
3. **混合渲染（可选）**：TikZ 画不出来的局部（复杂机制图标、手绘风插图、不规则示意），从设计稿裁剪 PNG 或请模型单独补生成一张，用 `\includegraphics` 嵌入；外壳的框、线、文字、分组仍是 TikZ。
4. **编译**：

```bash
python "$skill_dir/scripts/tikz_compile.py" figure.tex \
  --output-dir figures --formats pdf,svg,png
```

**样式对齐硬约束**：还原后的 TikZ 图必须和设计稿**同气质**——调色板、字重、节点形态、留白节奏一致。TikZ 还原不是把设计稿"退化为学术线稿"，而是把设计稿**矢量化**。

工具不可用时（TeX 引擎缺失、xeCJK 字体缺失、超时），说明未生成矢量版本，不悄悄回退到栅格或启用需额外密钥的服务。

### 6. 评审

**三条独立通道分别检查**——科学准确、读者理解、视觉质量 + 文件核验。任一条有问题就返工到对应阶段；返工后重新评审。详见 [diagram-review](references/diagram/diagram-review.md)；数据图走 [chart-review](references/chart/chart-review.md)。

#### 简要自查

**科学准确**：逐字核对必要标签；逐边核对关系、方向、条件；反查多余对象和多余连线。核对 TikZ 还原图是否遗漏或改动了设计稿里的任一个事实元素。

**读者理解**：读者在 10 秒内能看到核心机制、变化或区别吗？关键步骤或分组是否通过位置、大小、颜色或编号明确？

**视觉质量**（框架图）：

- 有没有脱离节点、连线、分组的游离注解？（大标题、游离小标签、底部图例条、作者戳 → 都删掉，让图自解释。）
- 每个节点是否有节点标题 + 一行描述？（图标按需加，不是硬要求。）
- 配色是否按 Lancet 2024-07 调色板分配角色？若使用图标，是否与描边同色（不是黑色）？
- 节点标题是否用思源黑体 Medium、描述是否用霞鹜文楷灰色？字重整体轻盈？
- 箭头是中性深灰细 Latex 大头，不是粗黑或五颜六色？
- 流程多于 3 步时是否贴了小号彩色编号圆点，且不与边标签重叠？
- **样式对齐**：TikZ 还原图与设计稿并排比较，气质是否一致？不是"用矢量退化成另一种风格"？

#### 文件与尺寸核验

```bash
python "$skill_dir/scripts/validate.py" figures/figure.png --placed-width-mm 180 --min-dpi 300
```

TikZ 主输出是 PDF/SVG，PNG 用于预览。混合渲染时核对嵌入 PNG 的实际分辨率、`viewBox`、文字处理。

#### 判定与返工

- 三条通道全部通过 → 保存 `figure.tex` + `figure.pdf` + 设计稿 + prompt + 嵌入资源，交付。
- 事实错误 → 回步骤 1；版式/参考不清 → 回步骤 3；设计稿不合理 → 回步骤 4 重新 prompt；还原偏离设计稿或样式不对齐 → 回步骤 5 修 TikZ；文件尺寸问题 → 回步骤 5。
- 连续修订无改善或关键事实无法核实 → 保留最佳版本并说明限制。

## 什么值得约束，什么留给设计

- **事实准确**是硬约束。标签、关系、方向、数量、公式、来源不能让模型自主。
- **视觉语言**是硬约束。节点、箭头、字体、配色按 [diagram-visual-style](references/diagram/diagram-visual-style.md) 统一，TikZ 还原时必须对齐设计稿气质。
- **布局、形状、具体位置**：第 ①步交给图像模型；第 ②步按设计稿还原。参考图作为方向，不反推成逐节点坐标。
- **按媒介判断可读性**。用实际标签与最终宽度判断；不靠把字号越缩越小解决拥挤。
- **如实呈现**。不生成冒充实验、显微、医学或观测证据的图片；示意与真实数据明确区分。

## 延伸阅读

按问题读取；不因为打开参考就把短 prompt 扩展成全套样式限制。

| 要解决什么 | 读哪份 |
|---|---|
| 挑参考图、学版式 | [examples/index.md](examples/index.md) |
| **框架图** | |
| &nbsp;&nbsp;视觉元素（节点、箭头、字体、配色、图标、布局） | [diagram/diagram-visual-style.md](references/diagram/diagram-visual-style.md) |
| &nbsp;&nbsp;①步出设计稿（写 prompt + 参考图） | [diagram/diagram-model.md](references/diagram/diagram-model.md) |
| &nbsp;&nbsp;②步 TikZ 还原（选版式 + 规划布线 + 混合渲染 + 编译） | [diagram/diagram-tikz.md](references/diagram/diagram-tikz.md) |
| &nbsp;&nbsp;③步评审（科学、理解、视觉、文件、样式对齐） | [diagram/diagram-review.md](references/diagram/diagram-review.md) |
| **数据图** | |
| &nbsp;&nbsp;Matplotlib 绘制、图型、配色 | [chart/chart-draw.md](references/chart/chart-draw.md) |
| &nbsp;&nbsp;数据图评审 | [chart/chart-review.md](references/chart/chart-review.md) |
| **跨类** | |
| 多面板组合 | [multipanel-figures.md](references/multipanel-figures.md) |
| 教学对照图例（弱 vs 强） | [examples/pedagogical/index.md](examples/pedagogical/index.md) |
| 图标选择 | [assets/icons/README.md](assets/icons/README.md) |
