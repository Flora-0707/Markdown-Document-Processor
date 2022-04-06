from __future__ import annotations
from cgitb import text

import click
import re
from typing import *


class MdParseException(Exception):
    pass

class MarkdownDocument:
    components: List[MdBaseComponent]

    def __init__(self) -> None:
        self.components = []

    def __str__(self) -> str:
        return "\n\n".join(map(str, self.components))

    @classmethod
    def parse(cls, input: str) -> MarkdownDocument:
        doc = MarkdownDocument()
        lines = input.split("\n")
        i = 0
        while i < len(lines):
            if lines[i].lstrip() == "":
                i += 1
                continue
            if lines[i][0] == "#":
                try:
                    doc.components.append(MdHeading.parse(lines[i]))
                except MdParseException:
                    pass
                else:
                    i += 1
                    continue
            j = i
            while j < len(lines) and MdUnorderedList.RE_FORMAT.match(lines[j]):
                j += 1
            if j > i:
                doc.components.append(MdUnorderedList.parse("\n".join(line.strip() for line in lines[i:j])))
                i = j
                continue
            while j < len(lines) and lines[j].lstrip() != "":
                j += 1
            doc.components.append(MdParagraph.parse("\n".join(lines[i:j])))
            i = j
        return doc


class MdBaseComponent:
    def __str__(self) -> str:
        raise NotImplementedError()


class MdHeading(MdBaseComponent):
    def __init__(self, text: str, level: int) -> None:
        super().__init__()
        self.text = text
        self.level = level

    def __str__(self) -> str:
        return "#" * self.level + " " + self.text

    @classmethod
    def parse(cls, input: str) -> MdHeading:
        h, text = input.split(" ", 1)
        for c in h:
            if c != "#":
                raise MdParseException()
        return MdHeading(text=text, level=len(h))


class MdParagraph(MdBaseComponent):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text

    def __str__(self) -> str:
        return self.text

    @classmethod
    def parse(cls, input: str) -> MdParagraph:
        lines = input.split("\n")
        paragraph = ""
        for x in lines:
            if len(x) > 2 and x[-2:] == "  ":
                paragraph += x.strip() + "\n"
            else:
                paragraph += x.strip() + " "
        paragraph = " ".join([y for y in paragraph.split(" ") if y != ""])
        return MdParagraph(paragraph)


class MdUnorderedList(MdBaseComponent):
    RE_FORMAT = re.compile(r"^ *[-*+] .*$")

    def __init__(self, ls: List[str]) -> None:
        super().__init__()
        self.ls = ls

    def __str__(self) -> str:
        return "\n".join(self.ls)

    @classmethod
    def parse(cls, input: str) -> MdUnorderedList:
        lines = input.split("\n")
        ls = []
        for line in lines:
            l = line.strip()
            ul, text = l.split(" ", 1)
            ls.append(ul + " " + text)
        return MdUnorderedList(ls)


@click.command()
@click.argument("filename")
def convert(filename):
    with open(filename) as f:
        lines = f.read()
    print(MarkdownDocument.parse(lines))


if __name__ == "__main__":
    convert()