# 历史 newsletter 风格参照

当前默认风格改为 [清晰技术示意图](clean-technical-style.md)。此处只保留历史迭代，不再要求深色图标底板或每个节点一行解释；必要中文说明按现行要求使用文楷。

![技术 newsletter 风格](newsletter-style.png)

本图来自 2026-10-09 用户认可的框图风格迭代，用于给模型具体的品质参考：统一 outline 语义图标与底板，醒目的标题与小一档灰色说明，主要框内同色浅深，张量等机制图元与文字共同解释内容。这张历史 PNG 的字体、色值与图标形状仅作外观参考；新复杂框图须由模型直接生成 SVG，按当前渲染规格绑定真实中文思源黑体与英文 Inter，并使用准确 Lancet 色值。

借鉴图标、标注层次、图形比例与留白，构图由新任务自主设计。优先用于跨主题品质参考；同主题自由重设计时改选其他品质图，先把科学内容抽成事实清单。图片不提供新任务的标签、维度或算法关系，机制逐图核验。

生成工具：`image_gen.imagegen`；实际模型名、seed 与采样参数未由工具暴露。完整设计与修订提示词见 [newsletter-style.prompt.txt](newsletter-style.prompt.txt)，像素与 SHA-256 见 [newsletter-style.json](newsletter-style.json)。本次生成使用用户认可的配色层次图与 skill 的 api-gateway-fanout 作品质方向参考，未复制外部参考内容或布局，原始外部图片未在本目录重分发。
