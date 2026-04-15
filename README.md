# GHAS ゼロコスト運用プロジェクト：実装ガイド

本リポジトリは、GitHub Advanced Security (GHAS) をパブリックリポジトリで活用し、AIアプリケーション特有の脆弱性と従来のOWASP Top 10脆弱性をどのように検出し、防御するかを実演するためのデモプロジェクトです。

## 1. 料金構造とパブリックリポジトリの優位性

GHASは通常、エンタープライズ向けの有料機能ですが、**Publicリポジトリに限りすべての機能が無料で提供されます。**

| 機能 | 特徴 | 学習・運用上のメリット |
| :--- | :--- | :--- |
| **CodeQL** | 静的解析 (SAST) | セキュアコーディングの自動レビュー。PR時に指摘が入る。 |
| **Dependabot** | 依存関係解析 (SCA) | 脆弱なライブラリを検知し、自動で修正PRを作成する。 |
| **Secret Scanning** | 秘匿情報検知 | APIキー等の漏洩をPush前にブロック (Push Protection)。 |

## 2. プロジェクトコンセプト：『Vulnerable AI Swiss-Knife』

「AI搭載の便利ツール」を装いつつ、OWASP Top 10 および LLM 特有の脆弱性を凝縮した最小構成のリポジトリです。

- **OWASP Top 10 網羅**: SQLiやXSSだけでなく、AI時代の脆弱性を追加。
- **AI観点の導入**: Prompt InjectionやAI SDKの脆弱性をターゲットにする。
- **ノイズレス運用**: 無料枠を賢く使うための設定を公開。

## 3. 実装されている脆弱性のシナリオ

### A. AI Prompt Injection (LLM01)
- **機能**: ユーザー入力からAI要約を生成。
- **脆弱性**: 入力をそのままプロンプトに結合。
- **CodeQL検知対象**: `py/tainted-data-in-llm-prompt` (実験的クエリ) 相当のフロー。

### B. SSRF (A10:2021)
- **機能**: 指定したURLのドキュメントをAIに読み込ませる。
- **脆弱性**: URLのバリデーション不備により、内部NWへのアクセスを許す。
- **CodeQL検知対象**: `py/full-path-injection` などのSSRFクエリ。

### C. Cross-Site Scripting (A03:2021)
- **機能**: AIの回答（Markdown）を即座にプレビュー。
- **脆弱性**: `innerHTML` による出力（サニタイズなし）。
- **CodeQL検知対象**: `js/xss` などのクライアントサイドXSS。

## 4. 運用の流れとアラートの確認

本リポジトリを自身のパブリックリポジトリとして公開し、以下の点を確認してください。

1.  **Detection**: [Security] タブの [Code scanning] で、CodeQLがソース(入力)からシンク(危険な関数)までの経路を検出していることを確認。
2.  **Auto-Remediation**: [Pull requests] タブで、Dependabotが `requirements.txt` の古いライブラリを更新するPRを自動作成していることを確認。
3.  **Prevention**: `main.py` に含まれるダミーAPIキーを検出し、Secret Scanningが警告（またはPushブロック）を出すことを確認。

---
> [!CAUTION]
> 本プロジェクトは学習・検証用です。意図的に脆弱性が含まれているため、実際の運用環境や秘密情報を含むリポジトリと混ぜないように注意してください。
