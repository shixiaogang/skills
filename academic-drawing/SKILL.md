---
name: academic-drawing
description: 为论文、教材和技术报告设计、生成、修订和评审静态科研图片。架构图、流程图、机制图与插画默认由图像大模型按统一视觉语言生成，需要真矢量或代码可控时走 TikZ；定量数据图用 Matplotlib；不用于正文写作、交互式仪表盘或伪造实验影像。
---

# 科技绘图

本 skill 按**数据图 vs 框架图**两类组织。框架图使用统一的视觉语言（见 [diagram-visual-style](references/diagram/diagram-visual-style.md)），不切换风格。

- **数据图**（chart）：定量编码，Matplotlib 路径。详见 [references/chart/](references/chart/)。
- **框架图**（diagram）：架构、流程、对照、神经网络等解释图，两条路径二选一。

## 框架图的两条路径

| 路径 | 何时选 | 输入 | 输出 | 读哪份 |
|---|---|---|---|---|
| **图像模型**（默认） | 新设计任何解释图；教学/博客/幻灯片插画感 | 场景 + 事实清单 + 视觉风格 + 参考图 | 一个 **prompt** + 栅格 PNG | [diagram-model](references/diagram/diagram-model.md) |
| **TikZ 代码** | 用户指定代码、维护已有 TikZ 工程、要求真矢量或全部图元可编辑、精确拓扑/公式 | 版式选择 + 节点与连线规划 | 一个可编译的 **`.tex`** + PDF/SVG | [diagram-tikz](references/diagram/diagram-tikz.md) |

两条路径都用 [diagram-visual-style](references/diagram/diagram-visual-style.md) 的 10 色语义板、节点三件套、箭头规格、字体层级。成图均用 [diagram-review](references/diagram/diagram-review.md) 的三条通道（科学 / 读者 / 视觉）验收。

- **图像模型路径**：不规划节点坐标，不列几十条规则；由模型基于场景与参考自主构图。参考图只借布局/品质，不借色值/字体。
- **TikZ 代码路径**：先选版式（架构/流程/对照/神经网络），再规划节点、连线、走廊，用 `tikz_template.tex` 的 10 种 role box 和 badge 圆点填内容。

## 数据图路径

数据图始终走 Matplotlib：保留数据、代码与真实矢量输出。详细 [chart-draw](references/chart/chart-draw.md)；评审 [chart-review](references/chart/chart-review.md)。

## 共用流程

### 1. 核实内容

- 读者要理解什么：机制、变化、对比还是结构。
- 核实对象、必需关系、方向、条件和数量。
- 未在方法描述、代码或用户输入中出现的层、维度和连接标记 `[待作者确认]`。

### 2. 选路径与版式

| 任务 | 路径 |
|---|---|
| 位置、长度、面积或颜色需要准确编码数值的曲线、统计图、热图 | Matplotlib（[chart-draw](references/chart/chart-draw.md)） |
| 架构、流程、对照、神经网络等解释图，无代码或矢量硬要求 | 图像模型（[diagram-model](references/diagram/diagram-model.md)） |
| 同上，但要求真矢量、精确拓扑、公式集成或代码可控 | TikZ（[diagram-tikz](references/diagram/diagram-tikz.md)） |
| 机制图与定量结果组合 | 分面板制作后合成（[multipanel-figures](references/multipanel-figures.md)） |

精确拓扑、数学标签和图形简单都不自动改变默认工具；仅要求 PDF 或文字清晰，不等于要求纯矢量。

### 3. 挑参考图

从 [参考图库](examples/index.md) 挑 1-2 张结构或气质相近的参考图：

- **架构**：[examples/architecture/](examples/architecture/)
- **流程**：[examples/flow/](examples/flow/)
- **对照**：[examples/comparison/](examples/comparison/)
- **神经网络**：[examples/neural-network/](examples/neural-network/)

