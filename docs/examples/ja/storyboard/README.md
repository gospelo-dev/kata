# Storyboard サンプル(日本語・漫才)

`storyboard` テンプレートを使った 4 カットの短編スクリプト例です。
仲のいい夫婦(アリスとボブ)の会話漫才で、ピクトグラムの顔が動かないことそのものをオチに使っています。

## シーン

**「あの箱」** — アリスがボブに驚愕の事実を告げ、ボブは「驚いた!」と返すが顔は変わらない。アリスは嘘だとバラすが、最後にボブの部屋にある"あの箱"の中身が気になり出す。

- **C-001**: アリスが話を振る(6 秒)。
- **C-002**: アリスが爆弾発言。ボブは無表情のまま「驚いた!」(10 秒)。
- **C-003**: アリスが嘘だと明かし、表情の分かりにくさをツッコむ(6 秒)。
- **C-004**: ボブが心拍数の戻りを報告。アリスが"あの箱"の中身を問い詰める(10 秒)。

## ファイル

| ファイル | 用途 |
|------|------|
| [`data.yml`](data.yml) | シーンのソースデータ(登場人物・カット・セリフ)。 |
| [`storyboard.kata.md`](storyboard.kata.md) | レンダリング済みの storyboard。 |
| [`images/storyboard/characters/`](images/storyboard/characters/) | キャラクターアバター(`alice.png`, `bob.png`)。 |
| [`images/storyboard/`](images/storyboard/) | カットのプレースホルダー画像(`C-001.jpg` 〜 `C-004.jpg`)。 |

## 再生成方法

```bash
gospelo-kata build storyboard data.yml -o storyboard.kata.md
```

## 画像パス規約

`data.yml` の画像参照はすべて `./images/storyboard/…` の名前空間を使用しています。これは実プロジェクトで `gospelo-kata init --type storyboard --with-assets` を実行した時に展開される構造と一致しており、別テンプレートを追加で install しても画像が衝突しません。

## Data ↔ ドキュメント ラウンドトリップ

レンダリングされた `storyboard.kata.md` は LiveMorph に対応しています:

```bash
# レンダリング結果から Data を抽出
gospelo-kata extract storyboard.kata.md

# レンダリング側で編集した内容を Data ブロックへ反映し、再レンダー
gospelo-kata sync to-data storyboard.kata.md
```

`extract` で取り出せるのは `<span data-kata="…">` でラップされた値だけです。画像の `src` 属性や隠しセリフなど、ラップされていないフィールドは `merge_extracted_into_data` によって既存の Data ブロックから保持されるため、sync を繰り返しても情報が失われません。

## 1 カット内で話者が入れ替わる表現

C-002 と C-004 では 1 カット内でアリスとボブの発話が入れ替わります。ピクトグラムでは表情差が付かないため、実際の制作では**吹き出しの左右位置**で話者を表現するのが現実的です。`notes` に運用メモを残してあります。
