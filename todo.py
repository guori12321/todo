#!/usr/bin/env python
# coding=utf8

__version__ = '0.1.1'


from ply import lex
from ply import yacc


class Task(object):
    """
    Task object.
    One task looks like:

      1. (x) Go shopping

    if not done,  leave there blank.

    id          int     task's id
    content     str     task'content
    done        bool    is this task done?
    """
    def __init__(self, id, content, done=False):
        self.id = id
        self.content = content
        self.done = done


class Tag(object):
    """
    Tag object.
    Tags split tasks list like milestones.
    One tag looks like:
      ----- The tasks above is before 12-04-05 ----
    The string 'The....05' is the tag's content, it should be unique.

    name        str     tag's name, should be unique in all tags
    """

    def __init__(self, name):
        self.name = name


class TodoLexer(object):
    """
    Lexer for Todo format string.
    Tokens
      ID        e.g. '1.'
      TAG       e.g. '---- SampleTag ----'
      DONE      e.g. '(x)'
      TASK      e.g. 'This is a task'
    """

    tokens = (
        "ID",
        "TAG",
        "DONE",
        "TASK",
    )

    t_ignore = "\x20\x09"  # ignore spaces and tabs

    def t_ID(self, t):
        r'\d+\.([uU]|[lL]|[uU][lL]|[lL][uU])?'
        t.value = int(t.value[:-1])
        return t

    def t_TAG(self, t):
        r'-+(.*)-+'
        t.value = ''.join(i for i in t.value if i != '-')
        t.value = t.value.strip()
        return t

    def t_DONE(self, t):
        r'(\(x\))'
        return t

    def t_TASK(self, t):
        r'((?!\(x\))).+'
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        raise SyntaxError(
            "Illegal character: '%s' at Line %d" % (t.value[0], t.lineno)
        )

    def __init__(self):
        self.lexer = lex.lex(module=self)

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print tok


class TodoParser(object):
    """
    Parser for Todo format string, works with a todo lexer.

    Parse string to Python list:
      todo_str = "#1 Watch TV! (done)"
      TodoParser().parse(todo_str)
    """

    tokens = TodoLexer.tokens

    def p_error(self, p):
        if p:
            raise SyntaxError(
                "Character '%s' at line %d" % (p.value[0], p.lineno)
            )
        else:
            raise SyntaxError("SyntaxError at EOF")

    def p_start(self, p):
        "start : translation_unit"
        p[0] = self.lst

    def p_translation_unit(self, p):
        """
        translation_unit : translate_single_line
                         | translation_unit translate_single_line
                         |
        """
        pass

    def p_translation_task(self, p):
        """
        translate_single_line : ID DONE TASK
                              | ID TASK
        """
        if len(p) == 4:
            done = True
            content = p[3]
        elif len(p) == 3:
            done = False
            content = p[2]
        task = Task(p[1], content, done)
        self.lst.append(task)

    def p_translation_tag(self, p):
        """
        translate_single_line : TAG
        """
        tag = Tag(p[1])
        self.lst.append(tag)

    def __init__(self):
        self.parser = yacc.yacc(module=self, debug=0, write_tables=0)

    def parse(self, data):
        # reset list
        self.lst = list()
        return self.parser.parse(data)


class TodoGenerator(object):
    """
    Generator from python list to string.
    """

    g_newline = "\n"

    def g_id(self, v):
        return str(v) + "."

    def g_done(self, v):
        if v is True:
            return '(x)'
        else:
            return '   '

    def g_task(self, v):
        return v

    def g_tag(self, v):
        return '---- ' + v + ' ----'

    def gen_tag(self, tag):
        return self.g_tag(tag.name)

    def gen_task(self, task):
        lst = []
        lst.append(self.g_id(task.id))
        lst.append(self.g_done(task.done))
        lst.append(self.g_task(task.content))
        return " ".join(lst)

    def generate(self, lst):
        re = []
        for i in lst:
            if isinstance(i, Tag):
                re.append(self.gen_tag(i))
            elif isinstance(i, Task):
                re.append(self.gen_task(i))
            else:
                raise SyntaxError('Not support type: ' + type(i))
        return self.g_newline.join(re)


lexer = TodoLexer()  # build lexer
parser = TodoParser()  # build parser
generator = TodoGenerator()  # build generator

lst = parser.parse(open("todo.txt").read())

for i in lst:

    if isinstance(i, Task):
        print i.id, i.content, i.done

print generator.generate(lst)
