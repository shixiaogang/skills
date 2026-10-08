# 第三方素材说明

本目录下 18 张参考图均为用户上传素材。原始出处与许可状态：

| 子目录 | 文件数 | 原始出处 | 许可状态 |
|---|---:|---|---|
| architecture/ | 8 | System Design Classroom newsletter (`newsletter.systemdesignclassroom.com`) | newsletter 本体未在图页明确标注开源许可 |
| flow/ | 3 | 同上 | 同上 |
| comparison/ | 4 | 同上 | 同上 |
| neural-network/ | 1 | 常见教材/讲义 CNN 示意图 | 原始作者与许可无法确定 |
| neural-network/ | 2 | Vaswani et al., "Attention Is All You Need", NeurIPS 2017（arXiv [1706.03762](https://arxiv.org/abs/1706.03762) Figure 1 & 2） | arXiv perpetual non-exclusive license to distribute；学术/教学合理引用通常可接受，正式再分发需引用原论文 |

本仓库对这些图的立场：

- 保留原图作为风格参考与审美对照素材，不作重分发（即不建议在 npm 包、Docker 镜像或衍生数据集中发布本目录）。
- 不作任何改编版本。所有生成产物由模型自绘，不复制其视觉元素。
- 若 skill 公开发布，`publish` 前需做以下之一：（a）取得原作者许可或引用原论文；（b）替换为按 [sources.json](sources.json) 借鉴清单自绘的参考图。
- 当前仓库仅在团队内部与本 skill 的对话中引用这些图。

## 候选第三方来源及许可约束

调研阶段评估过以下来源，均未保存到本目录。使用它们或从中生成新图时请遵守对应条款：

| 项目 | 许可 | 可做 | 不可做 |
|---|---|---|---|
| [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) | CC BY 4.0 | 可本地保存、改编、再分发；需署名 | 不得去除署名 |
| [ByteByteGo/system-design-101](https://github.com/ByteByteGoHq/system-design-101) | CC BY-NC-ND 4.0 | 仅可链接参考 | 不得本地保存、修改、商用、分发修改版 |
| [karanpratapsingh/system-design](https://github.com/karanpratapsingh/system-design) | CC BY-NC-ND 4.0 | 仅可链接参考 | 不得本地保存修改版、商用、分发修改版 |
| [unDraw](https://undraw.co/) | unDraw License（有附加条款） | 可用于插画资产 | 不得用于 AI 训练/生成 |

## 图标集许可

见 [../assets/icons/sources.json](../assets/icons/sources.json)。TikZ 代码路径默认使用 `fontawesome5` CTAN 包（LPPL 1.3c + CC BY 4.0），图标调用无需本地 SVG。
