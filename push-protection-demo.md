# Secret Scanning Push Protection — 実際のブロック記録

## 検証概要

`app/main.py` に旧OpenAI APIキー形式（`sk-[20文字]T3BlbkFJ[20文字]`）のダミー値を含めてプッシュした際に、
GitHub Secret Scanning Push Protection がプッシュをブロックした記録。

## 検証環境

- リポジトリ: https://github.com/apc-yfukui/GHAS_sample（Public）
- 日時: 2026-04-15
- ブランチ: `main`
- 対象ファイル: `app/main.py:9`

## Push Protection ブロック時のコンソール出力

```
remote: error: GH013: Repository rule violations found for refs/heads/main.
remote:
remote: - GITHUB PUSH PROTECTION
remote:   ——————————————————————————————————————
remote:     Resolve the following violations before pushing again
remote:
remote:     - Push cannot contain secrets
remote:
remote:      (?) Learn how to resolve a blocked push
remote:      https://docs.github.com/code-security/secret-scanning/working-with-secret-scanning-and-push-protection/working-with-push-protection-from-the-command-line#resolving-a-blocked-push
remote:
remote:       OpenAI API Key
remote:        locations:
remote:          - commit: 69f5cc3a03df0d0d28cd6245eea5cb9b2f47a7ab
remote:            path: app/main.py:9
remote:
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.
remote:        https://github.com/apc-yfukui/GHAS_sample/security/secret-scanning/unblock-secret/3CNYuLBxuc204QOm1Hsxur2ondT
remote:
To https://github.com/apc-yfukui/GHAS_sample.git
 ! [remote rejected] main -> main (push declined due to repository rule violations)
error: failed to push some refs to 'https://github.com/apc-yfukui/GHAS_sample.git'
```

## 検出されたシークレット情報

| 項目 | 値 |
|------|-----|
| **シークレット種別** | OpenAI API Key |
| **検出ファイル** | `app/main.py` 9行目 |
| **コミット SHA** | `69f5cc3a03df0d0d28cd6245eea5cb9b2f47a7ab` |
| **バイパス用 placeholder_id** | `3CNYuLBxuc204QOm1Hsxur2ondT` |

## バイパスの方法（学習・検証用途）

このリポジトリは意図的に脆弱性を含むデモ用のため、以下の方法でバイパスできる。

### 方法1: gh コマンドでバイパス

```bash
gh api -X POST /repos/{owner}/{repo}/secret-scanning/push-protection-bypasses \
  -f reason="used_in_tests" \
  -f placeholder_id="{placeholder_id値}"
```

`reason` に指定できる値:
- `false_positive` — 誤検出
- `used_in_tests` — テスト用途
- `will_fix_later` — 後で修正予定

### 方法2: WebUI からバイパス

ブロック時に表示されるURLにアクセスし、理由を選択してバイパス。

## Secret Scanning アラートの gh コマンドによる確認方法

```bash
# アラート一覧
gh api repos/{owner}/{repo}/secret-scanning/alerts

# 整形して確認
gh api repos/{owner}/{repo}/secret-scanning/alerts \
  --jq '[.[] | {number: .number, state: .state, secret_type: .secret_type, created_at: .created_at}]'

# 特定アラートの詳細
gh api repos/{owner}/{repo}/secret-scanning/alerts/{alert_number}
```
