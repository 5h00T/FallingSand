"""
ピクセルワールド管理モジュール（cur/nxt 2重バッファ版）。

- cur: 現在の状態（読み取り専用のつもりで扱う）
- nxt: 次の状態（このフレームでの結果を書き込む）
- moved: このフレームで確定したセル（同一フレーム内の二重移動・競合を防ぐ）

このモジュールはpyxelに依存せず、純粋なシミュレーションロジックのみを提供する。
"""

from game.simulation.material import (
    EMPTY,
    SAND,
    Material,
    MaterialRegistry,
    MaterialType,
)


class World:
    """
    ピクセルシミュレーションのワールドクラス（cur/nxt 2重バッファリング）。

    - get_pixel / get_material_at は常に cur を参照する
    - swap_pixels は cur を参照し、nxt に書き込む（movedで競合回避）
    - update() の最後に cur<->nxt を swap して確定
    """

    # 後方互換性のための定数
    EMPTY = EMPTY
    SAND = SAND

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.registry = MaterialRegistry()

        # 2重バッファ
        self._cur: list[list[MaterialType]] = self._create_empty_grid()
        self._nxt: list[list[MaterialType]] = self._create_empty_grid()

        # このフレームで確定済み（nxtに書いた）セル
        self._moved: list[list[bool]] = self._create_flag_grid()

        self._frame_count: int = 0

    # ============
    # グリッド生成
    # ============

    def _create_empty_grid(self) -> list[list[MaterialType]]:
        return [[EMPTY for _ in range(self.width)] for _ in range(self.height)]

    def _create_flag_grid(self) -> list[list[bool]]:
        return [[False for _ in range(self.width)] for _ in range(self.height)]

    def _reset_moved_flags(self) -> None:
        for y in range(self.height):
            row = self._moved[y]
            for x in range(self.width):
                row[x] = False

    # ============
    # 外部互換API
    # ============

    @property
    def pixels(self) -> list[list[MaterialType]]:
        """
        既存互換：現在状態（cur）を返す。

        注意:
            cur/nxt方式では、update中の途中結果は cur に反映されない。
            “現在確定している状態” として参照する用途に限定するのが安全。
        """
        return self._cur

    def clear(self) -> None:
        self._cur = self._create_empty_grid()
        self._nxt = self._create_empty_grid()
        self._moved = self._create_flag_grid()

    def get_pixel(self, x: int, y: int) -> MaterialType | int:
        """curから取得。範囲外は -1。"""
        if self._is_valid_position(x, y):
            return self._cur[y][x]
        return -1

    def get_material_at(self, x: int, y: int) -> Material | None:
        """curから material を取得。範囲外は None。"""
        pixel_id = self.get_pixel(x, y)
        if pixel_id < 0:
            return None
        return self.registry.get(pixel_id)

    def set_pixel(self, x: int, y: int, pixel_type: MaterialType) -> bool:
        """
        指定座標にピクセルを設置する。

        ブラシ等の「外部からの編集」は cur に反映する。
        ※ update() 中に呼ぶなら、基本は swap/try_move/try_set を使うのがおすすめ。
        """
        if self._is_valid_position(x, y):
            self._cur[y][x] = pixel_type
            return True
        return False

    # ============
    # moved / 競合管理
    # ============

    def is_updated(self, x: int, y: int) -> bool:
        """
        互換用：このフレームで確定済み（moved）か。

        moved=True なら、そのセルはこのフレームではもう動かさない/書き換えない。
        """
        if not self._is_valid_position(x, y):
            return True
        return self._moved[y][x]

    def mark_updated(self, x: int, y: int) -> None:
        """互換用：movedを立てる（通常はWorld内部で使う想定）。"""
        if self._is_valid_position(x, y):
            self._moved[y][x] = True

    # ============
    # 2重バッファ更新用API（Materialから呼ばれる）
    # ============

    def swap_pixels(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """
        2つのセルを入れ替える（cur参照 / nxt書き込み）。

        - すでに moved のセルが絡む場合は失敗
        - 成功したら両方 moved にする（同一フレームの二重移動を防止）
        """
        if not (self._is_valid_position(x1, y1) and self._is_valid_position(x2, y2)):
            return False
        if self._moved[y1][x1] or self._moved[y2][x2]:
            return False

        a = self._cur[y1][x1]
        b = self._cur[y2][x2]

        # nxtに確定
        self._nxt[y1][x1] = b
        self._nxt[y2][x2] = a
        self._moved[y1][x1] = True
        self._moved[y2][x2] = True
        return True

    def try_move(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """
        (x1,y1) の粒子を (x2,y2) に移動（cur参照 / nxt書き込み）。
        移動元は EMPTY になる。

        swapではなく move が欲しい反応（生成・消滅）向け。
        """
        if not (self._is_valid_position(x1, y1) and self._is_valid_position(x2, y2)):
            return False
        if self._moved[y1][x1] or self._moved[y2][x2]:
            return False

        a = self._cur[y1][x1]
        self._nxt[y2][x2] = a
        self._nxt[y1][x1] = EMPTY
        self._moved[y1][x1] = True
        self._moved[y2][x2] = True
        return True

    def try_set(self, x: int, y: int, pixel_type: MaterialType) -> bool:
        """
        nxtの指定セルを上書き（cur参照 / nxt書き込み）。

        例：火が煙を生成、蒸発で水→蒸気、など。
        """
        if not self._is_valid_position(x, y):
            return False
        if self._moved[y][x]:
            return False

        self._nxt[y][x] = pixel_type
        self._moved[y][x] = True
        return True

    def update(self) -> None:
        """
        シミュレーションを1ステップ更新する。

        2重バッファ方式で安全に更新を行う:
        1. nxt を cur のコピーで初期化
        2. moved フラグをリセット
        3. 重いマテリアル（砂）を先に処理
        4. 軽いマテリアル（水）を後に処理
        5. cur と nxt をスワップして確定

        Note:
            砂パスでスワップされた水は moved=True となり、
            水パスでは処理されない。これにより砂が水を押しのけて沈む。
        """
        # 1) nxt = cur
        for y in range(self.height):
            self._nxt[y][:] = self._cur[y][:]

        # 2) moved reset
        self._reset_moved_flags()

        # パス1：火を最初に処理（延焼と消滅）
        self._update_pass(target_ids={MaterialType.FIRE})

        # パス2：砂など「重い粒子」を先に処理
        self._update_pass(target_ids={MaterialType.SAND})

        # パス3：水など「流体」を後に処理
        self._update_pass(target_ids={MaterialType.WATER, MaterialType.OIL})

        # 3) swap
        self._cur, self._nxt = self._nxt, self._cur
        self._frame_count += 1

    def _update_pass(self, target_ids: set[MaterialType]) -> None:
        """
        指定されたマテリアルタイプのピクセルを更新する。

        下から上にスキャンして落下を正確に処理する。
        水など横移動するマテリアルのために最下行も処理する。

        Parameters:
            target_ids (set[MaterialType]): 処理対象のマテリアルIDセット
        """
        # 最下行から上にスキャン（height-1 を含めて水の横流れも処理）
        for y in range(self.height - 1, -1, -1):
            x_range = (
                range(self.width)
                if self._frame_count % 2 == 0
                else range(self.width - 1, -1, -1)
            )
            for x in x_range:
                if self._moved[y][x]:
                    continue
                pid = self._cur[y][x]
                if pid in target_ids:
                    mat = self.registry.get(pid)
                    if mat is not None:
                        mat.update(x, y, self)

    # ============
    # 描画用
    # ============

    def get_render_data(self) -> list[tuple[int, int, int]]:
        """
        描画用のピクセルデータを取得する（curから生成）。

        Returns:
            list[tuple[int, int, int]]: (x, y, color)
        """
        render_data: list[tuple[int, int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                pixel_id = self._cur[y][x]
                if pixel_id != EMPTY:
                    material = self.registry.get(pixel_id)
                    if material is not None:
                        render_data.append((x, y, material.color))
        return render_data

    # ============
    # 内部
    # ============

    def _is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height
