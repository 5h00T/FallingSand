"""
マテリアルシステムモジュール。

ピクセルシミュレーションで使用される各種マテリアルを定義する。
Strategyパターンを使用して各マテリアルの振る舞いをカプセル化する。
"""

import random
from abc import ABC, abstractmethod
from enum import IntEnum
from typing import TYPE_CHECKING


class MaterialType(IntEnum):
    """
    マテリアルの種類を表す列挙型。

    IntEnumを継承しているため、int型との互換性を保ちつつ、
    型安全性を向上させる。
    """

    EMPTY = 0
    WALL = 1
    SAND = 2
    WATER = 3
    OIL = 4
    FIRE = 5


if TYPE_CHECKING:
    from game.simulation.world import World


class Material(ABC):
    """
    マテリアルの抽象基底クラス。

    各マテリアルはこのインターフェースを実装し、
    独自の物理挙動と描画色を定義する。
    """

    @property
    @abstractmethod
    def id(self) -> "MaterialType":
        """
        マテリアルの一意識別子を取得する。

        Returns:
            MaterialType: マテリアルID
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        マテリアルの表示名を取得する。

        Returns:
            str: マテリアル名
        """
        pass

    @property
    @abstractmethod
    def color(self) -> int:
        """
        マテリアルのPyxelカラーを取得する。

        Returns:
            int: Pyxelカラーインデックス (0-15)
        """
        pass

    @property
    def density(self) -> int:
        """
        マテリアルの密度を取得する。

        密度が高いほど下に沈む。
        デフォルトは100。

        Returns:
            int: 密度値
        """
        return 100

    @abstractmethod
    def update(self, x: int, y: int, world: "World") -> None:
        """
        マテリアルの物理挙動を更新する。

        Parameters:
            x (int): 現在のX座標
            y (int): 現在のY座標
            world (World): ワールドインスタンス
        """
        pass


class EmptyMaterial(Material):
    """
    空のマテリアル。

    何も存在しない空間を表す。物理挙動は持たない。
    """

    @property
    def id(self) -> MaterialType:
        """マテリアルIDを返す。"""
        return MaterialType.EMPTY

    @property
    def name(self) -> str:
        """マテリアル名を返す。"""
        return "Empty"

    @property
    def color(self) -> int:
        """描画色を返す。"""
        return 0

    @property
    def density(self) -> int:
        """密度を返す。空気は最も軽い。"""
        return 0

    def update(self, x: int, y: int, world: "World") -> None:
        """空のマテリアルは更新しない。"""
        pass


class WallMaterial(Material):
    """
    壁マテリアル。

    固定された障害物を表す。動かない。
    """

    @property
    def id(self) -> MaterialType:
        """マテリアルIDを返す。"""
        return MaterialType.WALL

    @property
    def name(self) -> str:
        """マテリアル名を返す。"""
        return "Wall"

    @property
    def color(self) -> int:
        """描画色を返す（灰色）。"""
        return 5

    @property
    def density(self) -> int:
        """密度を返す。壁は非常に重い（動かない）。"""
        return 1000

    def update(self, x: int, y: int, world: "World") -> None:
        """壁は動かないため更新しない。"""
        pass


