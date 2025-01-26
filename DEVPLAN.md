# Photoword 開発計画

## 1. 現在の実装状況

### 1-1. コア機能
- 画像アップロード機能 (JPG, JPEG, PNG対応)
- AWS Bedrock経由でのClaude Haiku (anthropic.claude-3-haiku-20240307-v1:0) による画像解析
- Pydanticモデルを使用した構造化データ処理
  - SpanishVocabulary: 単語、品詞、日本語訳、例文
  - ImageVocabularyResponse: 単語リストのコンテナ
- Streamlitベースのシンプルなユーザーインターフェース
- マークダウン形式での単語表示（スペイン語を強調表示）

### 1-2. テスト環境
- pytestによるテストフレームワーク
- 画像解析のテストケース（test1_restaurant.jpg）
- 構造化出力のテスト

## 2. 実装予定の機能（優先度順）

### Phase 1: データ永続化基盤の構築
**目標**: ユーザーデータと学習履歴を保存するための基盤を整備

#### 1-A. データベース設計と実装 (2週間)
- SQLiteデータベースの統合
  - [x] テーブル設計 (完了: 2024-01-26)
    ```sql
    -- users テーブル
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- vocabulary_entries テーブル
    CREATE TABLE vocabulary_entries (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        spanish_word TEXT NOT NULL,
        part_of_speech TEXT NOT NULL,
        japanese_translation TEXT NOT NULL,
        example_sentence TEXT NOT NULL,
        image_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (image_id) REFERENCES images(id)
    );

    -- images テーブル
    CREATE TABLE images (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        image_data BLOB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    -- learning_progress テーブル
    CREATE TABLE learning_progress (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        vocabulary_id INTEGER,
        status TEXT CHECK(status IN ('未学習','学習中','習得済み','要復習')),
        last_reviewed TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (vocabulary_id) REFERENCES vocabulary_entries(id)
    );
    ```
  - [x] SQLAlchemyモデルの実装 (完了: 2024-01-26)
    - models_db.pyにUser, Image, VocabularyEntry, LearningProgressモデルを実装
    - 外部キー制約とリレーションシップの設定
  - [x] マイグレーションスクリプトの作成 (完了: 2024-01-26)
    - Alembicを使用したマイグレーション管理
    - 自動マイグレーション生成の設定
  - [x] CRUD操作の実装とテスト (完了: 2024-01-26)
    - 基本的なCRUD操作の実装
    - トランザクション管理の実装
    - エラーハンドリングとロールバック処理

#### 1-B. セッション管理の実装 (1週間)
- [x] Streamlitセッションステートの活用 (完了: 2024-01-26)
- [x] ユーザーセッション管理の実装 (完了: 2024-01-26)
  - テストユーザー自動作成機能
  - セッション初期化と終了処理
- [x] セッションデータの永続化 (完了: 2024-01-26)
  - SQLiteデータベースとの連携
  - トランザクション管理

### Phase 2: 時系列表示機能の実装
**目標**: ユーザーの学習履歴を時系列で管理・表示

#### 2-A. 履歴管理機能 (1週間)
- [ ] 画像と単語データの紐付け
- [ ] タイムスタンプベースの並び替え
- [ ] ページネーション実装

#### 2-B. UI実装 (1週間)
- [ ] タイムライン表示コンポーネント
- [ ] フィルタリング機能
- [ ] 詳細表示モーダル

### Phase 3: クイズ機能の実装
**目標**: インタラクティブな学習機能の提供

#### 3-A. クイズエンジンの実装 (2週間)
- [ ] クイズ生成ロジック
  - スペイン語→日本語
  - 日本語→スペイン語
  - 例文穴埋め
- [ ] 正答判定システム
- [ ] 進捗データの記録

#### 3-B. クイズUIの実装 (1週間)
- [ ] クイズ表示コンポーネント
- [ ] 結果表示画面
- [ ] 復習モード

### Phase 4: 単語帳編集機能
**目標**: ユーザーによる単語帳のカスタマイズを可能に

#### 4-A. 編集機能の実装 (1週間)
- [ ] 単語情報の編集フォーム
- [ ] バリデーション処理
- [ ] 変更履歴の管理

#### 4-B. UI実装 (1週間)
- [ ] インラインエディタ
- [ ] 一括編集機能
- [ ] 変更履歴表示

### Phase 5: 学習進捗管理機能
**目標**: 学習状況の可視化と分析

#### 5-A. 進捗トラッキング (1週間)
- [ ] 学習ステータス管理
- [ ] 復習タイミングの計算
- [ ] 学習データの集計

#### 5-B. 分析・表示機能 (1週間)
- [ ] 進捗グラフの実装
- [ ] 学習統計の表示
- [ ] レコメンデーション機能

## 3. テスト戦略

### 3-1. 単体テスト
- 各コンポーネントのpytestケース作成
- モックを使用したAI/DB操作のテスト
- バリデーションテスト

### 3-2. 統合テスト
- エンドツーエンドテスト
- ユーザーフロー検証
- パフォーマンステスト

### 3-3. UI/UXテスト
- レスポンシブデザインテスト
- アクセシビリティテスト
- ユーザビリティテスト

## 4. 開発環境・ツール

### 4-1. 必要なパッケージ
```txt
# requirements.txtに追加予定
SQLAlchemy==2.0.27
alembic==1.13.1
pytest-cov==4.1.0
pytest-mock==3.12.0
```

### 4-2. 開発ツール
- VSCode + Python拡張
- SQLite Browser
- pytest + coverage.py

## 5. デプロイメント計画

### 5-1. 開発環境
- ローカル開発環境のセットアップ手順
- テストデータの準備

### 5-2. 本番環境
- デプロイメントチェックリスト
- バックアップ戦略
- モニタリング計画

## 6. マイルストーン

### Phase 1 (3週間) - ✅ 完了
- データベース設計・実装 (完了: 2024-01-26)
  - SQLiteデータベース設定
  - SQLAlchemyモデル実装
  - Alembicマイグレーション設定
- セッション管理実装 (完了: 2024-01-26)
  - Streamlitセッション統合
  - ユーザー管理機能
- 基本的なCRUD操作の実装 (完了: 2024-01-26)
  - 画像・単語データの永続化
  - エラーハンドリング実装

### Phase 2 (2週間)
- 時系列表示機能の実装
- UIコンポーネントの作成

### Phase 3 (3週間)
- クイズ機能の実装
- クイズUIの作成
- テストケースの作成

### Phase 4 (2週間)
- 編集機能の実装
- 変更履歴管理の実装

### Phase 5 (2週間)
- 進捗管理機能の実装
- 分析機能の実装

## 7. 参考資料

### 7-1. 技術文書
- [Streamlit Documentation](https://docs.streamlit.io/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### 7-2. プロジェクト文書
- [README.md](./README.md)
- [SPECIFICATION.md](./SPECIFICATION.md)
- [models.py](./models.py)
