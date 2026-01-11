"""
UI要素の基底クラスモジュール。

全てのUI要素が実装する抽象インターフェースを定義する。
"""

from abc import ABC, abstractmethod


class UIElement(ABC):
    """
    UI要素の抽象基底クラス。

    全てのUI要素（ボタン、パネル等）はこのインターフェースを実装する。
    Compositeパターンのコンポーネントとして機能する。

    Attributes:
        x (int): X座標
        y (int): Y座標
        width (int): 幅
        height (int): 高さ
        visible (bool): 表示状態
        enabled (bool): 有効状態
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        """
        UI要素を初期化する。

        Parameters:
            x (int): X座標
            y (int): Y座標
            width (int): 幅
            height (int): 高さ
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.enabled = True

    def contains_point(self, px: int, py: int) -> bool:
        """
        指定した点がこのUI要素の範囲内にあるかチェックする。

        Parameters:
            px (int): チェックするX座標
            py (int): チェックするY座標

        Returns:
            bool: 範囲内にある場合True
        """
        return (
            self.x <= px < self.x + self.width and self.y <= py < self.y + self.height
        )

    @abstractmethod
    def update(self) -> None:
        """
        UI要素を更新する。

        入力処理や状態更新を行う。
        """
        pass

    @abstractmethod
    def draw(self) -> None:
        """
        UI要素を描画する。
        """
        pass
