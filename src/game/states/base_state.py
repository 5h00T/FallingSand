"""
状態の基底クラスモジュール。

全てのゲーム状態が継承する抽象基底クラスを定義する。
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.game import Game


class BaseState(ABC):
    """
    ゲーム状態の抽象基底クラス。

    全てのゲーム状態（メニュー、インゲームなど）はこのクラスを継承する。
    状態パターンを実装し、各状態の振る舞いをカプセル化する。

    Attributes:
        game (Game): 親ゲームインスタンスへの参照
    """

    def __init__(self, game: "Game") -> None:
        """
        状態を初期化する。

        Parameters:
            game (Game): 親ゲームインスタンス
        """
        self.game = game

    def enter(self) -> None:
        """
        状態に入った時に呼ばれる。

        リソースの初期化や状態のセットアップを行う。
        サブクラスでオーバーライド可能。
        """
        pass

    def exit(self) -> None:
        """
        状態を抜ける時に呼ばれる。

        リソースのクリーンアップを行う。
        サブクラスでオーバーライド可能。
        """
        pass

    @abstractmethod
    def update(self) -> None:
        """
        毎フレーム呼ばれる更新処理。

        入力処理やゲームロジックの更新を行う。
        サブクラスで必ず実装する。
        """
        pass

    @abstractmethod
    def draw(self) -> None:
        """
        毎フレーム呼ばれる描画処理。

        画面への描画を行う。
        サブクラスで必ず実装する。
        """
        pass
