"""
マテリアル選択UIモジュール。

マテリアルを選択するためのUI コンポーネントを提供する。
"""

from collections.abc import Callable

import pyxel

from game.colors import COLOR_BACKGROUND, COLOR_WALL
from game.simulation.material import Material, MaterialRegistry
from game.ui.base import UIElement
from game.ui.button import ColorButton


class MaterialSelector(UIElement):
    """
    マテリアル選択パネル。

    複数のマテリアルボタンを管理し、選択されたマテリアルを
    コールバックで通知する。Compositeパターンでボタンを管理。

    Attributes:
        buttons (list[ColorButton]): マテリアルボタンのリスト
        selected_material (Material | None): 選択中のマテリアル
        on_material_selected (Callable[[Material], None] | None):
            マテリアル選択時のコールバック
    """

    # ボタンサイズの定数
    BUTTON_WIDTH = 20
    BUTTON_HEIGHT = 22
    BUTTON_SPACING = 4

    def __init__(
        self,
        x: int,
        y: int,
        screen_width: int,
        on_material_selected: Callable[[Material], None] | None = None,
    ) -> None:
        """
        マテリアルセレクターを初期化する。

        Parameters:
            x (int): X座標
            y (int): Y座標
            screen_width (int): 画面幅（中央揃え計算用）
            on_material_selected (Callable[[Material], None] | None):
                マテリアル選択時のコールバック
        """
        self.on_material_selected = on_material_selected
        self.buttons: list[ColorButton] = []
        self.selected_material: Material | None = None
        self._material_map: dict[int, Material] = {}

        # マテリアルレジストリから配置可能なマテリアルを取得
        registry = MaterialRegistry()
        placeable_materials = registry.get_placeable()

        # 幅と高さを計算
        total_width = (
            len(placeable_materials) * self.BUTTON_WIDTH
            + (len(placeable_materials) - 1) * self.BUTTON_SPACING
        )
        height = self.BUTTON_HEIGHT

        # 中央揃えでX座標を調整
        centered_x = (screen_width - total_width) // 2

        super().__init__(centered_x, y, total_width, height)

        # マテリアルごとにボタンを作成
        self._create_material_buttons(placeable_materials)

        # デフォルトで最初のマテリアルを選択
        if placeable_materials:
            self._select_material(placeable_materials[0])

    def _create_material_buttons(self, materials: list[Material]) -> None:
        """
        マテリアルボタンを作成する。

        Parameters:
            materials (list[Material]): マテリアルのリスト
        """
        for i, material in enumerate(materials):
            button_x = self.x + i * (self.BUTTON_WIDTH + self.BUTTON_SPACING)
            button = ColorButton(
                x=button_x,
                y=self.y,
                width=self.BUTTON_WIDTH,
                height=self.BUTTON_HEIGHT,
                display_color=material.color,
                label=material.name[0],  # 頭文字を表示
                on_click=self._create_select_callback(material),
            )
            self.buttons.append(button)
            self._material_map[material.id] = material

    def _create_select_callback(self, material: Material) -> Callable[[], None]:
        """
        マテリアル選択コールバックを作成する。

        クロージャでマテリアルをキャプチャする。

        Parameters:
            material (Material): 選択対象のマテリアル

        Returns:
            Callable[[], None]: コールバック関数
        """

        def callback() -> None:
            self._select_material(material)

        return callback

    def _select_material(self, material: Material) -> None:
        """
        マテリアルを選択する。

        Parameters:
            material (Material): 選択するマテリアル
        """
        self.selected_material = material

        # 全ボタンの選択状態を更新
        materials = list(self._material_map.values())
        for i, btn in enumerate(self.buttons):
            btn.selected = materials[i].id == material.id

        # コールバックを実行
        if self.on_material_selected is not None:
            self.on_material_selected(material)

    def select_by_id(self, material_id: int) -> None:
        """
        IDでマテリアルを選択する。

        Parameters:
            material_id (int): マテリアルID
        """
        material = self._material_map.get(material_id)
        if material is not None:
            self._select_material(material)

    def update(self) -> None:
        """
        マテリアルセレクターを更新する。

        全てのボタンの更新処理を呼び出す。
        """
        if not self.visible or not self.enabled:
            return

        for button in self.buttons:
            button.update()

        # 数字キーでマテリアル選択
        self._handle_keyboard_selection()

    def _handle_keyboard_selection(self) -> None:
        """
        キーボードによるマテリアル選択を処理する。

        1-9キーで対応するマテリアルを選択する。
        """
        key_mapping = [
            pyxel.KEY_1,
            pyxel.KEY_2,
            pyxel.KEY_3,
            pyxel.KEY_4,
            pyxel.KEY_5,
            pyxel.KEY_6,
            pyxel.KEY_7,
            pyxel.KEY_8,
            pyxel.KEY_9,
        ]

        materials = list(self._material_map.values())
        for i, key in enumerate(key_mapping):
            if i < len(materials) and pyxel.btnp(key):
                self._select_material(materials[i])
                break

    def draw(self) -> None:
        """
        マテリアルセレクターを描画する。

        パネル背景と全てのボタンを描画する。
        """
        if not self.visible:
            return

        # 背景パネルを描画
        panel_margin = 3
        pyxel.rect(
            self.x - panel_margin,
            self.y - panel_margin,
            self.width + panel_margin * 2,
            self.height + panel_margin * 2,
            COLOR_BACKGROUND,
        )
        pyxel.rectb(
            self.x - panel_margin,
            self.y - panel_margin,
            self.width + panel_margin * 2,
            self.height + panel_margin * 2,
            COLOR_WALL,
        )

        # 全ボタンを描画
        for button in self.buttons:
            button.draw()

    def is_point_in_ui(self, px: int, py: int) -> bool:
        """
        指定した点がUI範囲内にあるかチェックする。

        Parameters:
            px (int): X座標
            py (int): Y座標

        Returns:
            bool: UI範囲内にある場合True
        """
        panel_margin = 3
        return (
            self.x - panel_margin <= px < self.x + self.width + panel_margin
            and self.y - panel_margin <= py < self.y + self.height + panel_margin
        )
