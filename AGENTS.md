# AGENTS.md — Liftdex / CodeX 初回共有（完全版）

> このファイルは、CodeX（開発支援AI/エージェント）に Liftdex プロジェクトの前提・要件・設計方針を**漏れなく**伝達するためのドキュメントです。
> Django SSR で最短でMVPを完成させ、後で段階的に拡張します。

---

## 0. プロジェクト基本情報
- **プロダクト名**: Liftdex
- **種別**: 筋トレ how-to（フォーム確認）特化 Webアプリ
- **目的**: 筋トレ中の「種目フォーム/注意点/参考動画」の検索時間を短縮する（即時参照・迷わないUI）
- **ターゲット**: ジム利用者（モバイルブラウザ想定）
- **技術**:
  - Python
  - Django（SSR中心・標準機能中心）
  - DB: SQLite（MVP）
  - 画像: `ImageField`（必要に応じて）
- **設計思想**:
  - MVPは **Djangoの標準機能をフル活用**し、独自JSを最小化
  - UIは筋トレ中でも読めるよう **タグ/カード/箇条書き**で構成
  - データ投入はまず Admin を整える（運用が回る形が最優先）
- **非目標（MVPではやらない）**:
  - 複雑なレコメンド（機械学習など）
  - メール認証・SNSログイン（必要なら後で）
  - リアルタイム更新（SPA化など）

---

## 1. 機能要件（MVP）
### 1.1 必須機能
- 検索機能（種目名/英語名/関連筋肉名）
- 会員登録 / ログイン / ログアウト
- ブックマーク機能（ユーザーごとに種目を保存）
- コメント機能（参考になったフォーム動画リンク等の共有ログ）

### 1.2 画面要件（表示内容）
#### 共通（デフォルト表示）
- ロゴ
- サイト名（アプリ名）
- ハンバーガーメニュー

#### Top
- 検索バー
- ブックマークした種目（最大3件）
- 人気種目（閲覧回数 `view_count` 上位）

#### 種目詳細
- 種目名
- 主動筋肉 / 補助筋肉
- フォーム参考動画（複数）
- Tips
- 目的別推奨レップ数（筋力アップ / 筋肥大 / 筋持久力）
- 代替種目
- コメントログ（アカウント名、リンク、コメント）

#### 筋肉一覧
- 胸
  - 大胸筋
  - 大胸筋上部
  - 大胸筋下部
- 背中
  - 広背筋
  - 僧帽筋
  - 脊柱起立筋
  - 菱形筋
  - 大円筋
- etc（筋群→筋肉の階層構造）

#### 筋肉詳細（例：大胸筋）
- 筋肉構造の画像
- 筋肉の説明
- 関連種目（種目名）

#### アカウント画面
- ブックマーク種目一覧（最上段に表示）
- アカウント詳細

---

## 2. URL/画面設計（想定）
- `/` : Top（検索・ブクマ3件・人気）
- `/exercises/` : 種目一覧（検索結果もここに集約、GETクエリで絞り込み）
- `/exercises/<slug>/` : 種目詳細
- `/muscles/` : 筋肉一覧（筋群→筋肉）
- `/muscles/<slug>/` : 筋肉詳細
- （必要なら）`/muscle-groups/` : 筋群一覧
- 認証:
  - `/accounts/signup/`
  - `/accounts/login/`
  - `/accounts/logout/`
  - `/accounts/me/`

> 検索は「Topの検索バー → `/exercises/?q=...`」のGET遷移を基本とする。

---

## 3. データ設計（確定事項）
### 3.1 slug の扱い（重要）
- `slug` は **各モデル内で一意**（`unique=True`）
- **筋群と筋肉で slug が同じでもOK**
  - 理由: `MuscleGroup` と `Muscle` は別テーブルなので衝突しない
  - 例: `MuscleGroup.slug="chest"` と `Muscle.slug="chest"` は共存可能
- URLで衝突回避できる（例：`/muscle-groups/chest/` と `/muscles/chest/`）

### 3.2 Difficulty（難易度）
- 難易度は **1〜5 の5段階**
- 実装は `IntegerChoices` + `PositiveSmallIntegerField` を推奨

### 3.3 Equipment（器具）
- 器具は choices 管理
- 例の候補（MVP）:
  - barbell / dumbbell / smith / machine / plate_loaded / cable / bodyweight / other

---

