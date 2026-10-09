# 图标资产

主要角色与功能模块默认使用统一 Lucide outline 图标和同色较深底板，配醒目标题与灰色短说明；纯数学算子或无准确图标的对象可省略。不能为方便编译而在 TikZ 还原时整批删除设计稿图标。

本目录是本 skill 的图标使用参考。图标语义与设计稿风格**优先 Lucide**，Lucide 无对应项时退用 **Font Awesome 7 regular / outline**。TikZ 端优先复用 Lucide SVG；Font Awesome 7 的 LaTeX 命令暂由 `fontawesome5` 宏包兼容实现。映射表见 [diagram-render §4.2.4](../../references/diagram/diagram-render.md#424-图标代码路径)。

## 路径选择

| 路径 | 使用方式 | 为什么 |
|---|---|---|
| TikZ / LaTeX 首选 | Lucide SVG → `\includesvg` 或预转 PDF 后 `\includegraphics` | 与设计稿的 Lucide outline 风格最一致 |
| TikZ / LaTeX 兜底 | Font Awesome 7 regular / outline；命令暂由 `\usepackage{fontawesome5}` 提供 | TeX Live / MiKTeX 自带，节点内直接插入 |
| 图像大模型路径 | 提示词里写 Lucide 语义名 + `"Lucide outline icon, thin uniform stroke"` | 模型自绘，风格轻盈统一 |

## 代码路径：Lucide 优先，Font Awesome 7 兜底

Lucide SVG 示例：

```latex
\usepackage{svg}
\node[inner sep=0pt] (apiicon) {\includesvg[width=5mm]{assets/icons/lucide/globe.svg}};
```

Font Awesome 7 兜底示例（底层宏包名暂为 `fontawesome5`）：

```latex
\usepackage{fontawesome5}
\node (apiicon) {\faGlobe};
```

常用技术角色映射：

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

Lucide 使用 ISC/MIT 许可，图标以轻量 outline 线稿为主。Font Awesome Free 图标使用 CC BY 4.0，LaTeX `fontawesome5` 宏包使用 LPPL 1.3c；这里的宏包名只是实现细节，不代表设计稿优先使用 Font Awesome 5。

## 图像模型路径：风格锚

在提示词中让模型按某个图标集的"风格"自绘，不要求像素复制：

```text
Use consistent Lucide outline icons across all nodes in the figure: thin,
uniform stroke, no fill, no rounded/filled Material style. Icons by role:
user for client, settings for service, database for persistence, cpu for
compute, workflow for pipeline, network for routing, cloud for remote.
If Lucide has no suitable icon, use a Font Awesome 7 regular/outline icon.
```

常用风格锚：

- **Lucide（首选）** - Feather 衍生，细线、等线宽、气质轻盈；设计稿和 TikZ SVG 都优先使用。
- **Font Awesome 7 regular / outline（兜底）** - Lucide 无对应图标时使用；避免 solid 填充风格。
- **Phosphor** - 仅当 Lucide 和 Font Awesome 7 都缺少对应语义时考虑。
- **Tabler** - 另一组线稿等宽图标，比 Lucide 的"工业设计感"稍重。
- **Heroicons** - Tailwind 配套；outline / solid 二选一。

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

Lucide SVG 与 Font Awesome 7 兼容命令都不可用时的 Unicode fallback（仅示意，不作首选）：

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

Unicode 字符渲染跨平台差异大，仅作应急；优先使用 Lucide SVG，其次 Font Awesome 7 regular / outline。
