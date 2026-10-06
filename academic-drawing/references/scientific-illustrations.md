# 科研插画

## 适用范围

用于器官、细胞、材料、实验装置、环境和抽象机制等概念性图片。默认使用当前环境中已授权的图像生成能力，按 [图像模型工作流](image-model-workflow.md) 生成和修订；需要稳定的复杂文字或公式时，可选用可编辑 SVG 或 LaTeX 标注层；用户指定原生文字时继续模型编辑。

本文件的独立标注层均为可选方案；用户明确要求模型原生文字时，保留原生文字并通过模型编辑修订，不擅自留白、覆盖文字或添加标注层。

不用于生成实验数据、代表性显微图、医学影像、检测结果、观测照片或带有伪造比例尺的证据图片。

## 选择生成方式

| 内容 | 方式 |
|---|---|
| 复杂结构、机制、器官、细胞、材料或装置示意 | 图像模型；短标签和箭头可直接生成并逐项核验 |
| 函数曲线、柱状图、统计数据和数值轴 | Matplotlib |
| 复杂中文、公式或长期需要编辑的精确标签 | 图像模型；可按任务选用可编辑 SVG 或 LaTeX 标注层 |
| 少量节点、单层结构、短标签、简单连线的框图 | TikZ |
| 用户明确要求 TikZ 或局部维护已有 TikZ 图 | 按用户要求或已有工程实施 |

## 绘图前收集

- 图片的科学目的和明确的示意性质。
- 必须出现与必须排除的对象。
- 对象数量、相对位置、视角、尺度关系和遮挡关系。
- 可视化的状态、过程和时间点。
- 允许模型自由发挥的区域。
- 短标签和箭头的准确清单，以及需要可编辑叠加的复杂文字、公式和图例。
- 目标比例、背景和最终尺寸。

## 提示词结构

按以下顺序构造提示词：

```text
Purpose:
Subject and required objects:
Spatial composition and viewpoint:
Scientific state and relationships:
Visual treatment:
Background and output framing:
Explicit exclusions:
```

有效提示词应具体描述对象和空间，不使用“高端”“震撼”“顶刊风格”等无法验证的形容词。

示例：

```text
Purpose: conceptual overview of nanoparticle delivery across an intestinal barrier.
Subject: one cross-section of epithelial cells, mucus layer, nanoparticles, and capillary.
Composition: left-to-right transport, orthographic cutaway, generous empty space above.
Treatment: restrained scientific illustration, flat lighting, clear material boundaries.
Background: white, landscape composition.
Exclusions: no scale bar, no data plots, no decorative particles, no invented anatomical structures.
Labels and relationships: use only the verified labels and transport directions supplied in the brief;
if editable overlays are requested, leave stable empty space and omit those labels from the base image.
```

## 生成与迭代

1. 按已核实的简报生成完整示意图；短标签和箭头可直接生成。复杂中文、公式或需要编辑的标注可提前规划独立排版；用户指定原生文字时保持模型生成与编辑。
2. 逐对象、逐标签、逐关系检查数量、结构、位置、方向和科学合理性；不能仅凭整体外观验收。
3. 只把具体缺陷写入下一轮提示词，例如“移除第三个细胞核”，不使用“更专业”之类空泛反馈。
4. 标注需要叠层时，生成预留空白的底图，再用可编辑 SVG 或 LaTeX 添加准确文字、公式、关系和图例，不要求使用 TikZ。
5. 保存最终提示词、实际可获取的模型标识与参数、生成时间、中间版本和修改记录；工具未提供的字段注明未提供，不编造。

不要为了达到主观评分反复重绘已经正确的部分。连续修订无改善、工具失败或关键事实无法核实时，保留最佳版本、生成记录和设计材料，说明具体问题；仍有科学错误的图不能称为完成或可投稿。

## 风格

- 使用白色或透明背景，除非场景本身要求环境背景。
- 保持正交、剖面或统一透视，不混用多个消失点。
- 采用低饱和浅填充和清晰轮廓，避免发光、镜头光晕、渐变背景和海报式装饰。
- 需要叠加标注时，为后续标签预留稳定空白；完整图直接生成的标签也不能出现乱码或占位文字。
- 同一组插画保持视角、光照、轮廓和材质表现一致。
- 不生成品牌标识、受版权保护的角色或来源不明的素材拼贴。

## 真实性边界

- 不生成“代表性”实验图或补齐缺失实验。
- 不在生成图中加入虚构样本编号、剂量、时间、比例尺或统计值。
- 不能确认的结构和机制标记 `[待核实来源]`。
- 概念图在图注中明确写明是 schematic、conceptual illustration 或示意图。
- 若目标期刊要求披露生成式 AI，保留并提供完整生成记录。

## 验收

- 图片不会被读者误认为实验或观测证据。
- 所有必需对象出现且数量正确，禁止对象未出现。
- 结构、方向、尺度关系和视角没有科学错误。
- 最终图无乱码文字、伪标签、伪比例尺和伪数据。
- 每个关键文字和箭头已对照简报核验；使用标注叠层时同时保留可编辑源文件。
- 提示词、可获取的模型与参数信息、生成时间和迭代记录可追溯。
