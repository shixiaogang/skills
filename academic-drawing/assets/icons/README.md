# 图标资产

本目录是本 skill 的图标使用参考。**不保存第三方 SVG 文件**；代码路径默认通过 LaTeX 字体包调用，图像模型路径通过语义化提示词由模型自绘。

## 路径选择

| 路径 | 使用方式 | 为什么 |
|---|---|---|
| TikZ / LaTeX 代码路径 | `\usepackage{fontawesome5}` + `\faDatabase` 等命令 | 零外部依赖；TeX Live / MiKTeX 自带；节点内直接插入 |
| 图像大模型路径 | 提示词里描述图标语义 + 风格锚（如 "Phosphor regular icon"） | 模型自绘，风格可控；不需要本地 SVG |
| SVG 直接插入 | 下载 SVG → 转 PDF → `\includegraphics` | 仅在前两条无法满足特定图标时使用；流程繁琐 |

## 代码路径：fontawesome5 常用图标映射

LaTeX 中：

```latex
\usepackage{fontawesome5}
% 节点内
\node[iconbox] (api) {\faGlobe\quad REST API};
```

常用技术角色映射（按 teaching 色板的 10 种语义分组）：

| 语义角色 | 推荐图标命令 | 可选替代 |
|---|---|---|
| client / user | `\faUser` | `\faLaptop`、`\faMobile`、`\faDesktop` |
| service | `\faCogs` | `\faServer`、`\faCubes` |
| compute | `\faMicrochip` | `\faBrain`、`\faRobot`、`\faCode` |
| queue / event | `\faStream` | `\faShareAlt`、`\faExchangeAlt` |
| cache | `\faBolt` | `\faMemory`、`\faTachometerAlt` |
| database | `\faDatabase` | `\faHdd`、`\faFileAlt` |
| api / gateway | `\faGlobe` | `\faNetworkWired`、`\faSitemap`、`\faProjectDiagram` |
| observability | `\faChartLine` | `\faEye`、`\faBug`、`\faSearch` |
| risk / error | `\faShieldAlt` | `\faLock`、`\faKey`、`\faBug` |
| neutral / env | `\faCloud` | `\faBell`、`\faCog`、`\faEnvelope` |

Font Awesome 包的 `fontawesome5` 是本 skill 的默认 LaTeX 图标包，许可是 LPPL 1.3c（包）+ CC BY 4.0（图标），已随 TeX Live 2020+ 自带。所有可用命令见 [CTAN fontawesome5 文档](https://ctan.org/pkg/fontawesome5)。

## 图像模型路径：风格锚

在提示词中让模型按某个图标集的"风格"自绘，不要求像素复制：

```text
Use consistent icons across all nodes in the figure, drawn in a Phosphor-style
regular weight (2 px uniform stroke, soft rounded corners). Each node contains
exactly one icon on the left side, sized at ~32 px, filled with the node's
border color. Icons by role: user avatar for client, cogwheel for service,
cylindrical stack for database, lightning bolt for cache, three-node fan for
queue, globe for API gateway.
```

常用风格锚：

- **Phosphor** - 丰富度最高（9000+）、6 种 weight 可选，风格描述最具体；推荐 regular 或 bold 之一。
- **Lucide** - Feather 衍生，2 px 等线稿，气质轻盈。
- **Tabler** - 另一组线稿等宽图标，比 Lucide 的"工业设计感"稍重。
- **Material Symbols Outlined** - Google 生态；可用 wght/FILL 轴控制粗细与填充。
- **Heroicons** - Tailwind 配套；outline / solid 二选一。
- **Font Awesome Solid** - 配合 fontawesome5 LaTeX 包时作为视觉锚。

**不要混用多个风格锚**。全图图标必须风格一致，否则 teaching 派的秩序感会破坏。

## 具体公司/产品 Logo

架构图中需要 Kafka、Redis、Postgres、Docker 等具体品牌时：

- **Simple Icons** - CC0，可直接本地保存使用；文件在 CC0 下，但品牌 Logo 本身仍受公司商标法规约束。
- 在图像模型 prompt 中写 "flat silhouette logo of Apache Kafka" 等，模型会近似生成。
- 不得用品牌 Logo 暗示官方合作或默认背书。

## 可用性与许可

详细许可信息见 [sources.json](sources.json)。关键约束：

- **unDraw 不作为 AI 生成素材**，其许可明确禁止 AI 训练用途。
- **CC BY 4.0 图标集** 要求署名；Font Awesome Free 图标即其一。
- **CC BY-NC-ND 的参考图** 不得本地保存改编版本；仅可链接参考。
- **品牌 Logo** 文件可能 CC0，但品牌本身属各公司商标。

## 缺字 / Fallback

未安装 fontawesome5 时的 Unicode fallback（仅示意，不作首选）：

```text
\faUser      -> 👤
\faDatabase  -> 🗄
\faServer    -> 🖥
\faCloud     -> ☁
\faBell      -> 🔔
\faBolt      -> ⚡
\faCogs      -> ⚙
\faLock      -> 🔒
\faChartLine -> 📈
\faShieldAlt -> 🛡
```

Unicode 字符渲染跨平台差异大，仅作应急；优先使用 fontawesome5 或图像模型生成图标。
