from dataclasses import dataclass, field


@dataclass(order=True)
class Page:
    title: list = field(default_factory=list)
    body: list = field(default_factory=list)
    infobox: list = field(default_factory=list)
    categories: list = field(default_factory=list)
    links: list = field(default_factory=list)
    references: list = field(default_factory=list)
    id: int = 0

    def apply(
        self,
        func,
        title=True,
        body=True,
        infobox=True,
        categories=True,
        links=True,
        references=True,
    ):
        if title:
            for i, val in enumerate(self.title):
                self.title[i] = func(val)
        if body:
            for i, val in enumerate(self.body):
                self.body[i] = func(val)
        if infobox:
            for i, val in enumerate(self.infobox):
                self.infobox[i] = func(val)
        if categories:
            for i, val in enumerate(self.categories):
                self.categories[i] = func(val)
        if links:
            for i, val in enumerate(self.links):
                self.links[i] = func(val)
        if references:
            for i, val in enumerate(self.references):
                self.references[i] = func(val)

    def apply_list(
        self,
        func,
        title=True,
        body=True,
        infobox=True,
        categories=True,
        links=True,
        references=True,
    ):
        if title:
            self.title = func(self.title)
        if body:
            self.body = func(self.body)
        if infobox:
            self.infobox = func(self.infobox)
        if categories:
            self.categories = func(self.categories)
        if links:
            self.links = func(self.links)
        if references:
            self.references = func(self.references)
