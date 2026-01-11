"""
メニュー画面の状態モジュール。

ゲーム開始時に表示されるメニュー画面を管理する。
状態ロジックと描画ロジックを分離し、描画はMenuRendererに委譲する。
"""

from typing import TYPE_CHECKING

import pyxel

from game.rendering.menu_renderer import MenuRenderer
from game.states.base_state import BaseState

if TYPE_CHECKING:
    from game.game import Game


class MenuState(BaseState):
    """
    メニュー画面の状態クラス。

    ゲームのタイトル画面とメニュー選択を管理する。

    Attributes:
        menu_items (List[str]): メニュー項目のリスト
        selected_index (int): 現在選択中のメニュー項目のインデックス
    """

    def __init__(self, game: "Game") -> None:
        """
        メニュー状態を初期化する。

        Parameters:
            game (Game): 親ゲームインスタンス
        """
        super().__init__(game)
        self.menu_items: list[str] = ["START", "QUIT"]
        self.selected_index: int = 0

        # レンダラーを作成（描画処理を委譲）
        self._renderer = MenuRenderer(self)

    def enter(self) -> None:
        """メニュー状態に入った時の処理。"""
        self.selected_index = 0

    def update(self) -> None:
        """
        メニューの更新処理。

        キー入力を処理してメニュー項目の選択と決定を行う。
        """
        # 上下キーでメニュー項目を選択
        if pyxel.btnp(pyxel.KEY_UP):
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)

        # Enter/Spaceキーで決定
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
            self._select_menu_item()

    def _select_menu_item(self) -> None:
        """
        選択中のメニュー項目を実行する。

        選択されたメニュー項目に応じて適切なアクションを実行する。
        """
        selected_item = self.menu_items[self.selected_index]

        if selected_item == "START":
            self.game.change_state("ingame")
        elif selected_item == "QUIT":
            pyxel.quit()

    def draw(self) -> None:
        """
        メニュー画面を描画する。

        描画処理はMenuRendererに委譲する。
        """
        self._renderer.draw()
