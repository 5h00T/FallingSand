"""
メインゲームクラスモジュール。

ゲームの初期化と状態管理を担当する。
"""

import pyxel

from game.colors import apply_custom_palette
from game.states.base_state import BaseState
from game.states.ingame_state import InGameState
from game.states.menu_state import MenuState


class Game:
    """
    メインゲームクラス。

    ゲームの初期化、状態管理、メインループを担当する。
    状態パターンを使用して各画面を管理する。

    Attributes:
        width (int): 画面の幅（ピクセル）
        height (int): 画面の高さ（ピクセル）
        states (Dict[str, BaseState]): 状態名から状態インスタンスへのマッピング
        current_state (Optional[BaseState]): 現在の状態
    """

    def __init__(
        self,
        width: int = 160,
        height: int = 160,
        title: str = "Pixel Simulation",
        fps: int = 60,
    ) -> None:
        """
        ゲームを初期化する。

        Parameters:
            width (int): 画面の幅
            height (int): 画面の高さ
            title (str): ウィンドウタイトル
            fps (int): フレームレート
        """
        self.width = width
        self.height = height

        # 状態の初期化
        self.states: dict[str, BaseState] = {}
        self.current_state: BaseState | None = None

        # Pyxelの初期化
        pyxel.init(width, height, title=title, fps=fps)
        pyxel.mouse(True)  # マウスカーソルを有効化

        # カスタムカラーパレットを適用
        self._init_colors()

        # 状態を登録
        self._register_states()

        # 初期状態をメニューに設定
        self.change_state("menu")

        # ゲームループを開始
        pyxel.run(self.update, self.draw)

    def _register_states(self) -> None:
        """全ての状態を登録する。"""
        self.states["menu"] = MenuState(self)
        self.states["ingame"] = InGameState(self)

    def _init_colors(self) -> None:
        """
        ゲームで使用するカラーパレットを初期化する。

        Pyxelのデフォルトパレット（16色）をゲーム独自の
        カスタムカラーで再定義する。
        """
        apply_custom_palette()

    def change_state(self, state_name: str) -> None:
        """
        現在の状態を変更する。

        Parameters:
            state_name (str): 変更先の状態名

        Raises:
            ValueError: 指定された状態名が存在しない場合
        """
        if state_name not in self.states:
            raise ValueError(f"Unknown state: {state_name}")

        # 現在の状態を終了
        if self.current_state is not None:
            self.current_state.exit()

        # 新しい状態に変更
        self.current_state = self.states[state_name]
        self.current_state.enter()

    def update(self) -> None:
        """
        毎フレーム呼ばれる更新処理。

        現在の状態のupdate()を呼び出す。
        """
        if self.current_state is not None:
            self.current_state.update()

    def draw(self) -> None:
        """
        毎フレーム呼ばれる描画処理。

        現在の状態のdraw()を呼び出す。
        """
        if self.current_state is not None:
            self.current_state.draw()
