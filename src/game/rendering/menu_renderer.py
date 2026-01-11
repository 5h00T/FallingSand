"""
メニュー画面のレンダラーモジュール。

メニュー画面の描画処理を担当する。
"""

from typing import TYPE_CHECKING

import pyxel

from game.colors import (
    COLOR_BACKGROUND,
    COLOR_UI_HELP_TEXT,
    COLOR_UI_SELECTED,
    COLOR_UI_TEXT,
)
from game.rendering.base import BaseRenderer

if TYPE_CHECKING:
    from game.states.menu_state import MenuState


class MenuRenderer(BaseRenderer):
    """
    メニュー画面のレンダラークラス。

    タイトル、メニュー項目、操作説明の描画を担当する。
    MenuStateから描画ロジックを分離し、単一責任の原則に従う。

    Attributes:
        state (MenuState): 描画対象のメニュー状態
    """

    state: "MenuState"  # 型を明示的に再宣言

    def __init__(self, state: "MenuState") -> None:
        """
        メニューレンダラーを初期化する。

        Parameters:
            state (MenuState): 描画対象のメニュー状態
        """
        super().__init__(state)

    def draw(self) -> None:
        """
        メニュー画面を描画する。

        背景をクリアし、タイトル、メニュー項目、操作説明を
        順番に描画する。
        """
        pyxel.cls(COLOR_BACKGROUND)

        self._draw_title()
        self._draw_menu_items()
        self._draw_help()

    def _draw_title(self) -> None:
        """タイトルを描画する。"""
        title = "PIXEL SIMULATION"
        title_x = (self.state.game.width - len(title) * 4) // 2
        pyxel.text(title_x, 30, title, COLOR_UI_TEXT)

    def _draw_menu_items(self) -> None:
        """
        メニュー項目を描画する。

        選択中の項目はハイライト表示し、
        プレフィックスとして「>」を表示する。
        """
        menu_start_y = 60

        for i, item in enumerate(self.state.menu_items):
            is_selected = i == self.state.selected_index
            color = COLOR_UI_SELECTED if is_selected else COLOR_UI_TEXT
            prefix = "> " if is_selected else "  "
            item_text = prefix + item
            item_x = (self.state.game.width - len(item_text) * 4) // 2
            pyxel.text(item_x, menu_start_y + i * 12, item_text, color)

    def _draw_help(self) -> None:
        """操作説明を描画する。"""
        help_text = "UP/DOWN: SELECT  ENTER: OK"
        help_x = (self.state.game.width - len(help_text) * 4) // 2
        pyxel.text(help_x, self.state.game.height - 10, help_text, COLOR_UI_HELP_TEXT)
