# 框架图渲染（diagram-render）—— 流水线第 ②步：TikZ 还原

**本步是流水线的主交付环节**，把 [diagram-design](diagram-design.md) 产出的 PNG 设计稿还原成**可编辑的矢量图**。本步不是另起炉灶，而是**对照设计稿**在 TikZ 里重建版式、节点、连线、文字，使其既符合 [§4.2 视觉规格（TikZ 落地）](#42-视觉规格tikz-落地) 的硬规格，又保持与设计稿一致的气质。

TikZ 画不动的局部（复杂机制插画、手绘风示意、不规则曲面、独特图标）按 [§二 方案三选一](#二方案三选一处理不可实现元素) 决定——复用矢量图标 / 裁剪设计稿 / 请模型重新生成局部 PNG，用 `\includegraphics` 嵌入 TikZ 版面；外壳的节点、连线、文字、分组仍由 TikZ 维护。

完整评审走 [diagram-review](diagram-review.md)。整体流水线见 [SKILL.md](../../SKILL.md)。

**本步产物**：

- `figure.tex`：可编译的矢量源，必要时含 `\includegraphics` 嵌入的 PNG 片段。
- `figure.pdf` / `figure.svg`：矢量主输出。
- `figure.png`：预览栅格，供与设计稿对比。
- `assets/`（可选）：复用矢量图标 / 裁剪自设计稿 / 模型补生成的局部 PNG。

**样式对齐硬约束**：还原图必须与设计稿同气质——Lancet 2024-07 调色板、节点形态、字重轻重、箭头粗细、留白节奏一致。TikZ 还原**不是**把设计稿退化为学术线稿，而是**矢量化**。

**字体是 TikZ 还原的硬约束，与设计稿字体无关**：节点标题**必须**用思源黑体 Medium（Source Han Sans SC Medium），描述 / 边标签 / 分组名**必须**用霞鹜文楷（LXGW WenKai）灰色。即使设计稿里是其他近似字体（图像模型通常无法准确嵌入指定字体），TikZ 还原也**不照搬设计稿字体**，而是严格落地本 skill 的字体规格。字体不一致**不作为**样式对齐失败项，只要字重轻重与整体节奏一致即可。

---

## 一、读设计稿、先确定方案

拿到 [diagram-design](diagram-design.md) 的 `drafts/figure-draft.png` 后，第一步**不是**直接写代码，而是**列清单、定方案**。

### 1.1 清单：图里有什么

- **节点清单**：画面里有哪些节点（框、卡片、圆、立方体）、各自的标题和描述文字、带不带图标、属于哪个角色色。
- **连线清单**：哪些节点之间有连线，起止方位、是否带箭头、线型（实/虚）、是否带边标签、是否属于反馈/回路。
- **分组清单**：哪些节点被圈在同一个框、面板或色带里，分组名贴附位置。
- **强调元素**：badge 圆点位置和颜色、彩色高亮区域、特别图标。
- **近似估计**：节点大小的相对比例、整体画布宽高比、横向/纵向阅读方向。

把每一项标在设计稿的副本上（或写成一份文字清单），作为 TikZ 坐标草图。

### 1.2 事实清单（绘前核对）

- 读者要理解什么：机制、变化、对比还是结构。
- 必需对象、准确标签、关系、方向、条件和数量。
- 任何未在方法描述、代码或用户输入中出现的层、维度和连接标记 `[待作者确认]`。
- 必须保留的准确术语、缩写、版本和数量；单栏或双栏宽度；是否需要与正文中的颜色映射一致。

缺少关键拓扑或数值时不得依据领域习惯自行补全。计数和计算先用代码或记录核验再进入绘图。

### 1.3 识别"TikZ 画不动的元素"

对清单中的每一个元素，先判断 TikZ 能否直接画出来：

- **TikZ 擅长**：矩形/圆角/圆/多边形节点、直线/折线/弧线连接、文字标签、箭头、分组框、badge 圆点、顶色条、规则几何示意。→ 这些**全部**用 TikZ 代码写。
- **TikZ 不擅长**：复杂机制插画（Transformer attention 云、CNN feature map 立体渲染）、三维物件（带阴影的服务器、立体 CPU）、手绘风或水彩风卡通、艺术化图标、不规则曲面、生物/物理设备的拟真图像。→ 这些走 [§二 方案三选一](#二方案三选一处理不可实现元素)。

把"TikZ 不擅长"的元素单独列一张清单，为每一项选定处理方式后再进入 §三 实现。

---

## 二、方案三选一：处理不可实现元素

对 §1.3 列出的"TikZ 不擅长"元素，按优先级三选一。能用矢量方案就不走栅格嵌入，能复用就不新生成。

### 2.1 方案 A：复用已有矢量图标（**优先**）

能用 fontawesome5 或本地 `assets/icons/` 的矢量图标**近似替代**时，优先用矢量图标：

- 通用图标（齿轮 `\faCogs`、数据库 `\faDatabase`、云 `\faCloud`、箭头 `\faArrowRight`、用户 `\faUser`、脑 `\faBrain`、文件 `\faFile` 等）→ 直接 `\usepackage{fontawesome5}` 调用。可用图标映射见 [assets/icons/README.md](../../assets/icons/README.md)。
- 新版 fontawesome5 的 `\faFileAlt` → `\faFile`、`\faMobileAlt` → `\faMobile`、`\faShieldAlt` 已废弃，首次使用前先 `grep fontawesome5-mapping.def`。
- 图标颜色传与节点描边同色（如 `lcBlue!90!black`），**不要用 black**。

**适用判断**：设计稿里的图标语义能被矢量图标表达——即使样式略不同（例如设计稿是手绘感的 CPU，fontawesome5 的 `\faMicrochip` 是扁平线稿），只要**语义准确、风格统一**就优先用矢量。读者认的是语义，不是笔触细节。

### 2.2 方案 B：裁剪设计稿作为 PNG 嵌入

当方案 A 无法替代（没有合适的矢量图标，或语义特殊到必须用具象图），从设计稿裁剪对应区域：

- 用 Preview、GIMP 或 `pdftoppm` + 裁剪脚本从 `drafts/figure-draft.png` 切出目标区域。
- 去背（透明化白色或当前底色）后保存到 `assets/`。
- 继承设计稿的来源与 prompt 记录；文件 License 可追溯。

**适用判断**：设计稿里的插画质量已经够好，只是需要把它"抠"出来嵌到 TikZ 布局里。

### 2.3 方案 C：请大模型重新生成局部 PNG

当方案 A 不可用、方案 B 裁剪质量不足（原图分辨率不够、原图含不想要的背景、原图尺寸比例不对），请模型单独生成局部图：

- Prompt 要求：**仅画 XX 元素、透明背景、风格与设计稿一致**（同一画家笔触、同一调色板、同一线宽、同一笔触密度）。
- 单图分辨率按 §四 的编译目标尺寸计算有效 DPI ≥ 300，必要时请求更高原生输出。
- 保存到 `assets/`，单独记录 prompt。

**适用判断**：需要高分辨率、干净背景、特定比例的局部插画，且方案 A/B 都达不到要求。

### 2.4 决策记录

每一个"TikZ 不擅长"的元素，在 `assets/README.md` 或代码注释里记录：

```text
元素：Transformer attention 云图（右上角）
决策：方案 C（模型补生成）
原因：fontawesome5 无对应矢量；设计稿裁剪分辨率不够。
来源：assets/attention-cloud.png，prompt 见 assets/attention-cloud.prompt.txt
```

决策不透明会在评审时触发返工，建议第一次就记下来。

---

## 三、按版式用 TikZ 实现

设计稿已经给出大致版式。按设计稿观察到的结构，对照下表选具体 TikZ 布局方案。四类版式按读者问题选，每类对应一组布局方案。每一节都给出本地 [examples/](../../examples/) 的参考图目录；本地库之外，也可以在 **[topconf-paper-figure-gallery](https://github.com/qwdwqfwq/topconf-paper-figure-gallery)** 按 conceptual / framework / pipeline / architecture / taxonomy / teaser 标签筛选近年顶会的 Figure 1 作为灵感——只借布局和分组节奏，视觉元素仍按 [§4.2 视觉规格（TikZ 落地）](#42-视觉规格tikz-落地) 落地。

### 3.1 架构图

讲系统分几部分、谁调用谁、边界在哪。参考图在 [examples/architecture/](../../examples/architecture/)。

**绘前额外核对**：系统边界、外部参与者和内部模块；每条连接的起点、终点、方向、载荷或协议；同步/异步、数据/控制、正常/异常等关系类型。

**布局选择**：

| 结构 | 适用 | 阅读方向 | 参考 |
|---|---|---|---|
| 分层 | 计算、存储、网络、应用等稳定层级 | 自上而下或自下而上 | three-tier-architecture |
| 管线 | 数据经过一系列处理阶段 | 自左向右 | web-reference-architecture |
| 中心辐射 | 一个协调器连接多个同级组件 | 中心向外 | api-gateway-fanout |
| 一对多扇出 | 一个核心对多种后端 | 顶部单节点向下分列 | polyglot-persistence |
| 跨区域并列 | 多可用区/多机房 | 水平切片内部相同顺序 | multi-az-regional-architecture |
| 并排对照 | 几种架构方案等权呈现 | 等宽等高面板 | three-architecture-patterns |
| 概览 + 详述 | 一张图承担总览和内部说明 | 上部概览下部展开 | kubernetes-pv-pvc |

**元素要点**：节点按角色分色；相同角色跨图保持相同色相；容器边界表示真实所有权，用虚线框 + 文字标签说明边界含义。常见错误：层级混杂、双向箭头滥用、颜色代替边界、图标过多、全图等权。

### 3.2 流程图

讲一次请求或一轮计算经过哪些步骤。参考图在 [examples/flow/](../../examples/flow/)。多参与者协作走泳道或拆成架构图 + 流程图两张。

**绘前额外核对**：起点、正常主路径、终点或持续运行方式；动作、输入输出、判断条件、循环条件和异常路径；哪些步骤可并行；判断分支的完整条件和汇合位置。

**布局选择**：

| 组织方式 | 适用 | 参考 |
|---|---|---|
| 单行横向 + 编号圆点 | 顺序流程（3-7 步） | messaging-flow |
| 静态架构上 + 运行时步骤下 | 需要同时讲"架构"和"用法" | mcp-protocol-flow |
| 多行 + 汇合节点 | 流程有分支/旁路/回头取用 | rag-flow |
| 泳道 | 多参与者协作 | — |
| 环形 | 持续运行、反馈回路 | — |

**元素要点**：一个节点只表达一个动作；标签用"动词 + 对象"；判断条件标在离开判断节点的边上；顺序超 3 步贴 5-6 mm 彩色实心圆点；主路径实心粗箭头，分支/可选用虚线。常见错误：流程和数据流混用、菱形内写动作、线条交叉、大量回线、编号与箭头重复。

### 3.3 对照图

讲两/三种方案的差异在哪、什么情况下选哪一个。参考图在 [examples/comparison/](../../examples/comparison/)。

**绘前额外核对**：对照的是方案/路径/场景/决策/数据形态；共同的触发条件或冲突背景；每方案的"你得到什么/付出什么"；推荐、风险、等价选项的颜色编码必须真实对应；是否存在连续光谱。

**布局选择**：

| 组织方式 | 适用 | 参考 |
|---|---|---|
| 顶部场景 + 下部两张卡片对照 | 二元权衡 | cap-tradeoff |
| 上下两条平行路径 + 底部 spectrum | 并行路径对比 | caching-tradeoff |
| 顶部运行时视图 + 底部三栏 | 场景 + 机制 + 好处 | kubernetes-configmap |
| 左右两列 + 中间箭头，多行同构 | 决策映射：X 场景选 Y | data-shape-to-database |

超过 3 个选项时改用"决策映射"而非并排卡片。

**元素要点**：顶部标题 + 一行副标题提问建立场景；卡片顶部色条：绿=推荐、红=风险、黄=中间；卡内 `✓ / ⚠ / ✗` 短句不超过 5 条；两列间距 10-14 mm；Spectrum 色阶必须有真实连续语义。

### 3.4 神经网络图

讲模型结构、张量流、注意力、残差、训练与推理路径。参考图在 [examples/neural-network/](../../examples/neural-network/)。

**绘前额外核对**：输入、输出和监督信号；模块名称、顺序、重复次数与共享参数；张量形状；残差、跳连、跨注意力、门控和融合关系；训练专用、推理专用、共享路径。

**抽象层级**：

| 目的 | 应展示 | 应省略 |
|---|---|---|
| 全局架构 | 阶段、关键模块、主数据流、输入输出 | 模块内部每层参数 |
| 创新模块 | 运算顺序、分支、融合、残差、形状变化 | 与贡献无关的标准前后处理 |
| 训练过程 | 损失、监督来源、参数更新路径 | 推理时不存在的重复细节 |
| 推理过程 | 实际执行路径、缓存或自回归循环 | 仅训练使用的损失分支 |

**领域习惯画法（借布局）**：立方体表示张量；斜线投射感受野；扁平块表示运算单元（按运算类型固定色相）；叠块阴影表示并行多头/多层；长桥线表达跨栈关系（Encoder-Decoder cross-attention 必须有显式跨栈线）；brace 做阶段分组；Positional Encoding 用显式 ⊕；重复结构用 `×N`。

**元素要点**：跨注意力标清 Q、K、V 来源；训练/推理路径用明确分区或线型区分并图注说明。常见错误：画成节点墙、张量形状不一致、残差接错、训练推理混淆。

---

## 四、启动与 TikZ 模板

复制 [TikZ 模板](../../templates/tikz_template.tex) 到任务目录。模板默认走 **Lancet 2024-07 调色板**、**思源黑体 Medium + 霞鹜文楷**，整体字重和线重轻盈，与设计稿样式对齐。

```bash
python "$skill_dir/scripts/tikz_compile.py" figure.tex \
  --output-dir figures --formats pdf,svg,png
```

模板内置组件：

- **节点样式**：`r client` / `r api` / `r input` / `r database` / `r compute` / `r neutral` / `r queue` / `r observe` / `r warn` / `r risk` / `r feedback`，11 种角色对应 Lancet 11 色；都接受 `minimum width` / `minimum height` 覆盖默认尺寸。
- **节点内容**：模板提供两种写法——
  - 标题 + 描述（默认）：直接在节点里写 `{\sanssemiboldcjk Title}\\[.08em]{\wenkaicjk\color{muted} Description}`，图标按需添加。
  - 带图标：`\icn{<图标 pt>}{\faXxx}{<标题>}{<描述>}{<图标颜色>}`，图标颜色传与节点描边同色（如 `lcBlue!90!black`），**不要用 black**。图标是**可选**的，不是硬要求。
- **分组与标题**：`figtitle` + `figcaption` 作为**可选**的节点级标题——图能自解释时直接不加。分组用虚线框 + 分组名（贴在边界上），不要用游离的侧边小标签。
- **箭头**：`flow`（中性深灰 Latex 大头 0.9pt，正交折线自动圆角）、`secondary`（更细次要连接）、`dashflow`（虚线可选）、`feedback flow`（Lancet 玫红虚线反馈）。
- **编号圆点**：`badge blue` / `badge cyan` / `badge teal` / `badge grass` / `badge coral` / `badge rose`，4.8 mm 小号实心圆。
- **边标签**：`edge label` 用霞鹜文楷灰色，fill=white 便于穿越底色。

示例：

```latex
\begin{tikzpicture}[x=1mm,y=1mm]
  % No big title and no floating side labels — the figure self-explains.

  % 带图标节点（适合架构、角色区分明显的教学图）
  \node[r client,minimum width=30mm,minimum height=14mm] (a) at (14,14)
    {\icn{16}{\faUser}{Alice}{sends message}{lcBlue!90!black}};

  % 无图标节点（标题 + 描述，适合纯概念或数学示意）
  \node[r api,minimum width=30mm,minimum height=14mm] (b) at (58,14) {%
    \begin{tabular}{@{}l@{}}
      {\sanssemiboldcjk REST API}\\[.08em]
      {\wenkaicjk\color{muted}\fontsize{7.8}{9.6}\selectfont receives via HTTP}
    \end{tabular}};

  \draw[flow] (a.east) -- (b.west);
  \node[badge blue] at (36,14) {1};
\end{tikzpicture}
```

### 4.1 混合渲染：嵌入 §二 产出的 PNG

当 §二 决定了方案 B/C 需要嵌入 PNG 时，用 `\includegraphics` 把 `assets/` 下的 PNG 嵌入 TikZ 版面。外壳的节点、连线、文字、分组仍由 TikZ 维护。

**嵌入写法**（PNG 作为节点内容，外壳是 role box）：

```latex
\usepackage{graphicx}
% ...
\node[inner sep=0pt] (brain) at (54,36) {%
  \includegraphics[width=18mm]{assets/brain-illustration.png}%
};
% 外壳的 role box 包住嵌入图
\node[r compute,fit=(brain),inner sep=1.5mm,
      label={[r compute,above]above:{\sanssemiboldcjk 大脑模型}}] {};
```

**嵌入写法**（PNG 作为底图，TikZ 在上层画箭头/文字）：

```latex
\node[inner sep=0pt] at (0,0)
  {\includegraphics[width=120mm]{assets/attention-cloud.png}};
\node[edge label,fill=white] at (30,10) {Q};
\draw[flow] (10,-20)--(30,-10);
```

**嵌入片段的检查项**：

- 嵌入 PNG 的实际像素密度在最终尺寸下 ≥ 300 DPI。
- 透明背景与白底 TikZ 面板无接缝；若有可见边框，用 `clip` 或后处理裁掉。
- 嵌入片段的调色板和笔触与整图一致——不能左半张工业线稿、右半张卡通水彩。
- 文件 License 可追溯：裁剪自设计稿的 PNG 继承设计稿的来源与 prompt 记录；模型补生成的 PNG 单独记录 prompt。

**混合渲染不满足"真矢量"要求**：如果用户明确要求无位图的纯矢量 PDF/SVG，不能走混合渲染；要么退回 §2.1 用矢量图标代替，要么降低信息密度/换表示方式。

### 4.2 视觉规格（TikZ 落地）

本节是框架图所有视觉元素的**权威规格**，由 TikZ 还原时按 [tikz_template.tex](../../templates/tikz_template.tex) 落地；设计稿不负责这些精确数值。数值参数是最终排版尺寸下的试排起点，目标期刊或用户要求优先。本 skill 的「样式对齐硬约束」入口是本节 + 文件头部的"样式对齐硬约束"段。

#### 4.2.1 骨架

- 底色是纯白或极浅灰。标题是**可选**的：图能靠节点、分组和色彩自解释时不加大标题；需要上下文才加一行节点级标题，字重轻、不喧宾夺主。
- **只保留贴附在元素上的注解**：节点标题、节点描述、箭头上的边标签、分组边界上的分组名。**脱离具体节点、连线或分组的游离注解一律删除**——不写与图内重复的副标题、独立说明段、画布左侧的游离小标签、底部的"xx 色=yy"图例条、角上的作者/日期戳。
- 每个节点是圆角矩形或药丸形，有描边（0.6-0.9 pt，细线不加粗）配 pastel 填充；节点内是**节点标题 + 一行描述**。图标是**可选**辅助——有助于区分角色或增强教学感时可以加（置于标题左侧或顶部，与描边同色、不用黑色）。
- 颜色承担类别或状态语义，并在同图内保持稳定；相同语义使用相同色相，不同语义不共用一个色相。
- 流程线是中性深灰的实心细箭头（0.8-1.1 pt，Latex 大头尺寸 2.4-2.8 mm）；主流程不用虚线，分支或可选关系才用虚线。整体字重和线重都偏轻盈。
- 顺序流程可伴随小号彩色编号圆点（4-6 mm，循环色相），直接贴在箭头旁边标出步骤号；步骤数清晰或箭头方向已自明时允许省略。
- 并行或对照结构改用卡片并排 + 色条标题。
- 整体气质像杂志配图或 technical newsletter，而非幻灯片封面。

目标媒介是黑白印刷或要求纯线稿时，调低饱和度到接近灰阶、保留节点形状，仍保持上述骨架。

**什么能保留，什么要删**：

| 元素 | 判断 | 处理 |
|---|---|---|
| 节点内标题 + 描述（图标按需） | 贴附在节点上 | 保留 |
| 箭头上的边标签（如 "动作 $a_t$"、"记录"） | 贴附在连线上 | 保留 |
| 分组边界 + 分组名（如虚线框 + "参与方 1"） | 贴附在分组上 | 保留 |
| 节点上的编号圆点 | 贴附在连线/节点上 | 保留 |
| 画布大标题 + 封面级副标题 | 游离，与图内重复 | 删除；真需要上下文时留一行节点级标题 |
| 侧边的"TRAIN" / "META-TRAIN" / "POLICY LOOP" 小标签 | 游离，和下方节点组所传达的信息重复 | 删除；需要分段时用节点组本身的位置和色彩表达 |
| 底部"蓝=客户端、绿=服务"的类别图例条 | 游离，颜色语义已在节点上 | 删除；类别信息改到节点自身讲清 |
| 画布角上的"图 N"、"xx 流程图" 等 | 游离，正文或图注承担 | 删除；交给图注 |

#### 4.2.2 节点语义色板

默认使用 **Lancet 2024-07** 调色板（来源 [AMFE 科研配色](https://color.amfe.space/palette/106)）。11 色按色相排序，角色映射把每个语义绑定到一个主色（Border + 图标）和一个浅底（Fill = 该主色 ≈ 18-25% 透明度）：

```text
Role            Main (Border/Icon)  Fill tint    语义示例
client / user   #7B95C6 蓝          #7B95C6!18   客户端、用户、输入
api / gateway   #49C2D9 青          #49C2D9!22   REST、gRPC、Gateway
input / tensor  #A1D8E8 浅青        #A1D8E8!30   输入块、嵌入、张量
database        #67A583 墨绿        #67A583!22   持久化、OLTP、冷存储
compute         #A2C986 嫩绿        #A2C986!25   模型、推理、本地训练
neutral / env   #D0E2C0 浅绿        #D0E2C0!40   环境、说明、Legend
queue / event   #FDED95 浅黄        #FDED95!60   消息队列、PE、时序
observability   #FFC1A6 浅橙        #FFC1A6!40   日志、监控、追踪
warn / caution  #F59C7C 中橙        #F59C7C!35   警告、风险输入、异常
risk / error    #F47254 橙红        #F47254!30   失败、过期、禁区
feedback        #C85E62 玫红        #C85E62!25   反馈、更新、损失
```

**用色准则**：

- 节点填充用主色的 20% 左右透明度，描边、图标、节点标题（当需要彩色标题时）都用对应主色。图标**不是黑色**，与节点同色相融，整体轻盈。
- Lancet 2024-07 的相邻色（蓝→青→浅青、墨绿→嫩绿→浅绿）需要用形状、图标或留白区分，不要连续三节点都走绿系。
- 允许同图使用 4-7 种类别色；每层换色却没有语义时，减少色彩竞争。
- 通过位置、标签、形状或线型辅助识别，不能靠色相承担全部含义。
- 文字默认深墨 `#3B4252`，描述文字默认中灰 `#6B7280`；强调用 feedback 色 `#C85E62` 或 risk 色 `#F47254`。
- 其他期刊专用色板（Nature、Science、JAMA 等）在用户明确指定时覆盖本节；覆盖时整图所有节点与箭头颜色一起更换，不混用两套色板。

数据图配色独立，见 [chart-draw](../chart/chart-draw.md) 配色小节。

#### 4.2.3 节点与卡片样式

| 卡片类型 | 结构 | 适用 |
|---|---|---|
| 标准节点 | 标题（粗 10-12 pt）+ 下描述（细 8-9 pt）；浅底 + 深描边 | 服务、模块、功能节点；最常用的默认形态 |
| 带图标节点 | 左图标 24-32 px + 右标题 + 下描述 | 架构图、教学配图里，用图标帮助区分角色（可选） |
| 顶色条卡片 | 顶部色条 6-10 mm + 色条内白色加粗标题 + 卡片内描述文字（+ 可选 bullet） | 对比卡（Option A/B）、分区标题 |

实现要点：

- 节点最小内边距 `inner xsep=3mm, inner ysep=2mm`；标题到描述间 `0.6em` 行距。
- 加图标时，图标占高度 30-40%，不塞满整格；颜色与节点描边一致，不是黑色。
- 不加图标时，用更大的标题字号或色条顶条提升节点辨识度，避免整图退化为无差别方框。
- 卡片宽度统一到 2-3 档；并列节点保持等高。
- 顶部色条用深色，色条内文字白色；卡片本体是浅色。
- 装饰阴影默认不加；需要立体感时用 1-2 mm 浅灰偏移块，不用高斯阴影。

#### 4.2.4 图标（代码路径）

图标是节点的辅助元素，不是必备。TikZ 侧用 `\usepackage{fontawesome5}`，调用 `\faDatabase`、`\faServer`、`\faCloud` 等。图标颜色设为**节点描边同色**（不是默认黑色），用 `{\color{<role border>}\fontsize{16}{16}\selectfont \faDatabase}` 的方式控制；可用名列表见 [图标资产](../../assets/icons/README.md)。

**Material Icons → fontawesome5 映射**：[diagram-design](diagram-design.md) 的 prompt 用 Google Material Icons 的语义名（例如 `person`、`cloud`、`database`、`settings`、`play_arrow`），因为图像模型更熟悉这套命名；TikZ 还原时在代码里**映射到最接近的 `fontawesome5` 命令**（Material Icons 没有 TeXLive 包）。常见映射：

```text
Material Icon            →  fontawesome5
person / account_circle  →  \faUser
devices / laptop         →  \faLaptop
settings / build         →  \faCogs
storage                  →  \faDatabase
bolt / memory            →  \faBolt / \faMemory
share / fork_right       →  \faStream / \faShareNodes
public / router          →  \faGlobe / \faNetworkWired
notifications            →  \faBell
monitoring / show_chart  →  \faChartLine
visibility               →  \faEye
cloud                    →  \faCloud
smartphone               →  \faMobileScreen
folder / description     →  \faFolder / \faFileLines
code / terminal          →  \faCode / \faTerminal
psychology / smart_toy   →  \faBrain / \faRobot
lock / shield            →  \faLock / \faShield
input                    →  \faSignInAlt
play_arrow               →  \faPlay
merge_type               →  \faCodeBranch
category                 →  \faThLarge
```

未安装 fontawesome5 时 fallback 使用 Unicode 符号，但 Unicode 不是首选；缺字时在图注说明近似。

#### 4.2.5 线条层级

| 元素 | 代码试排线宽 | 用法 |
|---|---:|---|
| 节点描边 | 0.6-0.9 pt | 用节点主色，细线保持轻盈 |
| 主流程箭头 | 0.8-1.1 pt | 中性深灰 `#6B7280`，不用黑色 |
| 反馈/更新 | 0.9-1.0 pt dashed | Lancet 玫红 `#C85E62`，表示回路 |
| 次要连接 | 0.6-0.8 pt | 中灰 `#6B7280!60`，无箭头或端点为小圆 |
| 分支/可选关系 | 0.7-0.9 pt dashed | 虚线段 2 mm 实 1.6 mm 空 |
| 卡片顶部色条 | 填充色块，无描边 | 色条高度 5-8 mm |

**线型语义**：

```text
solid     确定关系、实际计算与数据路径
dashed    可选、间接或训练反馈等需区分的关系；每图明确一种含义
dotted    参考线、预测、假设或待验证关系
dash-dot  第三个数据系列；只在确有需要时使用
```

- 默认主流程全部实线，分支/可选用虚线。不把全部关系改成虚线。
- 相同线型在同一张图中只表达一种关系。
- 主次优先用线宽和深浅区分；不因为路径处于次要层级就自动改为虚线。

#### 4.2.6 箭头与连接

- 默认 Latex 大头箭头（`Latex[length=2.6mm,width=1.8mm]`），实心、填充与线色相同；颜色用中性深灰 `#6B7280`，不是纯黑。
- 连线主流程走正交折线（水平段 + 竖直段），转角用 `rounded corners=0.8mm`，不走对角线。
- 分支/循环/反馈可用弧线，使用 `to[bend left=20]` 等软曲线；避免 S 形两段弧。
- 箭头不得穿过节点、文字、面板标签或其他箭头标签。
- 尽量消除交叉；无法消除时改变布局；关系过密且不可重排时才用明确的跨线桥。
- 共享起点的分支使用一致的出口、间距和转折位置。
- 用箭头表示方向，用无箭头线表示无向关联，用双箭头表示确实双向的关系（请求+响应 ≠ 一条双向线），用钝端或 T 形端点表示抑制。
- 两线交叉不自动表示汇合；真实汇合与单纯跨越必须可区分，只有确有连接语义时才加汇合点。
- Badge 圆点和边标签不要盖在同一位置：badge 贴近箭头起点或终点，边标签放在箭头中段上方 1-2 mm。

#### 4.2.7 编号圆点

顺序流程图用小号彩色实心圆点显示步骤号：

- 圆直径 4-6 mm，填充按 Lancet 调色板循环（蓝→嫩绿→浅橙→玫红→墨绿）。
- 圆内数字白色思源黑体 Medium，字号 8-9 pt。
- 圆点贴在箭头的中段或起点旁，距离箭头线和边标签至少 1.5 mm，不要互相遮挡。
- 不超过 9 步；超过要么分段，要么用字母 A/B/C 替代，不用两位数字。

#### 4.2.8 字体与标签

**字族**：

- **节点标题**：**思源黑体 Medium**（Source Han Sans SC Medium）。字重用 Medium 而非 Bold，整体轻盈不臃肿。英文可用 Inter / Helvetica Medium。
- **节点描述 / 边标签 / 分组名**：**霞鹜文楷**（LXGW WenKai）Regular，颜色用中灰 `#6B7280`。手写体感的衬线笔画，和思源黑体的现代几何感形成对比。
- **编号圆点**：思源黑体 Medium，白字实心背景。
- 其他数学符号、变量、公式仍走 LaTeX 数学字体（`\bm{\theta}` 等）；中文和西文混排时 `xeCJK` 自动切换。

| 元素 | 默认字号 | 字族 |
|---|---:|---|
| 可选节点级标题 | 10-12 pt | 思源黑体 Medium |
| 节点标题 | 9-10 pt | 思源黑体 Medium，与描边同色或深墨 |
| 节点描述 | 7.5-8.5 pt | 霞鹜文楷 Regular，中灰 |
| 边标签 / 分组名 | 7.5-8 pt | 霞鹜文楷 Regular，中灰 |
| 编号圆点 | 8-9 pt | 思源黑体 Medium，白字 |
| 建议避免低于 | 6 pt | — |

- 字号层级保持少而清楚，通常 3-4 档。
- 标签不能依赖颜色名称（用"Treatment A"而不是"红线"）。
- fontspec 示例：

```latex
\usepackage{fontspec}
\usepackage{xeCJK}
\setCJKmainfont{Source Han Sans SC}
\newCJKfontfamily\sanssemiboldcjk{Source Han Sans SC Medium}
\newCJKfontfamily\wenkaicjk{LXGW WenKai}
```

#### 4.2.9 布局与构图

**画布与阅读方向**：

- 先确定最终画布、面板比例和图注位置，再用实际标签安排对象。
- 整图通常横向，宽高比约 3:2 到 16:9；默认画布宽度 150-200 mm。
- 未指定目标时以约 90 mm 单栏或 180 mm 双栏宽度试排。
- 顶部主标题留 12-16 mm 空白；底部图例/时间轴留 10-14 mm 空白；节点组之间留 10-14 mm 空白。

**网格与对齐**：同层对象对齐共享边缘、中心线或文字基线；一个对象不要同时服从多个互相冲突的对齐。框、文字、图标和连接端口是同一布局单元。网格用于建立节奏，不要求所有区域机械等分。

**留白与分组**：保留能够隔离视觉焦点、区分组别的留白；消除未裁切画布、远置图例、不一致间距造成的无意义空白。可用邻近、留白、底板或边框表达分组；表示系统、安全或区室边界时必须对应真实归属。

**视觉层级**：每个面板围绕一个核心信息；核心对象位于阅读路径上的高优先位置并获得足够邻近留白。多个强色、大标题、粗边框和粗箭头互相争夺注意时，减少竞争或重新安排重点。

**端口与避让**：同侧多条独立连接各用一个可辨认的端口，在可用直边长度内均匀分配。并行独立线路保持可见间隙。先放语义底板，再画连线、节点及文字，并检查实际遮挡。

#### 4.2.10 可访问性

- 不以颜色作为唯一区分手段；至少再使用直接标签、点形、线型、位置或纹理之一。
- 优先直接标注数据线或对象，避免读者在图与远处图例间反复匹配颜色。
- 重要图形对象对比 3:1、小字 4.5:1 作为参考，以最终媒介和实际阅读为准。
- 检查灰度；关键区分依赖色彩时再做 protanopia / deuteranopia / tritanopia 模拟。

#### 4.2.11 视觉规格来源

- [Science Guide to Preparing Figures](https://www.science.org/cms/asset/6ebc81c2-e38a-4cea-b0c2-a0402817f13e/author_prep_guide_2025.pdf)
- [IEEE Create Graphics for Your Article](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/)
- [Color Universal Design](https://jfly.uni-koeln.de/color/)
- [W3C Non-text Contrast](https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast)
- [System Design Classroom newsletter](https://newsletter.systemdesignclassroom.com/) 与 [ByteByteGo blog](https://blog.bytebytego.com/) — 节点视觉样式实例

---

## 五、多节点正交布线预检

节点多、反馈线跨越多栏时，先按下表列每一条线再写 `\draw`：

| 条目 | 要点 |
|---|---|
| 起点锚点 | 用显式方位（`west` / `east` / `south` / `north`）或精确坐标；不同线从同一节点出入时分配到不同方位 |
| 中段走廊 | 列出每段的 x 或 y 常量；左右两侧与底部各走廊的坐标相差至少 6-10mm |
| 终点锚点 | 优先 `west/east/north/south`；最后一段进节点时方向与锚点方向一致 |
| 入节点位置 | 不进 `.north west` / `.south east` 等角点；需要多条线进同一边时用 `($(node.west)+(0,3)$)` 显式偏移 |
| 可能穿越 | 列出路径跨过的其他节点与线段；跨越节点的横/竖段必须回避，不靠 `rounded corners` 让它看起来还好 |

TikZ 的 `A |- B` 和 `A -| B` 把转折点放在**另一个节点的坐标处**，当 A 与 B 之间还有第三个节点时转折常落在该节点内部。多节点布局优先写**显式三段折线**：`(A) -- (x1,y1) -- (x2,y2) -- (B)`。

节点位置调整后，重查依赖该节点坐标的**所有横线和竖线**，不能只检查刚移动的那条线。

### 入节点锚点与箭头方向

TikZ 箭头的朝向由**最后一段路径的方向**决定，而不是终点锚点名字。想让箭头水平入节点，最后一段必须是**水平段**：

- 要水平入节点左侧：最后一段 `(x_corridor, y_target) -- (node.west)`，`y_target == node.west.y`。
- 不想碰角、又想真正水平：最后一段 `(x_corridor, y_target) -- ($(node.west)+(0, dy)$)`，`y_target` 同步等于 `node.west.y + dy`。
- 不要用 `(node.north west |- 0,y)` 这类表达。

---

## 六、foreach 变量命名避坑

`\foreach` 的变量名不要和 LaTeX 原生命令撞车：

- `\color` 是 LaTeX 原生命令，用作 `\foreach \x/\color in {...}` 时会在 `\iconnode` 中触发错误解析（如把 `client box` 当文本输出）。改用 `\cls`、`\clr` 等。
- 节点名、箭头名、描述文本都不要和 TikZ 关键字（`fill`、`draw`、`node`）同名。

---

## 七、真实矢量与可编辑性

用户要求无位图的 SVG/PDF 或全部图元可编辑时，将已核验设计完整重建为 SVG、TikZ 或项目支持的矢量对象。嵌入 PNG、只覆盖标签、修改扩展名，都不满足全图矢量要求。

区分字形轮廓、可编辑文本和可编辑绘图源：轮廓是矢量但不能直接改字；需要在交付 SVG 中修改文字时保留文本。仅要求清晰文字或 PDF 时，不自行扩大为全图重建。

---

## 八、编译并与设计稿对比

编译：

```bash
python "$skill_dir/scripts/tikz_compile.py" figure.tex \
  --output-dir figures --formats pdf,svg,png
```

字体嵌入或文字提取正常不能替代查看渲染结果。SVG 核对 `viewBox`、文字处理和位图组成。有排版文件时再看嵌入页。

**与设计稿对比**：把 `drafts/figure-draft.png` 和 `figures/figure.png` 并排放，核对以下项**基本一致**（允许矢量化带来的笔触差异，不允许信息丢失或样式漂移）：

- **节点清单对齐**：设计稿里的每一个节点都在 TikZ 版本里出现（允许嵌入 PNG 替代装饰性插画，不允许静默丢失事实节点）。
- **连线清单对齐**：每条连线的起止、方向、线型、边标签都保留；箭头方向一致。
- **分组清单对齐**：分组边界、分组名位置都对应。
- **布局节奏对齐**：主次节点大小比例、组内 vs 组间间距比例、整图阅读方向与设计稿一致。
- **样式气质对齐**：调色板、字重轻重、节点形态、箭头粗细、留白节奏与设计稿同气质，不是退化为灰阶学术线稿。**字体不要求与设计稿一致**：TikZ 还原按本 skill 字体规格落地（节点标题思源黑体 Medium、描述霞鹜文楷灰色），即使设计稿字体不同也不作为失败项，只要字重轻重与设计稿同气质。
- **强调元素对齐**：badge 位置和颜色、彩色强调区域、特别图标位置都保留。

**不一致时的处理**：

- **信息丢失**（节点、连线、分组、关键文字标签缺失）→ 补回 TikZ。
- **布局漂移**（节点位置顺序和设计稿差太多）→ 调 TikZ 坐标。
- **样式漂移**（配色、字重、线宽偏离设计稿）→ 回查是否误用了旧样式、是否字体加载正确。
- **设计稿本身有问题**（事实错误、关系错位）→ 回步骤 ①，让 [diagram-design](diagram-design.md) 重新修订设计稿，再回到本步。

对比通过后进入 [diagram-review](diagram-review.md) 做最终评审。

### 文件核验

```bash
python "$skill_dir/scripts/validate.py" \
  figures/figure.pdf figures/figure.svg figures/figure.png
```

**交付物**：`figure.tex` 源码、`figure.pdf` 主输出、按需的 `figure.svg` / `figure.png` 预览、`assets/` 嵌入资源与决策记录；完整评审走 [diagram-review](diagram-review.md)。

---

## 九、工具不可用时

TeX 引擎、所需宏包或 fontawesome5 不可用时，说明未生成图片，不悄悄改用其他路径或启用需额外密钥的服务。