class SandMaterial(Material):
    """
    砂マテリアル。

    重力に従って落下し、斜め下にも移動可能な粒子。
    """

    @property
    def id(self) -> MaterialType:
        """マテリアルIDを返す。"""
        return MaterialType.SAND

    @property
    def name(self) -> str:
        """マテリアル名を返す。"""
        return "Sand"

    @property
    def color(self) -> int:
        """描画色を返す（黄色/オレンジ）。"""
        return 9

    @property
    def density(self) -> int:
        """密度を返す。砂は水より重い。"""
        return 150

    def update(self, x: int, y: int, world: "World") -> None:
        """
        砂の物理挙動を更新する。

        砂は下に落下し、下が塞がっている場合は斜め下に移動する。
        水より重いため、水の中を沈む。

        Parameters:
            x (int): 現在のX座標
            y (int): 現在のY座標
            world (World): ワールドインスタンス
        """
        # 真下をチェック
        below = world.get_material_at(x, y + 1)

        if below is not None:
            # 真下に落下可能（空または水より軽いマテリアル）
            if below.density < self.density:
                world.swap_pixels(x, y, x, y + 1)
                return

        # 斜め下をチェック
        left_material = world.get_material_at(x - 1, y + 1)
        right_material = world.get_material_at(x + 1, y + 1)

        left_passable = (
            left_material is not None and left_material.density < self.density
        )
        right_passable = (
            right_material is not None and right_material.density < self.density
        )

        if left_passable and right_passable:
            # 両方空いている場合はランダムに選択
            if random.randint(0, 1) == 0:
                world.swap_pixels(x, y, x - 1, y + 1)
            else:
                world.swap_pixels(x, y, x + 1, y + 1)
        elif left_passable:
            world.swap_pixels(x, y, x - 1, y + 1)
        elif right_passable:
            world.swap_pixels(x, y, x + 1, y + 1)


class WaterMaterial(Material):
    """
    水マテリアル。

    重力に従って落下し、横方向にも流れる液体。
    修正: 上に水がある場合は横移動を制限し、千切れ（隙間）を防ぐ。
    """

    @property
    def id(self) -> MaterialType:
        return MaterialType.WATER

    @property
    def name(self) -> str:
        return "Water"

    @property
    def color(self) -> int:
        return 12

    @property
    def density(self) -> int:
        return 100

    def update(self, x: int, y: int, world: "World") -> None:
        """
        水の物理挙動を更新する。
        """
        # 1. 真下への落下（最優先）
        below = world.get_material_at(x, y + 1)
        if below is not None and below.density < self.density:
            world.swap_pixels(x, y, x, y + 1)
            return

        # 2. 斜め下への拡散（優先度高）
        left_below = world.get_material_at(x - 1, y + 1)
        right_below = world.get_material_at(x + 1, y + 1)

        left_below_passable = (
            left_below is not None and left_below.density < self.density
        )
        right_below_passable = (
            right_below is not None and right_below.density < self.density
        )

        if left_below_passable and right_below_passable:
            if random.randint(0, 1) == 0:
                world.swap_pixels(x, y, x - 1, y + 1)
            else:
                world.swap_pixels(x, y, x + 1, y + 1)
            return
        elif left_below_passable:
            world.swap_pixels(x, y, x - 1, y + 1)
            return
        elif right_below_passable:
            world.swap_pixels(x, y, x + 1, y + 1)
            return

        # 3. 横方向への流動
        # 【修正ポイント】
        # 自分の真上に「水（自分と同じID）」がある場合、横移動を行わない。
        # これにより、下の水が横に滑って上の水が取り残される（隙間ができる）のを防ぐ。
        above = world.get_material_at(x, y - 1)
        if above is not None and above.id == self.id:
            return

        left = world.get_material_at(x - 1, y)
        right = world.get_material_at(x + 1, y)

        left_passable = left is not None and left.density < self.density
        right_passable = right is not None and right.density < self.density

        if left_passable and right_passable:
            if random.randint(0, 1) == 0:
                world.swap_pixels(x, y, x - 1, y)
            else:
                world.swap_pixels(x, y, x + 1, y)
        elif left_passable:
            world.swap_pixels(x, y, x - 1, y)
        elif right_passable:
            world.swap_pixels(x, y, x + 1, y)