本地库之外，优先去 **[topconf-paper-figure-gallery](https://github.com/qwdwqfwq/topconf-paper-figure-gallery)**（ICLR/ICML/NeurIPS/CVPR/ACL/AAAI 2023-2026 的 Figure 1 / teaser 合集，按 conceptual / framework / pipeline / architecture / taxonomy / teaser 筛选）找更新的真实论文首图作参考。只借布局与分组节奏，视觉元素仍按 [diagram-visual-style](references/diagram/diagram-visual-style.md) 落地。

参考图作用：

- 图像模型路径 → 用参考图品质引导模型，不复制内容（[diagram-model §二](references/diagram/diagram-model.md)）。
- TikZ 代码路径 → 用参考图的布局方案做版式决策（[diagram-tikz §二](references/diagram/diagram-tikz.md)）。

### 4. 生成

- **图像模型**：按 [diagram-model](references/diagram/diagram-model.md) 的四段式写 prompt（场景 + 事实 + 视觉风格 + 参考作用），把参考图通过工具真实接口传入，保存 `prompt.txt` + `figure.png`。
- **TikZ**：按 [diagram-tikz](references/diagram/diagram-tikz.md) 复制模板、规划布线、编译：

```bash
python "$skill_dir/scripts/tikz_compile.py" figure.tex \
  --output-dir figures --formats pdf,svg,png
```

工具不可用时（接口未配置、密钥缺失、TeX 引擎缺失、超时），说明未生成图片，不悄悄切路径或启用需额外密钥的服务。

### 5. 评审

**三条独立通道分别检查**——科学准确、读者理解、视觉质量 + 文件核验。任一条有问题就返工到对应阶段；返工后重新评审。详见 [diagram-review](references/diagram/diagram-review.md)；数据图走 [chart-review](references/chart/chart-review.md)。

#### 简要自查

**科学准确**：逐字核对必要标签；逐边核对关系、方向、条件；反查多余对象和多余连线。

**读者理解**：读者在 10 秒内能看到核心机制、变化或区别吗？关键步骤或分组是否通过位置、大小、颜色或编号明确？

**视觉质量**（框架图）：

- 有没有脱离节点、连线、分组的游离注解？（大标题、游离小标签、底部图例条、作者戳 → 都删掉，让图自解释。）
- 每个节点是否有节点标题 + 一行描述？（图标按需加，不是硬要求。）
- 配色是否按 Lancet 2024-07 调色板分配角色？若使用图标，是否与描边同色（不是黑色）？
- 节点标题是否用思源黑体 Medium、描述是否用霞鹜文楷灰色？字重整体轻盈？
- 箭头是中性深灰细 Latex 大头，不是粗黑或五颜六色？
- 流程多于 3 步时是否贴了小号彩色编号圆点，且不与边标签重叠？

#### 文件与尺寸核验

```bash
python "$skill_dir/scripts/validate.py" figures/figure.png --placed-width-mm 180 --min-dpi 300
```

有效 DPI 来自像素与实际排版尺寸；改 DPI 标签或上采样不增加细节。SVG 核对 `viewBox`、文字处理和位图组成；TikZ 路径再查字体嵌入与真实矢量输出。

#### 判定与返工

- 三条通道全部通过 → 保存选定产物到项目资源目录，交付。
- 任一条有问题 → 回到对应阶段：事实错误回步骤 1；版式/参考不清回步骤 3；视觉或局部问题回步骤 4；文件尺寸问题回步骤 4。
- 连续修订无改善或关键事实无法核实 → 保留最佳版本并说明限制。

## 什么值得约束，什么留给设计

- **事实准确**是硬约束。标签、关系、方向、数量、公式、来源不能让模型自主。
- **视觉语言**是硬约束。节点、箭头、字体、配色按 [diagram-visual-style](references/diagram/diagram-visual-style.md) 统一，不切换到期刊线稿或其他风格。
- **布局、形状、具体位置**：图像模型路径交给模型，TikZ 路径由设计者规划。参考图作为方向，不反推成逐节点坐标、固定框宽、圆角半径或色值。
- **按媒介判断可读性**。用实际标签与最终宽度判断；不靠把字号越缩越小解决拥挤。
- **如实呈现**。不生成冒充实验、显微、医学或观测证据的图片；示意与真实数据明确区分。

## 延伸阅读

按问题读取；不因为打开参考就把短 prompt 扩展成全套样式限制。

| 要解决什么 | 读哪份 |
|---|---|
| 挑参考图、学版式 | [examples/index.md](examples/index.md) |
| **框架图** | |
| &nbsp;&nbsp;视觉元素（节点、箭头、字体、配色、图标、布局） | [diagram/diagram-visual-style.md](references/diagram/diagram-visual-style.md) |
| &nbsp;&nbsp;图像模型路径（写 prompt + 参考图） | [diagram/diagram-model.md](references/diagram/diagram-model.md) |
| &nbsp;&nbsp;TikZ 代码路径（选版式 + 规划布线 + 编译） | [diagram/diagram-tikz.md](references/diagram/diagram-tikz.md) |
| &nbsp;&nbsp;评审（科学、理解、视觉、文件） | [diagram/diagram-review.md](references/diagram/diagram-review.md) |
| **数据图** | |
| &nbsp;&nbsp;Matplotlib 绘制、图型、配色 | [chart/chart-draw.md](references/chart/chart-draw.md) |
| &nbsp;&nbsp;数据图评审 | [chart/chart-review.md](references/chart/chart-review.md) |
| **跨类** | |
| 多面板组合 | [multipanel-figures.md](references/multipanel-figures.md) |
| 教学对照图例（弱 vs 强） | [examples/pedagogical/index.md](examples/pedagogical/index.md) |
| 图标选择 | [assets/icons/README.md](assets/icons/README.md) |
