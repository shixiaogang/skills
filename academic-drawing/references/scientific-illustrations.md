# 科研插画

## 适用范围

用于器官、细胞、材料、实验装置、环境和抽象机制等难以用规则几何完整表达的概念性图片。默认使用当前环境中已授权的图像生成能力，必要时与 TikZ 组合。

不用于生成实验数据、代表性显微图、医学影像、检测结果、观测照片或带有伪造比例尺的证据图片。

## 选择生成方式

| 内容 | 方式 |
|---|---|
| 框、箭头、文字、公式、精确拓扑 | TikZ |
| 统计数据和数值轴 | Matplotlib |
| 具象器官、细胞、材料或装置外观 | 图像模型 |
| 具象底图加精确机制标签 | 图像模型生成底图，TikZ 添加标注 |
| 可由基本几何清楚表达的示意图 | TikZ，不调用图像模型 |

## 绘图前收集

- 图片的科学目的和明确的示意性质。
- 必须出现与必须排除的对象。
- 对象数量、相对位置、视角、尺度关系和遮挡关系。
- 可视化的状态、过程和时间点。
- 允许模型自由发挥的区域。
- 需要程序化叠加的精确标签、箭头和图例。
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
Exclusions: no text, no labels, no arrows, no scale bar, no data plots, no decorative particles.
```

## 生成与迭代

1. 先生成无文字、无箭头、无比例尺的底图。
2. 检查对象数量、结构、位置、方向和科学合理性。
3. 只把具体缺陷写入下一轮提示词，例如“移除第三个细胞核”，不使用“更专业”之类空泛反馈。
4. 底图通过后，用 TikZ 添加准确标签、关系和图例。
5. 保存最终提示词、模型标识、参数、生成时间、中间版本和人工修改记录。

不要为了达到主观评分反复重绘已经正确的部分。迭代达到上限仍有科学错误时停止交付并报告问题。

## 风格

- 使用白色或透明背景，除非场景本身要求环境背景。
- 保持正交、剖面或统一透视，不混用多个消失点。
- 采用低饱和浅填充和清晰轮廓，避免发光、镜头光晕、渐变背景和海报式装饰。
- 为后续标签预留稳定空白，不在底图中生成占位乱码。
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
- 底图无乱码文字、伪标签、伪比例尺和伪数据。
- 关键文字和箭头由可编辑工具添加。
- 提示词、模型、参数和迭代记录完整。
