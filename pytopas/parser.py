"TOPAS parser"

from dataclasses import dataclass
from functools import cache, reduce
from typing import Any, List, Type, Union

import pyparsing as pp

from .base import BaseNode, FallbackNode, FormulaNode, NodeSerialized

RootStatements = Union[FormulaNode, FallbackNode]


@dataclass
class RootNode(BaseNode):
    "Root node of AST"
    type = "topas"
    statements: List[RootStatements]

    @classmethod
    @property
    def root_statement_clses(cls) -> tuple[Type[RootStatements], ...]:
        return (cls.formula_cls, cls.fallback_cls)

    @classmethod
    @cache
    def get_parser(cls, permissive=True):
        root_stmts = [
            x.get_parser(permissive)
            for x in cls.root_statement_clses
            if x != cls.fallback_cls
        ]
        parser = pp.OneOrMore(
            pp.MatchFirst(root_stmts).set_results_name("stmt")
        ).add_parse_action(lambda toks: cls(statements=toks.as_list()))
        return parser

    @classmethod
    def parse(cls, text, permissive=True, parse_all=True):
        "Try to parse text with optional fallback"
        return super().parse(text, permissive, parse_all=parse_all)

    def unparse(self):
        return " ".join(x.unparse() for x in self.statements)

    def serialize(self) -> NodeSerialized:
        return [self.type, *[x.serialize() for x in self.statements]]

    @classmethod
    def unserialize(cls, data: list[Any]):
        assert len(data) >= 1
        assert data[0] == cls.type
        return cls(
            statements=[
                cls.match_unserialize(cls.root_statement_clses, x) for x in data[1:]
            ]
        )


class Parser:
    "TOPAS Parser"

    @staticmethod
    def parse(text: str) -> NodeSerialized:
        "Parse TOPAS source code"

        tree = RootNode.parse(text)
        return tree.serialize()
