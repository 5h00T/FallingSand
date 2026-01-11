"""
インゲーム画面のレンダラーモジュール。

ピクセルシミュレーション画面の描画処理を担当する。
"""

from typing import TYPE_CHECKING

import pyxel

from game.colors import (
    COLOR_BACKGROUND,
    COLOR_UI_HELP_TEXT,
    COLOR_UI_TEXT,
)
from game.rendering.base import BaseRenderer

if TYPE_CHECKING:
    from game.states.ingame_state import InGameState


class InGameRenderer(BaseRenderer):
    """
    インゲーム画面のレンダラークラス。

    シミュレーションワールド、UI、カーソルの描画を担当する。
    InGameStateから描画ロジックを分離し、単一責任の原則に従う。

    Attributes:
        state (InGameState): 描画対象のインゲーム状態
    """

    state: "InGameState"  # 型を明示的に再宣言

    def __init__(self, state: "InGameState") -> None:
        """
        インゲームレンダラーを初期化する。

        Parameters:
            state (InGameState): 描画対象のインゲーム状態
        """
        super().__init__(state)

    def draw(self) -> None:
        """
        インゲーム画面を描画する。

        背景、シミュレーションフレーム、ワールド、UI、カーソルを
        順番に描画する。
        """
        pyxel.cls(COLOR_BACKGROUND)

        # シミュレーションウィンドウの枠を描画
        self._draw_simulation_frame()

        # ワールドを描画（オフセット付き）
        self._draw_world()

        # UIを描画
        self._draw_ui()

        # マテリアル選択UIを描画
        self.state.material_selector.draw()

        # カーソルを描画
        self._draw_cursor()

    def _draw_simulation_frame(self) -> None:
        """
        シミュレーションウィンドウの枠を描画する。

        シミュレーション領域を囲む境界線を描画する。
        """
        frame_x = self.state.sim_offset_x - self.state.BORDER_WIDTH
        frame_y = self.state.sim_offset_y - self.state.BORDER_WIDTH
        frame_width = self.state.SIM_WIDTH + self.state.BORDER_WIDTH * 2
        frame_height = self.state.SIM_HEIGHT + self.state.BORDER_WIDTH * 2
        pyxel.rectb(frame_x, frame_y, frame_width, frame_height, COLOR_UI_TEXT)

    def _draw_world(self) -> None:
        """
        ワールドのピクセルを描画する。

        シミュレーションからレンダリングデータを取得し、
        各ピクセルをオフセットを加味して描画する。
        """
        render_data = self.state.world.get_render_data()
        for x, y, color in render_data:
            pyxel.pset(x + self.state.sim_offset_x, y + self.state.sim_offset_y, color)

    def _draw_ui(self) -> None:
        """
        UIを描画する。

        ポーズ表示、ステータス情報、操作ヘルプを描画する。
        """
        # ポーズ表示（シミュレーションウィンドウの中央）
        if self.state.paused:
            self._draw_pause_overlay()

        # ステータス表示（画面上部）
        self._draw_status()

        # 操作ヘルプ（画面下部）
        self._draw_help()

    def _draw_pause_overlay(self) -> None:
        """ポーズオーバーレイを描画する。"""
        pause_text = "PAUSED"
        text_width = len(pause_text) * 4
        pause_x = self.state.sim_offset_x + (self.state.SIM_WIDTH - text_width) // 2
        pause_y = self.state.sim_offset_y + self.state.SIM_HEIGHT // 2
        pyxel.text(pause_x, pause_y, pause_text, COLOR_UI_TEXT)

    def _draw_status(self) -> None:
        """ステータス情報を描画する。"""
        # ブラシサイズ
        pyxel.text(2, 2, f"BRUSH:{self.state.brush_size}", COLOR_UI_TEXT)

        # 選択中マテリアル名
        if self.state.current_material is not None:
            material_text = f"MAT:{self.state.current_material.name}"
            pyxel.text(50, 2, material_text, self.state.current_material.color)

    def _draw_help(self) -> None:
        """操作ヘルプを描画する。"""
        help_y = self.state.game.height - 8
        pyxel.text(2, help_y, "ESC:MENU C:CLEAR SPACE:PAUSE", COLOR_UI_HELP_TEXT)

    def _draw_cursor(self) -> None:
        """
        カーソルを描画する。

        シミュレーションウィンドウ内にマウスがある場合のみ、
        ブラシサイズに応じた円形カーソルを描画する。
        """
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        half_size = self.state.brush_size // 2

        # シミュレーションウィンドウ内にカーソルがある場合のみ描画
        sim_x = mx - self.state.sim_offset_x
        sim_y = my - self.state.sim_offset_y
        if 0 <= sim_x < self.state.SIM_WIDTH and 0 <= sim_y < self.state.SIM_HEIGHT:
            # カーソルの輪郭を描画
            cursor_color = 7
            if self.state.current_material is not None:
                cursor_color = self.state.current_material.color
            pyxel.circb(mx, my, half_size, cursor_color)
