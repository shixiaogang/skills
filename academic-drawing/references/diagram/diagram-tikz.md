# TikZ 路径（diagram-tikz）

讲**用 TikZ 代码绘制框架图**：从读者问题到选版式、规划节点与连线，再到渲染输出一个可编译的 `.tex` 文件。视觉元素的具体样式走 [diagram-visual-style](diagram-visual-style.md)；成图验收走 [diagram-review](diagram-review.md)。

**何时走本路径**：

- 用户指定代码工具或已有 TikZ 工程维护。
- 明确要求真实矢量、全部图元可编辑或 PDF/SVG 可直接改字。
- 精确拓扑、精确数学标签、复杂公式嵌入或与 LaTeX 正文强耦合。

精确拓扑和图形简单不自动切到代码路径；"要 PDF" 不等于"要真矢量"。不满足上述条件的解释图默认走 [diagram-model](diagram-model.md)。

---

## 一、绘前核对

- 读者要理解什么：机制、变化、对比还是结构。
- 必需对象、准确标签、关系、方向、条件和数量。
- 任何未在方法描述、代码或用户输入中出现的层、维度和连接标记 `[待作者确认]`。
- 必须保留的准确术语、缩写、版本和数量；单栏或双栏宽度；是否需要与正文中的颜色映射一致。

缺少关键拓扑或数值时不得依据领域习惯自行补全。计数和计算先用代码或记录核验再进入绘图。

---

## 二、选版式

四类版式按读者问题选，每类对应一组布局方案。每一节都给出本地 [examples/](../../examples/) 的参考图目录；本地库之外，也可以在 **[topconf-paper-figure-gallery](https://github.com/qwdwqfwq/topconf-paper-figure-gallery)** 按 conceptual / framework / pipeline / architecture / taxonomy / teaser 标签筛选近年顶会的 Figure 1 作为灵感——只借布局和分组节奏，视觉元素仍按 [diagram-visual-style](diagram-visual-style.md) 落地。

### 2.1 架构图

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

### 2.2 流程图

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

### 2.3 对照图

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

### 2.4 神经网络图

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

## 三、启动与模板

复制 [TikZ 模板](../../templates/tikz_template.tex) 到任务目录。模板默认走 **Lancet 2024-07 调色板**、**思源黑体 Medium + 霞鹜文楷**，整体字重和线重轻盈。

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
- **图标（可选）**：`\usepackage{fontawesome5}`。可用图标映射见 [assets/icons/README.md](../../assets/icons/README.md)。新版 fontawesome5 的 `\faFileAlt` → `\faFile`、`\faMobileAlt` → `\faMobile`、`\faShieldAlt` 已废弃，首次使用前先 grep `fontawesome5-mapping.def`。
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

---

## 四、多节点正交布线预检

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

## 五、foreach 变量命名避坑

`\foreach` 的变量名不要和 LaTeX 原生命令撞车：

- `\color` 是 LaTeX 原生命令，用作 `\foreach \x/\color in {...}` 时会在 `\iconnode` 中触发错误解析（如把 `client box` 当文本输出）。改用 `\cls`、`\clr` 等。
- 节点名、箭头名、描述文本都不要和 TikZ 关键字（`fill`、`draw`、`node`）同名。

---

## 六、真实矢量与可编辑性

用户要求无位图的 SVG/PDF 或全部图元可编辑时，将已核验设计完整重建为 SVG、TikZ 或项目支持的矢量对象。嵌入 PNG、只覆盖标签、修改扩展名，都不满足全图矢量要求。

区分字形轮廓、可编辑文本和可编辑绘图源：轮廓是矢量但不能直接改字；需要在交付 SVG 中修改文字时保留文本。仅要求清晰文字或 PDF 时，不自行扩大为全图重建。

---

## 七、输出与检查

```bash
python "$skill_dir/scripts/validate.py" \
  figures/figure.pdf figures/figure.svg figures/figure.png
```

字体嵌入或文字提取正常不能替代查看渲染结果。SVG 核对 `viewBox`、文字处理和位图组成。有排版文件时再看嵌入页。

**交付物**：`.tex` 源码、`.pdf` 主输出、按需的 `.svg` / `.png` 预览；完整评审走 [diagram-review](diagram-review.md)。

---

## 八、工具不可用时

TeX 引擎、所需宏包或 fontawesome5 不可用时，说明未生成图片，不悄悄改用其他路径或启用需额外密钥的服务。