class OilMaterial(Material):
    """
    油マテリアル。

    水より軽い液体で、水の上に浮く。
    火で燃える可燃性を持つ。
    """

    @property
    def id(self) -> MaterialType:
        """マテリアルIDを返す。"""
        return MaterialType.OIL

    @property
    def name(self) -> str:
        """マテリアル名を返す。"""
        return "Oil"

    @property
    def color(self) -> int:
        """描画色を返す（茶色）。"""
        return 10

    @property
    def density(self) -> int:
        """密度を返す。油は水より軽い。"""
        return 50

    @property
    def flammable(self) -> bool:
        """可燃性を返す。油は燃える。"""
        return True

    def update(self, x: int, y: int, world: "World") -> None:
        """
        油の物理挙動を更新する。

        水と同様に流れるが、水より軽いので水の上に浮く。

        Parameters:
            x (int): 現在のX座標
            y (int): 現在のY座標
            world (World): ワールドインスタンス
        """
        # 1. 真下への落下（最優先）
        below = world.get_material_at(x, y + 1)
        if below is not None and below.density < self.density:
            world.swap_pixels(x, y, x, y + 1)
            return

        # 2. 斜め下への拡散（優先度高）
        left_below = world.get_material_at(x - 1, y + 1)
        right_below = world.get_material_at(x + 1, y + 1)

        left_below_passable = (
            left_below is not None and left_below.density < self.density
        )
        right_below_passable = (
            right_below is not None and right_below.density < self.density
        )

        if left_below_passable and right_below_passable:
            if random.randint(0, 1) == 0:
                world.swap_pixels(x, y, x - 1, y + 1)
            else:
                world.swap_pixels(x, y, x + 1, y + 1)
            return
        elif left_below_passable:
            world.swap_pixels(x, y, x - 1, y + 1)
            return
        elif right_below_passable:
            world.swap_pixels(x, y, x + 1, y + 1)
            return

        # 3. 横方向への流動
        above = world.get_material_at(x, y - 1)
        if above is not None and above.id == self.id:
            return

        left = world.get_material_at(x - 1, y)
        right = world.get_material_at(x + 1, y)

        left_passable = left is not None and left.density < self.density
        right_passable = right is not None and right.density < self.density

        if left_passable and right_passable:
            if random.randint(0, 1) == 0:
                world.swap_pixels(x, y, x - 1, y)
            else:
                world.swap_pixels(x, y, x + 1, y)
        elif left_passable:
            world.swap_pixels(x, y, x - 1, y)
        elif right_passable:
            world.swap_pixels(x, y, x + 1, y)


