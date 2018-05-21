import sys

def lex(line, symbols):
  # \ is the universal escape character (the next char is always interpreted verbatim)
  # recognize strings and braces and symbols (numbers are just symbols)
  DEFAULT = 0
  IDENTIFIER = 1
  STRING = 2
  ESCAPE = 3
  SYMBOL = 4

  token = []
  symbol = [""]
  ret = [DEFAULT]

  def reset_token(c):
    del token[:]
    token.append(c)

  def lex_default(c):
    if c in symbols:
      symbol[0] = c
      return SYMBOL, False
    if c == "\\":
      ret[0] = DEFAULT
      return ESCAPE, False
    if c == '"':
      reset_token(c)
      return STRING, False
    if c.isspace():
      return DEFAULT, False
    reset_token(c)
    return IDENTIFIER, False

  def lex_identifier(c):
    if c in symbols:
      symbol[0] = c
      return SYMBOL, True
    if c == "\\":
      ret[0] = IDENTIFIER
      return ESCAPE, False
    if c.isspace():
      return DEFAULT, True
    token.append(c)
    return IDENTIFIER, False

  def lex_string(c):
    if c == "\\":
      ret[0] = STRING
      token.append("\\")
      return ESCAPE, False
    if c == "\"":
      token.append("\"")
      return DEFAULT, True
    token.append(c)
    return STRING, False

  def lex_escape(c):
    token.append(c)
    return ret[0], False

  def lex_symbol(c):
    pass

  state = DEFAULT
  dfa = {
    DEFAULT: lex_default,
    IDENTIFIER: lex_identifier,
    STRING: lex_string,
    ESCAPE: lex_escape,
    SYMBOL: lex_symbol
  }
  for c in line + "\n":
    state, gottoken = dfa[state](c)
    if gottoken:
      yield "".join(token)
    if state == SYMBOL:
      yield symbol[0]
      state = DEFAULT

def parenthesize(lines):
  variadic = -1
  prefix = "/"
  closing_punctuation = ",;."
  braces = "{}()[]"
  indentation = "    "

  result = []

  bindings = {} # maps identifiers to arities (-1 if variadic)
  scopes = {} # maps indentation levels to operators
  levels = [] # list of indentation levels with keys in scopes
  demands = [] # the number arguments left to satisfy the last operator on the call stack (negative if variadic)
  disabled = [False] # whether or not to process inputs

  def buffer():
    return result[-1]

  def write(s):
    result[-1] += s

  def append(s):
    if buffer().strip() != "":
      result[-1] += " "
    write(s)

  def newline():
    result.append("")

  # create a new demand
  def demand(arity, indent_level):
    demands.append(arity)
    if indent_level in scopes:
      scopes[indent_level] += 1
    else:
      scopes[indent_level] = 1
      levels.append(indent_level)

  # close a demand
  def resolve():
    write(")")
    demands.pop()

    level = levels[-1]
    scopes[level] -= 1
    if scopes[level] == 0:
      del scopes[level]
      levels.pop()

    if len(demands) > 0:
      appease()

  # appease a demand
  def appease():
    if demands[-1] == variadic:
      return

    demands[-1] -= 1
    if demands[-1] == 0:
      resolve()

  def deindent(old, new):
    while len(levels) > 0 and levels[-1] >= new:
      resolve()

  # directives
  def use(filename):
    r, b = parenthesize(open(filename))
    result.extend(r)
    for binding in b:
      bindings[binding] = b[binding]

  def define(name, arity=variadic):
    bindings[name] = int(arity)

  def comment(*args):
    pass

  def disable(*args):
    disabled[0] = True

  def enable(*args):
    disabled[0] = False

  directives = {
    "use": use,
    "def": define,
    "/": comment,
    "off": disable,
    "on": enable
  }

  last_indent = None
  for l in lines:
    # extract indentation level and code
    line = l.rstrip()
    code = line.lstrip()
    indent = len(line) - len(code)

    # if directive, handle it and skip this line
    if code.startswith(prefix):
      tokens = code[len(prefix):].split(" ")
      directive = tokens[0]
      arguments = tokens[1:]
      if not disabled[0] or directive == "on":
        directives[directive](*arguments)
    # if disabled, just write the line verbatim
    elif disabled[0]:
      newline()
      write(line)
    # a normal line of code
    else:
      # close any brackets from indentation changes
      if last_indent is not None and indent < last_indent:
        deindent(last_indent, indent)

      # handle the new line
      newline()
      write(" " * indent)
      for token in lex(code, closing_punctuation): # include braces? harder to force spaces in output that way
        #print(token, bindings)
        #print(result, demands, scopes)
        # normal binding
        if token in bindings:
          append("(" + token)
          demand(bindings[token], indent)
        # forced variadic binding
        elif token[-1] == ":" and token[:-1] in bindings:
          append("(" + token[:-1])
          demand(variadic, indent)
        # close a binding
        elif token in closing_punctuation:
          resolve()
        # normal token
        else:
          append(token)
          appease()

    # save for next line
    last_indent = indent
  deindent(indent, 0)

  return result, bindings

source = sys.argv[1]
result, bindings = parenthesize(open(source))
print("\n".join(result))
