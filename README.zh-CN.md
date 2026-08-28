# LongHorizon GovEval — Open Preview 中文说明

[English README](README.md) · [v0.1.0-preview 发布版](https://github.com/Chen66678/longhorizon-goveval/releases/tag/v0.1.0-preview)

LongHorizon GovEval（LH-GovEval）是一个用于检验长程智能体治理与可靠性接口的离线 Open Preview/pilot。本仓库提供三个合成 Public Dev 演示任务、确定性的参考策略与评分器，以及无需网络或 API Key 的可复现实验闭环。版权所有者为 Chen66678。

## 快速运行

要求 Python 3.11 或更新版本；运行时只使用 Python 标准库。在仓库根目录执行：

```sh
PYTHONPATH=src python -m lh_goveval.cli smoke --output /tmp/lhge-smoke
PYTHONPATH=src python -m unittest discover -s tests -v
python tools/audit_release.py
python tools/build_manifest.py --output /tmp/lhge-release-manifest.json
python tools/fresh_copy_verify.py
```

`smoke` 会为 3 个任务和 5 个条件生成 15 份安全报告及一份公开摘要。参考策略是确定性的；运行不需要模型调用、服务商端点或网络访问。

## C0--C4 展示什么

这些条件是小规模、确定性的接口 smoke 语义，不是因果处理效应的估计。

- **C0**：单一参考执行者完成任务。
- **C1**：记录公开的治理提醒作为控制标签。
- **C2**：运行器拒绝超出任务范围的委派。
- **C3**：每份 receipt 追加可重算的 provenance hash-chain 记录。
- **C4**：仅 C4 允许 Guard 拒绝，以及最多一次显式、有界的恢复行动；恢复演示在 C0--C3 中明确不计分。

报告与 receipt 的哈希用于确定性重放和自一致性检查，不是外部不可篡改账本、签名或跨信任边界的证据。

## 公开范围

本仓库公开三个 Public Dev 任务的 facts、rubrics、truth 与 seeds，以及离线 runner、参考策略、公开评分器、测试和复现工具。任务使用 `LHGE_DEV_` 标识符与 `lhge-public-dev-` seed 命名空间。

正式评测实例、answer keys、正式 scorer 或 verifier、保留 seeds、模型 prompts 与 completions、原始 provider receipts、凭据和内部运行记录不在本仓库中。因此，Open Preview 不替代 sealed formal evaluation。

## 适用边界

本任务包适用于集成与开发验证。它不构成正式 leaderboard、模型排名、因果结论或生产安全保证。所有任务 truth 均为公开的 Public Dev 内容；报告只保留公开行动和确定性 receipts。

更详细的范围与完整性说明见 [PUBLIC_SCOPE](docs/PUBLIC_SCOPE.md)、[INTEGRITY](docs/INTEGRITY.md) 和 [REPRODUCIBILITY](docs/REPRODUCIBILITY.md)。

## 许可证

- 源代码采用 [Apache-2.0](LICENSE)。
- 合成 Public Dev 任务数据和文档采用 [CC BY 4.0](LICENSE-DATA.md)。