## 4. 相談事項への結論（確定方針）
### 4.1 同名だが器具が違う種目（例：ケーブルシーテッドロウ vs プレートロードシーテッドロウ）
- **MVPでは「完全別種目（別Exercise）」として扱う**
  - 理由: 動画・tips・代替・レップ推奨・フォーム注意点が器具で変わるため、データと表示を分離した方が事故らない
- ただし「同一種目グループ」としてまとめて見せたいので、
  - `base_exercise`（自己参照FK）で **親子（ファミリー）** を作る
  - 詳細画面で “器具切替” UI（兄弟variantへのリンク）を表示する
- 制約:
  - `Exercise.name` は **uniqueにしない**（同名許可）
  - `(name, equipment)` の **複合ユニーク制約**を付ける（同名×同器具の重複のみ禁止）
- slug 生成:
  - **器具違いで衝突しないよう** `"{slugify(name)}-{equipment}"` を推奨
  - 例: `seated-row-cable` / `seated-row-plate_loaded`

---

## 5. モデル一覧（MVP：確定モデル）
### 5.1 Muscle系
- `MuscleGroup`
  - 胸/背中/腕/脚 など
  - fields: `name`, `slug(unique)`, `sort_order`
- `Muscle`
  - 大胸筋/広背筋…など
  - fields: `group(FK)`, `name`, `slug(unique)`, `description`, `structure_image`, `sort_order`
  - constraint: `(group, name)` unique（同一筋群内で筋肉名が重複しない）

### 5.2 Exercise系
- `Exercise`
  - fields（コア）:
    - `name`（uniqueではない）
    - `english_name`
    - `slug(unique)`
    - `difficulty`（1〜5）
    - `equipment`（choices）
    - `exercise_type`（compound/isolation）
    - `primary_muscles`（M2M → Muscle）
    - `secondary_muscles`（M2M → Muscle）
    - `tips`
    - `view_count`
    - `base_exercise`（self FK：variantsグルーピング用。null/blank可）
    - `created_at`, `updated_at`
  - constraints:
    - `UniqueConstraint(name, equipment)`（同名×同器具の重複禁止）
  - slug方針:
    - デフォルトは `name + equipment` を含める

- `ExerciseVideo`
  - fields: `exercise(FK)`, `title`, `url`, `is_recommended`, `sort_order`

- `RepRecommendation`
  - 目的別推奨レップ数
  - fields: `exercise(FK)`, `goal(strength/hypertrophy/endurance)`, `rep_min`, `rep_max`, `note`
  - constraint: `(exercise, goal)` unique

- `ExerciseAlternative`
  - 代替種目（自己参照ManyToManyのthrough）
  - fields: `from_exercise(FK)`, `to_exercise(FK)`, `note`, `sort_order`
  - constraint: `(from_exercise, to_exercise)` unique

### 5.3 Social系
- `Bookmark`
  - fields: `user(FK)`, `exercise(FK)`, `created_at`
  - constraint: `(user, exercise)` unique

- `Comment`
  - fields: `user(FK)`, `exercise(FK)`, `content(Text)`, `created_at`
  - contentには「参考動画リンク + コメント」を含める想定（MVP）
  - （将来拡張）必要なら `url` 専用フィールドを追加可能

---

## 6. 実装方針（Django / SSR）
### 6.1 開発順（MVP）
1. Models確定 → Migrations
2. Admin登録（データ投入を最優先）
   - 動画/レップ/代替はインライン編集できると良い
3. 種目一覧/詳細（関連M2M、動画、レップ、代替、コメント）
4. 検索（Top→一覧GET）
5. 認証（signup/login/logout）
6. ブックマーク（トグル、Top3、マイページ一覧）
7. 人気（詳細表示時に `view_count` をインクリメントしTopに表示）

### 6.2 パフォーマンス（最低限の指針）
- 一覧/詳細で `select_related` / `prefetch_related` を使用
- まずは運用データ規模が小さい前提で最適化は段階的

---

## 7. UI/UX（筋トレ中前提の原則）
- 長文より、タグ・カード・箇条書きを優先
- 詳細ページの情報階層:
  1) 種目名
  2) 主動/補助筋（タグ）
  3) 参考動画（おすすめ優先）
  4) Tips
  5) 目的別レップ
  6) 代替種目
  7) コメント

---

## 8. 既知の拡張候補（将来）
- 検索：PostgreSQL導入後に全文検索（GIN + SearchVector）
- 人気：期間（7日/30日）ランキング
- コメント：URL専用フィールド追加、スパム対策
- 動画：埋め込み表示や検証（YouTube等）

---
