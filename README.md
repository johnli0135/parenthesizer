# Parenthesizer

A command line utility that uses whitespace and punctuation rules to generate properly parenthesized code of LISP dialects.

Usage: `python parenthesizer.py <input file>`

## Directives

Knowledge of operator arity is given through directives. A directive is any line where the first non-whitespace character is a slash.

`/use f`: process a file `f` and include the results in the current file.

`/def f n`: define an operator `f` to take `n` arguments, or to take a variable number of arguments if `n` is not specified.

`/mask f`: treat `f` as a normal identifier rather than an operator.

`/unmask f`: undo `/mask f`.

`//`: line comment.

`/off`: disable any processing until the next `/on` directive.

`/on`: re-enable processing.

## Simple operators

Since directives tell the parenthesizer the arity of common operators, many parentheses can be omitted.

For example:
```racket
/use racket.txt
define (fact n)
    if = n 0
        1
        * n (fact - n 1)
```
will generate
```racket
(define (fact n)
    (if (= n 0)
        1
        (* n (fact (- n 1)))))
```

## Punctuation

A comma, semicolon, or period can serve as a closing parenthesis for an operator that takes a variable number of arguments:

```racket
/use racket.txt
define (f x y) 
    display x;
    display y;
    + x y.
```

A colon at the end of an operator name forces the operator to take a variable number of arguments:

```
+: 1 2 3.
```

## Whitespace

Going from higher to lower indentation closes any blocks in between.

End-of-file is treated as a blank line of lowest possible indentation level.

Indentations are preserved after addition of parentheses.

```racket
/use racket.txt
define (f x y)
    +
        x
      // does nothing, since no operators above this indentation level
      y
// lower indentation level closes define and + 
```
will generate
```racket
(define (f x y)
    (+
        x
      y))
```

An esoteric variant of the first punctuation example:

```racket
/use racket.txt
define (f x y)
    display x
   // trigger a closing parenthesis for display x
   display y
  // trigger a closing parenthesis for display y
  + x y
// close the define
```

If you want, you can use a directive to remove even more parentheses from the `fact n` example:
```racket
/use racket.txt
/def fact 1
define fact n
    if = n 0
        1
        * n fact - n 1
```
