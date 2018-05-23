# Parenthesizer

A command line utility that uses whitespace and punctuation rules to generate properly parenthesized code for LISP dialects.

Usage: `python parenthesizer.py <input file>`

## Directives

Knowledge of operator arity is given through directives. A directive is any line where the first non-whitespace character is a slash.

`/use f`: process the contents of `f` (pretty much the same as C's `#include`).

`/def f n`: define an operator `f` to take `n` arguments, or to take a variable number of arguments if `n` is not specified.

`/mask f ...`: treat `f` and any additional arguments as normal identifiers rather than operators.

`/unmask f ...`: undo `/mask f ...`.

`//`: line comment.

`/off`: disable any parenthesizing until the next `/on` directive (i.e. copy lines verbatim).

`/on`: re-enable parenthesizing.

## Simple operators

Since directives tell the parenthesizer the arity of common operators, many parentheses can be omitted.

For example,
```racket
/use racket.txt
(define (fact n)
    if = n 0
        1
        * n (fact - n 1))
```
will generate
```racket
(define (fact n)
    (if (= n 0)
        1
        (* n (fact (- n 1)))))
```

If you really want, you can use a directive to remove even more parentheses:
```racket
/use racket.txt
/def fact 1
(define fact n
    if = n 0
        1
        * n fact - n 1)
```

## Punctuation

A period can serve as a closing parenthesis for an operator that takes a variable number of arguments.

```racket
/use racket.txt
define (f x y) 
    display list x y x.
    display list y x y.
    + x y.
```

A colon at the end of an operator name forces the operator to take a variable number of arguments:
```
// 6
+: 1 2 3.

// #t
>: 5 4 3 2 1.
```

## Whitespace

Going from higher to lower-or-same indentation closes any blocks in between.

End-of-file is treated as a blank line of lowest possible indentation level.

Indentations are preserved after addition of parentheses.

These rules imply that any arguments to a function must be indented more than the function name.

For example,
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

Variant of the first punctuation example, using whitespace instead:
```racket
/use racket.txt
define (f x y)
    display list x y x
    // close list
    display list y x y
    // close list
    + x y
// close the define
```

Example of both punctuation and indentation being used together:
```racket
define one-to-nine
    append list 1 2 3. list 4 5 6. list 7 8 9.
```
(Technically, the last `.` is unnecessary, as the new indentation level will close both the `list` and the `append`
expressions.)

## Escaping

To prevent an operator from being automatically parenthesized, prefix it with an underscore. (Or use `/mask` and `/unmask` if many operators need to be escaped over many lines of code.)

For example, to construct a list of basic arithmetic operators,
```racket
list + - * /
```
erroneously generates
```racket
(list (+ (- (* (/)))))
```
but

```racket
list _+ _- _* _/
```
generates
```racket
(list + - * /)
```
as desired.

## Parentheses

An explicit closing parenthesis (or square bracket or curly brace) closes any "invisible open parentheses"
opened by operators.

This takes advantage of the fact that visible parentheses have to be balanced in order to deduce where closing
parentheses should be added for operators that take a variable number of arguments.

For example, in the following implementation of merge sort, the "invisible parentheses" opened by `lambda` and
`cond` are closed by the `]` that corresponds to `[merge`:
```racket
define (mergesort x)
    if or (empty? x) (empty? rest x)
        x
        letrec ([half   floor / (length x) 2]
                [left   take x half]
                [right  drop x half]
                [merge  lambda (a b)
                            cond
                                [(empty? a)            b]
                                [(empty? b)            a]
                                [(<= first a first b)  cons first a (merge rest a b)]
                                [else                  cons first b (merge a      rest b)]])
            (merge (mergesort left) (mergesort right))
```

Superfluous parentheses can also be added for clarity:
```racket
/use racket.txt
define (fact n)
   // = doesn't need to be parenthesized
   if (= n 0)
       1
       * n (fact - n 1)
```

