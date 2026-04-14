# Paper-Distiller（论文蒸馏器）

[English](README.md) | [中文](README_zh.md)

Paper-Distiller 将可复用的会议/期刊论文蒸馏工作流打包为工作区技能（Workspace Skill）。

本仓库包含一个技能 `venue-distillation`，用于将目标会议/期刊的已接收和被拒论文转化为结构化指导，供 AI 科研 pipeline 在创意生成、论文撰写和修改中复用。

**多学科支持：** 蒸馏引擎通过 YAML 配置支持学科专属 Schema。目前可用：计算机科学/AI（默认）和经济学/金融/管理学。新增学科只需创建 YAML 文件，无需修改代码。

## 技能功能

该技能覆盖端到端流程：

1. 从 OpenAlex、Semantic Scholar、OpenReview 采集已接收论文
2. 从 OpenReview 采集被拒论文及审稿意见
3. 将已接收论文蒸馏为严谨性、创新性和叙事三层结构化模式（Layers 1-3，LLM）
4. 将被拒论文蒸馏为审稿人关注的反模式（Layer 4，规则）
5. 提取引用与参考文献模式（Layer 5，正则 + API，无 LLM 成本）
6. 将五层结果打包为技能文件，注入 Agent pipeline

## 仓库结构

```text
.github/
  skills/
    venue-distillation/
      SKILL.md                         # 技能主入口
      references/
        collection-sources.md          # 论文采集来源
        data-schemas.md                # 数据 JSON Schema
        discipline_schema.py           # YAML Schema 加载器模块
        discipline-schemas/
          cs.yaml                      # 计算机科学/AI 默认 Schema
          economics.yaml               # 经济学/金融/管理学 Schema
        distillation-design.md         # 蒸馏设计（Layers 1-3 + Layer 5）
        multi-discipline.md            # 多学科设计文档
        openreview-api.md              # OpenReview API 指南
        rejection-analysis.md          # 拒稿分析设计
        skill-file-format.md           # 技能文件格式说明
```

## 五层蒸馏架构

```
Layer 1  Rigor Facets        → 方法论严谨性（基线对比/消融/数据集/计量方法）
Layer 2  Idea DNA            → 创新类型 + gap→hypothesis 推理
Layer 3  Narrative Structure  → 叙事模式（图表类型/讨论要素/文献综述策略）
Layer 4  Rejection Patterns   → 拒稿反模式（审稿人弱点分类）
Layer 5  Citation Patterns    → 引用网络结构（规则引擎，学科通用）
```

## 多学科 Schema 系统

蒸馏引擎的五层流水线保持不变，但各层的提取字段、prompt 模板、分类体系和聚合规则从 YAML 配置加载。

### 计算机科学/AI（`cs.yaml`，默认）

- **Layer 1**：`has_pretrained_baseline`、`has_ablation`、`has_real_data`、`reports_std` 等
- **Layer 2**：4 种创新类型 —— `incremental`、`new_formulation`、`new_application`、`paradigm_shift`
- **Layer 4**：面向 NeurIPS/ICML/ICLR 审稿模式

### 经济学/金融/管理学（`economics.yaml`）

- **Layer 1**：11 个布尔字段（稳健性检验、内生性处理、异质性分析、面板数据、固定效应等），6 个列表字段（模型类型 23 种、数据集名称、因果识别策略 9 种等），3 个整数字段（样本量、国家数、时间跨度）
- **Layer 2**：6 种创新类型 —— `new_empirical_evidence`、`new_identification_strategy`、`new_methodology`、`new_application`、`new_theoretical_mechanism`、`incremental`
- **Layer 4**：13 种经济学拒稿原因（内生性未处理、样本选择偏差、识别策略薄弱等）

### 新增学科

只需创建 `discipline-schemas/<family>.yaml`，引擎自动发现加载，无需修改代码。

## 在 GitHub Copilot 中使用

在 VS Code 中打开本仓库，启用 GitHub Copilot Chat，用自然语言提问：

```text
Use the venue-distillation skill for NeurIPS 2025 on LLM Agents.
```

经济学场景：

```text
Use the venue-distillation skill with economics schema for Energy Economics on carbon emissions estimation.
```

或更简洁地：

```text
蒸馏 NeurIPS 2025 的 LLM Agent 论文。
```

该技能会被 Copilot 自动发现，适用于以下场景：

- 论文/会议蒸馏
- 已接收 vs 被拒论文对比分析
- 基于 OpenReview 的审稿模式提取
- 为科研写作 Agent 构建技能文件

## 在 Claude 风格环境中使用

将技能目录复制到目标项目的以下路径之一：

- `.github/skills/venue-distillation/`
- `.claude/skills/venue-distillation/`
- `.agents/skills/venue-distillation/`

保留文件夹名称与 `SKILL.md` + `references/` 目录结构。

## 主入口文件

从 [.github/skills/venue-distillation/SKILL.md](.github/skills/venue-distillation/SKILL.md) 开始。

该文件描述了：

- 何时使用该技能
- 所需输入
- 五层蒸馏方法论
- 输出产物
- 蒸馏模式如何注入论文写作 pipeline

## 参考文档

- [数据 Schema](.github/skills/venue-distillation/references/data-schemas.md)：已接收/被拒论文 JSON 字段定义
- [采集来源](.github/skills/venue-distillation/references/collection-sources.md)：来源覆盖范围和采集策略
- [OpenReview API 指南](.github/skills/venue-distillation/references/openreview-api.md)：v1/v2 差异、认证、限流
- [蒸馏设计（Layers 1-3 + Layer 5）](.github/skills/venue-distillation/references/distillation-design.md)：LLM prompt、数据类、聚合逻辑、引用模式提取
- [多学科设计](.github/skills/venue-distillation/references/multi-discipline.md)：跨学科 Schema 系统
- [拒稿分析设计](.github/skills/venue-distillation/references/rejection-analysis.md)：正则模式、统计量、对比方法
- [技能文件格式](.github/skills/venue-distillation/references/skill-file-format.md)：输出技能文件的结构和标签
- [学科 Schema 目录](.github/skills/venue-distillation/references/discipline-schemas/)：各学科的 YAML 配置文件

## 设计目标

目标不仅是总结论文，而是生成可复用的结构化知识，帮助 Agent：

- 提出更强的研究想法
- 避免常见审稿人批评
- 以符合目标会议/期刊风格撰写论文
- 在审稿反馈后更有效地修改
