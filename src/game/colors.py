"""
カラーパレット定義モジュール。

ゲームで使用するカスタムカラーを定義する。
Pyxelのパレット（0-15）を再定義して独自の色を使用可能にする。
"""

# カラーインデックス定義（Pyxelのパレットインデックス 0-15）
COLOR_BACKGROUND = 0  # 背景色
COLOR_WALL = 5  # 壁
COLOR_SAND = 9  # 砂
COLOR_WATER = 12  # 水
COLOR_OIL = 10  # 油
COLOR_FIRE = 14  # 火
COLOR_UI_TEXT = 7  # UIテキスト
COLOR_UI_BUTTON = 6  # UIボタン
COLOR_UI_BUTTON_HOVER = 8  # UIボタン（ホバー時）
COLOR_UI_BORDER = 13  # UIボーダー
COLOR_UI_SELECTED = 10  # 選択状態（明るい緑）
COLOR_UI_SELECTED_BG = 11  # 選択状態の背景
COLOR_UI_HELP_TEXT = 5  # ヘルプテキスト（控えめな色）

# カスタムカラー定義（0xRRGGBB形式）
# 背景・空
PALETTE_BACKGROUND = 0x1A1A2E  # 暗い青紫（夜空のイメージ）

# 壁・岩
PALETTE_WALL = 0x4A4A5C  # 暗い灰色

# 砂
PALETTE_SAND = 0xE6C86E  # 明るい砂色

# 水
PALETTE_WATER = 0x4A90D9  # 鮮やかな青

# 油
PALETTE_OIL = 0x3D2914  # 暗い茶色

# 火
PALETTE_FIRE = 0xFF6B00  # オレンジの炎

# UI関連の色
PALETTE_UI_TEXT = 0xFFFFFF  # 白（テキスト）
PALETTE_UI_BUTTON = 0x3A3A5C  # 暗い紫灰（ボタン背景）
PALETTE_UI_BUTTON_HOVER = 0x5A5A8C  # 明るい紫灰（ホバー時）
PALETTE_UI_BORDER = 0x7A7AAC  # 明るめの紫灰（ボーダー）

# 追加色（予備）
PALETTE_ACCENT = 0xFF6B6B  # アクセントカラー（赤）
PALETTE_SUCCESS = 0x6BCB77  # 成功色（緑）
PALETTE_WARNING = 0xFFD93D  # 警告色（黄色）
PALETTE_DARK = 0x0F0F1A  # 最も暗い色

# カラーパレット全体の定義
# インデックス順に色を定義（0-15）
CUSTOM_PALETTE: dict[int, int] = {
    0: PALETTE_BACKGROUND,  # 背景
    1: PALETTE_DARK,  # 最も暗い色
    2: PALETTE_ACCENT,  # アクセント（赤）
    3: PALETTE_WARNING,  # 警告（黄色）
    4: PALETTE_SUCCESS,  # 成功（緑）
    5: PALETTE_WALL,  # 壁
    6: PALETTE_UI_BUTTON,  # UIボタン
    7: PALETTE_UI_TEXT,  # UIテキスト
    8: PALETTE_UI_BUTTON_HOVER,  # UIボタン（ホバー）
    9: PALETTE_SAND,  # 砂
    10: PALETTE_OIL,  # 油
    11: 0x228B22,  # 森林緑（将来の植物素材用）
    12: PALETTE_WATER,  # 水
    13: PALETTE_UI_BORDER,  # UIボーダー
    14: PALETTE_FIRE,  # 火
    15: 0xFFFFFF,  # 純白
}


def apply_custom_palette() -> None:
    """
    カスタムパレットをPyxelに適用する。

    pyxel.init()の後、pyxel.run()の前に呼び出す必要がある。
    """
    import pyxel

    for index, color in CUSTOM_PALETTE.items():
        pyxel.colors[index] = color
