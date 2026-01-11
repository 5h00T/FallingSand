"""
レンダラーの基底クラスモジュール。

全てのレンダラーが継承する抽象基底クラスを定義する。
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.states.base_state import BaseState


class BaseRenderer(ABC):
    """
    レンダラーの抽象基底クラス。

    各状態の描画処理をカプセル化する。
    状態（State）と描画（Renderer）を分離し、
    単一責任の原則に従う設計を実現する。

    Attributes:
        state (BaseState): 描画対象の状態インスタンス
    """

    def __init__(self, state: "BaseState") -> None:
        """
        レンダラーを初期化する。

        Parameters:
            state (BaseState): 描画対象の状態インスタンス
        """
        self.state = state

    @abstractmethod
    def draw(self) -> None:
        """
        描画処理を実行する。

        サブクラスで必ず実装する。
        """
        pass