class FireMaterial(Material):
    """
    火マテリアル。

    上に上昇し、一定時間で消える。
    周囲の可燃物に延焼する。
    """

    # 火の寿命を管理する辞書（座標をキーに）
    _lifetimes: dict[tuple[int, int], int] = {}

    @property
    def id(self) -> MaterialType:
        """マテリアルIDを返す。"""
        return MaterialType.FIRE

    @property
    def name(self) -> str:
        """マテリアル名を返す。"""
        return "Fire"

    @property
    def color(self) -> int:
        """描画色を返す（オレンジ）。"""
        return 14

    @property
    def density(self) -> int:
        """密度を返す。火は上昇するため負の値。"""
        return -10

    def update(self, x: int, y: int, world: "World") -> None:
        """
        火の物理挙動を更新する。

        火は上に上昇し、一定時間で消える。
        周囲の可燃物（油）に延焼する。

        Parameters:
            x (int): 現在のX座標
            y (int): 現在のY座標
            world (World): ワールドインスタンス
        """
        # 寿命を初期化または取得
        key = (x, y)
        if key not in FireMaterial._lifetimes:
            FireMaterial._lifetimes[key] = random.randint(15, 30)

        # 寿命を減らす
        FireMaterial._lifetimes[key] -= 1

        # 寿命が尽きたら消える
        if FireMaterial._lifetimes[key] <= 0:
            del FireMaterial._lifetimes[key]
            world.try_set(x, y, MaterialType.EMPTY)
            return

        # 周囲の可燃物に延焼
        self._spread_fire(x, y, world)

        # 上昇挙動
        above = world.get_material_at(x, y - 1)
        if above is not None and above.density > self.density:
            # 上と入れ替え可能なら上昇
            if above.id == MaterialType.EMPTY:
                if world.swap_pixels(x, y, x, y - 1):
                    # 寿命データを移動
                    self._move_lifetime(x, y, x, y - 1)
                return

        # 斜め上にも移動を試みる
        left_above = world.get_material_at(x - 1, y - 1)
        right_above = world.get_material_at(x + 1, y - 1)

        left_passable = left_above is not None and left_above.id == MaterialType.EMPTY
        right_passable = (
            right_above is not None and right_above.id == MaterialType.EMPTY
        )

        if left_passable and right_passable:
            if random.randint(0, 1) == 0:
                if world.swap_pixels(x, y, x - 1, y - 1):
                    self._move_lifetime(x, y, x - 1, y - 1)
            else:
                if world.swap_pixels(x, y, x + 1, y - 1):
                    self._move_lifetime(x, y, x + 1, y - 1)
        elif left_passable:
            if world.swap_pixels(x, y, x - 1, y - 1):
                self._move_lifetime(x, y, x - 1, y - 1)
        elif right_passable:
            if world.swap_pixels(x, y, x + 1, y - 1):
                self._move_lifetime(x, y, x + 1, y - 1)

    def _spread_fire(self, x: int, y: int, world: "World") -> None:
        """
        周囲の可燃物に延焼する。

        Parameters:
            x (int): 現在のX座標
            y (int): 現在のY座標
            world (World): ワールドインスタンス
        """
        # 8方向をチェック
        directions = [
            (-1, -1),
            (0, -1),
            (1, -1),
            (-1, 0),
            (1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
        ]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            neighbor = world.get_material_at(nx, ny)

            if neighbor is not None:
                # 可燃物（油）をチェック
                if hasattr(neighbor, "flammable") and neighbor.flammable:
                    # 確率で延焼（30%）
                    if random.random() < 0.3:
                        world.try_set(nx, ny, MaterialType.FIRE)

    def _move_lifetime(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """
        寿命データを移動先に移す。

        Parameters:
            x1 (int): 移動元のX座標
            y1 (int): 移動元のY座標
            x2 (int): 移動先のX座標
            y2 (int): 移動先のY座標
        """
        old_key = (x1, y1)
        new_key = (x2, y2)
        if old_key in FireMaterial._lifetimes:
            FireMaterial._lifetimes[new_key] = FireMaterial._lifetimes.pop(old_key)


class MaterialRegistry:
    """
    マテリアルレジストリ。

    全マテリアルを管理し、IDからマテリアルインスタンスを取得する。
    シングルトンパターンで実装。
    """

    _instance: "MaterialRegistry | None" = None
    _materials: dict[int, Material]

    def __new__(cls) -> "MaterialRegistry":
        """
        シングルトンインスタンスを返す。

        Returns:
            MaterialRegistry: レジストリのシングルトンインスタンス
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._materials = {}
            cls._instance._initialize_materials()
        return cls._instance

    def _initialize_materials(self) -> None:
        """デフォルトのマテリアルを登録する。"""
        self.register(EmptyMaterial())
        self.register(WallMaterial())
        self.register(SandMaterial())
        self.register(WaterMaterial())
        self.register(OilMaterial())
        self.register(FireMaterial())

    def register(self, material: Material) -> None:
        """
        マテリアルを登録する。

        Parameters:
            material (Material): 登録するマテリアル
        """
        self._materials[material.id] = material

    def get(self, material_id: int) -> Material | None:
        """
        IDからマテリアルを取得する。

        Parameters:
            material_id (int): マテリアルID

        Returns:
            Material | None: マテリアルインスタンス、存在しない場合はNone
        """
        return self._materials.get(material_id)

    def get_all(self) -> list[Material]:
        """
        全マテリアルのリストを取得する。

        Returns:
            list[Material]: 登録されている全マテリアル
        """
        return list(self._materials.values())

    def get_placeable(self) -> list[Material]:
        """
        配置可能なマテリアルのリストを取得する。

        空（Empty）以外のマテリアルを返す。

        Returns:
            list[Material]: 配置可能なマテリアルのリスト
        """
        return [m for m in self._materials.values() if m.id != 0]


# 便利な定数（後方互換性のため）
EMPTY = MaterialType.EMPTY
WALL = MaterialType.WALL
SAND = MaterialType.SAND
WATER = MaterialType.WATER
OIL = MaterialType.OIL
FIRE = MaterialType.FIRE
