# A parser.


class Tokens(object):

    def __init__(self, tokens):
        self._tokens = tokens
        self._pos = 0
        self._stack = []

    def get(self):
        self._pos += 1

        return self._tokens[self._pos - 1]

    def peek(self):
        return self._tokens[self._pos]

    def save(self):
        self._stack.append(self._pos)

    def restore(self):
        self._pos = self._stack.pop()

    def drop(self):
        self._stack.pop()

    def __repr__(self):
        return str(self._tokens[self._pos:self._pos + 2])


def match_item(item, tokens):
    if isinstance(item, str):
        tokens.save()
        mo = tokens.get()

        if item != mo.kind:
            tokens.restore()

            return None
    else:
        mo = item.match(tokens)

        if mo is None:
            return None

    return mo


class Sequence(object):
    """Matches a sequence of patterns.

    """
    
    def __init__(self, *members):
        self._members = members

    def match(self, tokens):
        matched = []

        for member in self._members:
            mo = match_item(member, tokens)

            if mo is None:
                return None

            if isinstance(member, Inline):
                matched.extend(mo)
            else:
                matched.append(mo)

        return matched


class Choice(object):
    """Matches any of given patterns.

    """    

    def __init__(self, *members):
        self._members = members

    def match(self, tokens):
        for member in self._members:
            tokens.save()
            mo = match_item(member, tokens)

            if mo:
                tokens.drop()

                return mo

            tokens.restore()

        return None


class ChoicePeek(object):
    """Matches any of given patterns.

    """

    def __init__(self, *members):
        self._members = members
        self._members_map = {}

        for member in members:
            self._members_map[member._members[0]] = member

    def match(self, tokens):
        try:
            return match_item(self._members_map[tokens.peek().kind], tokens)
        except KeyError:
            return None


class OneOrMore(object):
    """Matches a pattern one or more times.

    """

    def __init__(self, element, end=None):
        self._element = element
        self._end = end

    def match(self, tokens):
        matched = []

        while True:
            if self._end is not None:
                mo = match_item(self._end, tokens)

                if mo:
                    break

            mo = match_item(self._element, tokens)

            if mo is None:
                break

            matched.append(mo)

        if len(matched) > 0:
            return matched
        else:
            return None


class ZeroOrMore(object):
    """Matches a pattern zero or more times.

    """

    def __init__(self, element, end=None):
        self._element = element
        self._end = end

    def match(self, tokens):
        matched = []

        while True:
            if self._end is not None:
                mo = match_item(self._end, tokens)

                if mo is None:
                    break

            mo = match_item(self._element, tokens)

            if mo is None:
                break

            matched.append(mo)

        return matched


class Any(object):
    """Matches any token.

    """
    
    def __init__(self):
        pass

    def match(self, tokens):
        return tokens.get()


class Inline(object):

    def __init__(self, element):
        self._element = element

    def match(self, tokens):
        return self._element.match(tokens)


class DelimitedList(object):
    """Matches a delimented list of given pattern.

    """
    
    def __init__(self, element, delim=','):
        self._element = element
        self._delim = delim

    def match(self, tokens):
        matched = []

        while True:
            mo = match_item(self._element, tokens)

            if mo is None:
                return None

            matched.append(mo)

            mo = match_item(self._delim, tokens)

            if mo is None:
                return matched


class Grammar(object):
    """Creates a tree of given tokens.

    """
    
    def __init__(self, grammar):
        self._root = grammar

    def parse(self, tokens):
        tokens = Tokens(tokens)
        parsed = self._root.match(tokens)

        if tokens.get().kind == '__EOF__':
            return parsed
        else:
            raise Exception()
