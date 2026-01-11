"""
インゲーム画面の状態モジュール。

実際のピクセルシミュレーションを管理する。
状態ロジックと描画ロジックを分離し、描画はInGameRendererに委譲する。
"""

from typing import TYPE_CHECKING

import pyxel

from game.rendering.ingame_renderer import InGameRenderer
from game.simulation.material import EMPTY, SAND, Material, MaterialType
from game.simulation.world import World
from game.states.base_state import BaseState
from game.ui.material_selector import MaterialSelector

if TYPE_CHECKING:
    from game.game import Game


class InGameState(BaseState):
    """
    インゲーム画面の状態クラス。

    ピクセルシミュレーションの実行と操作を管理する。

    Attributes:
        world (World): ピクセルワールドのインスタンス
        paused (bool): ポーズ状態
        brush_size (int): ブラシサイズ
        sim_width (int): シミュレーションの幅
        sim_height (int): シミュレーションの高さ
        sim_offset_x (int): シミュレーションウィンドウのX座標オフセット
        sim_offset_y (int): シミュレーションウィンドウのY座標オフセット
        current_material (Material | None): 現在選択中のマテリアル
        material_selector (MaterialSelector): マテリアル選択UI
    """

    # シミュレーションサイズの定数
    SIM_WIDTH = 140
    SIM_HEIGHT = 100
    # 枠の太さ
    BORDER_WIDTH = 1
    # シミュレーションウィンドウのオフセット（上寄せ）
    SIM_OFFSET_Y = 10
    # UI領域の高さ
    UI_HEIGHT = 35

    def __init__(self, game: "Game") -> None:
        """
        インゲーム状態を初期化する。

        Parameters:
            game (Game): 親ゲームインスタンス
        """
        super().__init__(game)
        # シミュレーションウィンドウの中央揃え（X座標）
        self.sim_offset_x: int = (game.width - self.SIM_WIDTH) // 2
        self.sim_offset_y: int = self.SIM_OFFSET_Y
        self.world: World = World(self.SIM_WIDTH, self.SIM_HEIGHT)
        self.paused: bool = False
        self.brush_size: int = 3
        self.current_material: Material | None = None

        # マテリアル選択UIを作成
        ui_y = self.sim_offset_y + self.SIM_HEIGHT + 15
        self.material_selector: MaterialSelector = MaterialSelector(
            x=0,
            y=ui_y,
            screen_width=game.width,
            on_material_selected=self._on_material_selected,
        )

        # レンダラーを作成（描画処理を委譲）
        self._renderer = InGameRenderer(self)

    def _on_material_selected(self, material: Material) -> None:
        """
        マテリアル選択時のコールバック。

        Parameters:
            material (Material): 選択されたマテリアル
        """
        self.current_material = material

    def enter(self) -> None:
        """インゲーム状態に入った時の処理。"""
        self.world.clear()
        self.paused = False
        # デフォルトで砂を選択
        self.material_selector.select_by_id(SAND)

    def update(self) -> None:
        """
        インゲームの更新処理。

        入力処理とシミュレーション更新を行う。
        """
        self._handle_input()

        # UIを更新
        self.material_selector.update()

        # ポーズ中はシミュレーションを停止
        if not self.paused:
            self.world.update()

    def _handle_input(self) -> None:
        """ユーザー入力を処理する。"""
        # ESCキーでメニューに戻る
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.game.change_state("menu")
            return

        # スペースキーでポーズ切り替え
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.paused = not self.paused

        # Cキーでクリア
        if pyxel.btnp(pyxel.KEY_C):
            self.world.clear()

        # ブラシサイズ変更
        if pyxel.btnp(pyxel.KEY_UP):
            self.brush_size = min(self.brush_size + 1, 10)
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.brush_size = max(self.brush_size - 1, 1)

        # マウス座標をシミュレーション座標に変換
        sim_x = pyxel.mouse_x - self.sim_offset_x
        sim_y = pyxel.mouse_y - self.sim_offset_y

        # UI領域ではピクセル配置を行わない
        if self.material_selector.is_point_in_ui(pyxel.mouse_x, pyxel.mouse_y):
            return

        # マウスクリックでピクセルを配置
        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            if self.current_material is not None:
                self._place_pixels(sim_x, sim_y, self.current_material.id)

        # 右クリックでピクセルを削除
        if pyxel.btn(pyxel.MOUSE_BUTTON_RIGHT):
            self._place_pixels(sim_x, sim_y, EMPTY)

    def _place_pixels(
        self, center_x: int, center_y: int, pixel_type: MaterialType
    ) -> None:
        """
        ブラシサイズに応じてピクセルを配置する。

        Parameters:
            center_x (int): 中心X座標
            center_y (int): 中心Y座標
            pixel_type (int): ピクセルの種類
        """
        half_size = self.brush_size // 2
        for dy in range(-half_size, half_size + 1):
            for dx in range(-half_size, half_size + 1):
                # 円形のブラシにする
                if dx * dx + dy * dy <= half_size * half_size + half_size:
                    self.world.set_pixel(center_x + dx, center_y + dy, pixel_type)

    def draw(self) -> None:
        """
        インゲーム画面を描画する。

        描画処理はInGameRendererに委譲する。
        """
        self._renderer.draw()
