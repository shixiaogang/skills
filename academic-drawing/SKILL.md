---
name: academic-drawing
description: 为论文、教材和技术报告设计、生成、修订和评审静态科研图片。框架图走"设计 → 渲染 → 评审"的串联流水线：图像模型根据场景/事实/视觉要求出设计稿，再用 TikZ 对照还原，必要时复用矢量图标、裁剪设计稿或请模型重新生成局部 PNG 嵌入；定量数据图用 Matplotlib；不用于正文写作、交互式仪表盘或伪造实验影像。
---

# 科技绘图

本 skill 按**数据图 vs 框架图**两类组织。

- **数据图**（chart）：定量编码，Matplotlib 路径。详见 [references/chart/](references/chart/)。
- **框架图**（diagram）：架构、流程、对照、神经网络等解释图，走"**设计 → 渲染 → 评审**"三步串联流水线。

**统一色板**：框架图和数据图**共用**同一份 **Lancet 2024-07 调色板**（11 种 HEX）。分类用色严格从色板中取；连续色阶在色板内选相近色相插值；禁止色板外色、禁止自行加亮/加暗/调饱和。调色板的权威定义见 [diagram-render §4.2.2](references/diagram/diagram-render.md#422-节点语义色板)。

## 框架图流水线

```
事实 + 视觉要求 + 参考图
        │
        ▼
   ① 设计（design）              ← diagram-design
   图像大模型自主设计构图、
   分组节奏、色彩比例、形状；
   产出 PNG 设计稿；初步检查
   通过后进入下一步。
        │
        ▼
   ② 渲染（render）              ← diagram-render
   对照设计稿用 TikZ 还原矢量图。
   不可实现的图片元素先确定方案：
     a. 优先复用 Lucide SVG，无法复用时退用 Font Awesome 7 regular / outline
     b. 裁剪设计稿作为 PNG 嵌入
     c. 请模型重新生成局部 PNG 嵌入
   编译后与设计稿并排对比，
   连线/布局/分组/关键文字标签
   基本一致方可进入评审。
        │
        ▼
   ③ 评审（review）              ← diagram-review
   科学准确 / 读者理解 /
   视觉质量 + 样式对齐 四通道。
```

**路径说明**：

- **① 设计（diagram-design）**：描述场景、事实清单、基本视觉要求、参考图品质喂给图像大模型，让模型自主决定构图、分组节奏、色彩比例、形状；输出 PNG **设计稿**作为中间产物（含完整 prompt 记录）；对设计稿做初步事实与视觉检查，通过后再进入第 ②步。视觉风格为 **Lancet 调色板 + 轻盈 technical newsletter 风格 + Lucide outline 图标（可选，Font Awesome 7 regular / outline 兜底）**；精确字重、线宽、字号、留白等视觉规格不在本步交给模型，由第 ②步 TikZ 严格落地。**字体允许近似**：图像模型通常无法准确嵌入指定字体，设计稿字体近似外观即可，不作为合格条件。
- **② 渲染（diagram-render）**：对照设计稿按本 skill 视觉语言用 TikZ 重建成矢量图。**TikZ 只负责微小局部改动**——字体、字号微调、边距数值的小量规整、图标替换；布局/留白/连线/形状/颜色一律沿用设计稿，不自行调整。**先确定方案**：对每一个 TikZ 不擅长实现的图片元素，三选一——优先复用 Lucide SVG，无法复用时退用 Font Awesome 7 regular / outline；或裁剪设计稿对应区域；或请模型重新生成局部 PNG。然后用 `tikz_template.tex` 的 Lancet 11 种 role box 实现外壳，用 `\includegraphics` 嵌入 PNG。本步同时承载完整的「视觉规格（TikZ 落地）」中硬规格——Lancet 2024-07 色板、思源黑体 Normal + 霞鹜文楷字体表；其它视觉参数（线宽/箭头/编号圆点/留白节奏）从设计稿观察并沿用。编译后与设计稿**并排对比**，连线、布局、分组、关键文字标签基本一致方可进入评审。
- **③ 评审（diagram-review）**：三通道检查——科学准确、读者理解、视觉质量 + 样式对齐。样式对齐把 TikZ 还原图与设计稿并排核对调色板、字重、节点形态、留白节奏、混合渲染衔接、信息完整性；布局/留白/连线/形状/颜色偏离设计稿是阻断项。

## 数据图路径

数据图始终走 Matplotlib：保留数据、代码与真实矢量输出。详细 [chart-draw](references/chart/chart-draw.md)；评审 [chart-review](references/chart/chart-review.md)。

**chart 与 diagram 共用同一套 Lancet 2024-07 色板**（11 色主色严格约束，不允许色板外任何近似色）。两类图在同一文档内配色保持一致。

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
| 架构、流程、对照、神经网络等解释图 | 设计 → 渲染 → 评审（本流水线） |
| 机制图与定量结果组合 | 分面板制作后合成（[multipanel-figures](references/multipanel-figures.md)） |

### 3. 挑参考图

从 [参考图库](examples/index.md) 挑 1-2 张结构或气质相近的参考图：

- **架构**：[examples/architecture/](examples/architecture/)
- **流程**：[examples/flow/](examples/flow/)
- **对照**：[examples/comparison/](examples/comparison/)
- **神经网络**：[examples/neural-network/](examples/neural-network/)

本地库之外，优先去 **[topconf-paper-figure-gallery](https://github.com/qwdwqfwq/topconf-paper-figure-gallery)**（ICLR/ICML/NeurIPS/CVPR/ACL/AAAI 2023-2026 的 Figure 1 / teaser 合集，按 conceptual / framework / pipeline / architecture / taxonomy / teaser 筛选）找更新的真实论文首图作参考。只借布局与分组节奏，视觉元素仍按 [diagram-render §4.2](references/diagram/diagram-render.md#42-视觉规格tikz-落地) 落地。

参考图在两个阶段都用：

- **第 ①步给图像模型**：作为布局方向和品质示范，让模型基于参考自主构图。
- **第 ②步给 TikZ 还原**：作为版式决策依据（设计稿属于架构 / 流程 / 对照 / 神经网络哪一类，哪种布局方案更对应）。

### 4. 设计（diagram-design）

按 [diagram-design](references/diagram/diagram-design.md) 的四段式写 prompt（场景 + 事实 + 视觉风格 + 参考作用），通过工具真实接口把参考图传给模型，保存 `prompts/draft.txt` + `drafts/figure-draft.png`。设计稿**是中间产物**，不是最终交付。

出设计稿后做一轮初步检查：

- **事实检查**：必需对象、准确标签、关系、方向、不变量是否齐全。
- **视觉检查**：配色、字重、节点形态是否符合 Lancet 2024-07 + 思源黑体 Normal + 霞鹜文楷骨架；有无游离的大标题、侧边小标签、底部图例条。

初步检查不通过就回到 prompt 修订，不要带着错误事实进入第 ②步。

### 5. 渲染（diagram-render）

按 [diagram-render](references/diagram/diagram-render.md)：

1. **读设计稿、先确定方案**：列节点 / 连线 / 分组 / 强调元素清单；对 TikZ 不擅长实现的元素，三选一处理：
   - **方案 A（优先）**：复用 Lucide SVG 或本地 `assets/icons/` 的矢量图标；Lucide 无对应项时退用 Font Awesome 7 regular / outline；
   - **方案 B**：裁剪设计稿对应区域作为 PNG 嵌入；
   - **方案 C**：请大模型重新生成局部 PNG（指定风格与设计稿一致、透明背景）嵌入。
   每个决策记录到 `assets/README.md` 或代码注释。
2. **按 tikz_template.tex 实现**：Lancet 11 种 role box、`\icn` 五参数（图标可选）、badge 圆点、edge label；思源黑体 Normal + 霞鹜文楷。混合渲染时用 `\includegraphics` 嵌入 `assets/` 下的 PNG，外壳的节点、连线、文字、分组仍由 TikZ 维护。
3. **编译并对比**：

```bash
python "$skill_dir/scripts/tikz_compile.py" figure.tex \
  --output-dir figures --formats pdf,svg,png
```

与 `drafts/figure-draft.png` 并排对比，确认连线、布局、分组、关键文字标签都能还原、样式气质一致。不一致则调整 TikZ，或回到第 ④步让模型修订设计稿。

工具不可用时（TeX 引擎、xeCJK、Lucide SVG 资源或 Font Awesome 7 兼容命令缺失、超时），说明未生成矢量版本，不悄悄回退或启用需额外密钥的服务。

### 6. 评审（diagram-review）

**三条独立通道分别检查**——科学准确、读者理解、视觉质量 + 样式对齐 + 文件核验。任一条有问题就返工到对应阶段；返工后重新评审。详见 [diagram-review](references/diagram/diagram-review.md)；数据图走 [chart-review](references/chart/chart-review.md)。

#### 简要自查

**科学准确**：逐字核对必要标签；逐边核对关系、方向、条件；反查多余对象和多余连线。核对 TikZ 还原图是否遗漏或改动了设计稿里的任一个事实元素。

**读者理解**：读者在 10 秒内能看到核心机制、变化或区别吗？关键步骤或分组是否通过位置、大小、颜色或编号明确？

**视觉质量**（框架图）：

- 有没有脱离节点、连线、分组的游离注解？（大标题、游离小标签、底部图例条、作者戳 → 都删掉，让图自解释。）
- 每个节点是否有节点标题 + 一行描述？（图标按需加，不是硬要求。）
- 配色是否按 Lancet 2024-07 调色板分配角色？若使用图标，是否全图统一且与描边同色（不是黑色）？
- **TikZ 侧硬要求**：节点标题思源黑体 Normal、描述霞鹜文楷灰色、整体字重轻盈；字体字号表按 [diagram-render §4.2](references/diagram/diagram-render.md#42-视觉规格tikz-落地) 落地。其他视觉参数（线宽、箭头、编号圆点、留白）从设计稿观察并沿用，不独立规格化。设计稿字体允许近似，不作失败项。
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
- **视觉语言**是硬约束。节点、箭头、字体、配色按 [diagram-render §4.2 视觉规格（TikZ 落地）](references/diagram/diagram-render.md#42-视觉规格tikz-落地) 统一，TikZ 还原时必须对齐设计稿气质。
- **布局、形状、具体位置**：第 ①步交给图像模型；第 ②步按设计稿还原。参考图作为方向，不反推成逐节点坐标。
- **按媒介判断可读性**。用实际标签与最终宽度判断；不靠把字号越缩越小解决拥挤。
- **如实呈现**。不生成冒充实验、显微、医学或观测证据的图片；示意与真实数据明确区分。

## 延伸阅读

按问题读取；不因为打开参考就把短 prompt 扩展成全套样式限制。

| 要解决什么 | 读哪份 |
|---|---|
| 挑参考图、学版式 | [examples/index.md](examples/index.md) |
| **框架图** | |
| &nbsp;&nbsp;①步 设计（prompt、参考图、视觉规格、初步检查） | [diagram/diagram-design.md](references/diagram/diagram-design.md) |
| &nbsp;&nbsp;②步 渲染（方案三选一、TikZ 实现、混合渲染、对比） | [diagram/diagram-render.md](references/diagram/diagram-render.md) |
| &nbsp;&nbsp;③步 评审（科学、理解、视觉、样式对齐、文件） | [diagram/diagram-review.md](references/diagram/diagram-review.md) |
| **数据图** | |
| &nbsp;&nbsp;Matplotlib 绘制、图型、配色 | [chart/chart-draw.md](references/chart/chart-draw.md) |
| &nbsp;&nbsp;数据图评审 | [chart/chart-review.md](references/chart/chart-review.md) |
| **跨类** | |
| 多面板组合 | [multipanel-figures.md](references/multipanel-figures.md) |
| 教学对照图例（弱 vs 强） | [examples/pedagogical/index.md](examples/pedagogical/index.md) |
| 图标选择 | [assets/icons/README.md](assets/icons/README.md) |
