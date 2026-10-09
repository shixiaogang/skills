# 框架图渲染（diagram-render）—— 流水线第 ②步：TikZ 还原

**本步是流水线的主交付环节**，把 [diagram-design](diagram-design.md) 产出的 PNG 设计稿还原成**可编辑的矢量图**。本步不是另起炉灶，而是**对照设计稿**在 TikZ 里重建版式、节点、连线、文字，使其既符合 [diagram-design §四](diagram-design.md#四视觉规格权威规格) 的视觉语言，又保持与设计稿一致的气质。

TikZ 画不动的局部（复杂机制插画、手绘风示意、不规则曲面、独特图标）按 [§二 方案三选一](#二方案三选一处理不可实现元素) 决定——复用矢量图标 / 裁剪设计稿 / 请模型重新生成局部 PNG，用 `\includegraphics` 嵌入 TikZ 版面；外壳的节点、连线、文字、分组仍由 TikZ 维护。

完整评审走 [diagram-review](diagram-review.md)。整体流水线见 [SKILL.md](../../SKILL.md)。

**本步产物**：

- `figure.tex`：可编译的矢量源，必要时含 `\includegraphics` 嵌入的 PNG 片段。
- `figure.pdf` / `figure.svg`：矢量主输出。
- `figure.png`：预览栅格，供与设计稿对比。
- `assets/`（可选）：复用矢量图标 / 裁剪自设计稿 / 模型补生成的局部 PNG。

**样式对齐硬约束**：还原图必须与设计稿同气质——Lancet 2024-07 调色板、节点形态、字重、箭头粗细、留白节奏一致。TikZ 还原**不是**把设计稿退化为学术线稿，而是**矢量化**。

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

设计稿已经给出大致版式。按设计稿观察到的结构，对照下表选具体 TikZ 布局方案。四类版式按读者问题选，每类对应一组布局方案。每一节都给出本地 [examples/](../../examples/) 的参考图目录；本地库之外，也可以在 **[topconf-paper-figure-gallery](https://github.com/qwdwqfwq/topconf-paper-figure-gallery)** 按 conceptual / framework / pipeline / architecture / taxonomy / teaser 标签筛选近年顶会的 Figure 1 作为灵感——只借布局和分组节奏，视觉元素仍按 [diagram-design §四](diagram-design.md#四视觉规格权威规格) 落地。

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
- **样式气质对齐**：调色板、字重、节点形态、箭头粗细、留白节奏一致，不是退化为灰阶学术线稿。
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
