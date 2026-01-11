"""
ボタンUIコンポーネントモジュール。

クリック可能なボタンを実装する。
"""

from collections.abc import Callable

import pyxel

from game.colors import (
    COLOR_UI_BORDER,
    COLOR_UI_BUTTON,
    COLOR_UI_SELECTED,
    COLOR_UI_SELECTED_BG,
    COLOR_UI_TEXT,
)
from game.ui.base import UIElement


class Button(UIElement):
    """
    ボタンUIコンポーネント。

    クリック時にコールバックを実行するボタン。
    Observerパターンでクリックイベントを通知する。

    Attributes:
        label (str): ボタンのラベルテキスト
        color (int): ボタンの背景色
        text_color (int): テキスト色
        selected (bool): 選択状態
        on_click (Callable[[], None] | None): クリック時のコールバック
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        label: str = "",
        color: int = 5,
        text_color: int = 7,
        on_click: Callable[[], None] | None = None,
    ) -> None:
        """
        ボタンを初期化する。

        Parameters:
            x (int): X座標
            y (int): Y座標
            width (int): 幅
            height (int): 高さ
            label (str): ボタンのラベル
            color (int): 背景色
            text_color (int): テキスト色
            on_click (Callable[[], None] | None): クリック時コールバック
        """
        super().__init__(x, y, width, height)
        self.label = label
        self.color = color
        self.text_color = text_color
        self.selected = False
        self.on_click = on_click
        self._hovered = False

    def update(self) -> None:
        """
        ボタンの状態を更新する。

        マウス入力を処理し、ホバー・クリック状態を更新する。
        """
        if not self.visible or not self.enabled:
            return

        # マウスホバー判定
        self._hovered = self.contains_point(pyxel.mouse_x, pyxel.mouse_y)

        # クリック判定
        if self._hovered and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.on_click is not None:
                self.on_click()

    def draw(self) -> None:
        """
        ボタンを描画する。

        選択状態・ホバー状態に応じて見た目を変更する。
        """
        if not self.visible:
            return

        # 背景色を決定
        bg_color = self.color
        if self.selected:
            bg_color = COLOR_UI_SELECTED_BG  # 選択時は明るい色
        elif self._hovered and self.enabled:
            bg_color = COLOR_UI_BUTTON  # ホバー時は中間色

        # 背景を描画
        pyxel.rect(self.x, self.y, self.width, self.height, bg_color)

        # 枠を描画
        border_color = COLOR_UI_TEXT if self.selected else COLOR_UI_BORDER
        pyxel.rectb(self.x, self.y, self.width, self.height, border_color)

        # ラベルを描画（中央揃え）
        if self.label:
            text_width = len(self.label) * 4
            text_x = self.x + (self.width - text_width) // 2
            text_y = self.y + (self.height - 5) // 2
            pyxel.text(text_x, text_y, self.label, self.text_color)


class ColorButton(UIElement):
    """
    カラー表示ボタンUIコンポーネント。

    マテリアルの色を表示するボタン。
    テキストの代わりに色のプレビューを表示する。

    Attributes:
        display_color (int): 表示する色
        selected (bool): 選択状態
        on_click (Callable[[], None] | None): クリック時のコールバック
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        display_color: int = 7,
        label: str = "",
        on_click: Callable[[], None] | None = None,
    ) -> None:
        """
        カラーボタンを初期化する。

        Parameters:
            x (int): X座標
            y (int): Y座標
            width (int): 幅
            height (int): 高さ
            display_color (int): 表示する色
            label (str): ボタンのラベル
            on_click (Callable[[], None] | None): クリック時コールバック
        """
        super().__init__(x, y, width, height)
        self.display_color = display_color
        self.label = label
        self.selected = False
        self.on_click = on_click
        self._hovered = False

    def update(self) -> None:
        """
        ボタンの状態を更新する。

        マウス入力を処理し、ホバー・クリック状態を更新する。
        """
        if not self.visible or not self.enabled:
            return

        self._hovered = self.contains_point(pyxel.mouse_x, pyxel.mouse_y)

        if self._hovered and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.on_click is not None:
                self.on_click()

    def draw(self) -> None:
        """
        カラーボタンを描画する。

        マテリアルの色プレビューとラベルを表示する。
        """
        if not self.visible:
            return

        # 背景（マテリアルの色）を描画
        inner_margin = 2
        pyxel.rect(
            self.x + inner_margin,
            self.y + inner_margin,
            self.width - inner_margin * 2,
            self.height - inner_margin * 2 - 6,  # ラベル分のスペースを確保
            self.display_color,
        )

        # 枠を描画
        if self.selected:
            pyxel.rectb(self.x, self.y, self.width, self.height - 6, COLOR_UI_TEXT)
            pyxel.rectb(
                self.x - 1,
                self.y - 1,
                self.width + 2,
                self.height - 4,
                COLOR_UI_SELECTED,
            )
        elif self._hovered:
            pyxel.rectb(self.x, self.y, self.width, self.height - 6, COLOR_UI_BUTTON)
        else:
            pyxel.rectb(self.x, self.y, self.width, self.height - 6, COLOR_UI_BORDER)

        # ラベルを描画（下部）
        if self.label:
            text_width = len(self.label) * 4
            text_x = self.x + (self.width - text_width) // 2
            text_y = self.y + self.height - 5
            pyxel.text(text_x, text_y, self.label, COLOR_UI_TEXT)
