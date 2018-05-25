# Parenthesizer

A command line utility that generates properly parenthesized code for LISP dialects.
With the help of directives that give information about operator arity,
whitespace/punctuation rules, and a few special characters (`_`, `|`, and `:`),
arbitrarily many parentheses can be omitted.
This makes it easier to write code quickly without having to worry about syntax errors.

Usage: `python parenthesizer.py <input file>` outputs properly parenthesized code

## Example

An implementation of mergesort:
```racket
/use racket.txt
/def mergesort 1
define (mergesort x)
    if or (empty? x) (empty? rest x)
        x
        letrec : | half   floor / (length x) 2
                 | left   take x half
                 | right  drop x half
                 | merge  lambda (a b)
                             cond
                                 | (empty? a)            b
                                 | (empty? b)            a
                                 | (<= first a first b)  cons first a (merge rest a b)
                                 | else                  cons first b (merge a      rest b)
            (merge (mergesort left) (mergesort right))
```

The properly parenthesized output:
```racket
(define (mergesort x)
    (if (or (empty? x) (empty? (rest x)))
        x
        (letrec ([half (floor (/ (length x) 2))]
                 [left (take x half)]
                 [right (drop x half)]
                 [merge (lambda (a b)
                             (cond
                                 [(empty? a) b]
                                 [(empty? b) a]
                                 [(<= (first a) (first b)) (cons (first a) (merge (rest a) b))]
                                 [else (cons (first b) (merge a (rest b)))]))])
            (merge (mergesort left) (mergesort right)))))
```

## Directives

Knowledge of operator arity is given through directives. A directive is any line where the first non-whitespace character is a slash.

`/use f`: process the contents of `f` (pretty much the same as C's `#include`).

`/def f n`: define an operator `f` to take `n` arguments, or to take a variable number of arguments if `n` is not specified.

`/del f ...`: delete `f` and any additional arguments from the list of known operators.

`/mask f ...`: treat `f` and any additional arguments as normal identifiers rather than operators.

`/unmask f ...`: undo `/mask f ...`.

`//`: line comment.

`/off`: disable any parenthesizing until the next `/on` directive (i.e. copy lines verbatim).

`/on`: re-enable parenthesizing.

## Basic transformations

Since directives tell the parenthesizer the arity of common operators, many parentheses can be omitted.

For example,
```racket
(define (fact n)
    (if (= n 0)
        1
        (* n (fact (- n 1)))))
```
can be written as
```racket
/use racket.txt
(define (fact n)
    if = n 0
        1
        * n (fact - n 1))
```
or even
```racket
/use racket.txt
/def fact 1
(define fact n
    if = n 0
        1
        * n fact - n 1)
```

## Punctuation

A period serves as a closing parenthesis for an operator that takes a variable number of arguments.

```racket
/use racket.txt
define one-to-nine
    append list 1 2 3. list 4 5 6. list 7 8 9..
```

A colon at the end of an operator name forces the operator to take a variable number of arguments:
```
// becomes (+ 1 2 3) => 6
+: 1 2 3.

// becomes (> 5 4 3 2 1) => #t
>: 5 4 3 2 1.
```

## Whitespace

Going from higher to lower-or-same indentation closes any blocks in between.

End-of-file is treated as a blank line of lowest possible indentation level.

Indentations are preserved after addition of parentheses.

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

Using whitespace, you can drop the trailing `..` from the earlier punctuation example:
```racket
define one-to-nine
    append list 1 2 3. list 4 5 6. list 7 8 9
```

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
;            this has to match [merge, so the lambda and cond have to be closed before it ^
            (merge (mergesort left) (mergesort right))
```
generates
```racket
(define (mergesort x)
    (if (or (empty? x) (empty? (rest x)))
        x
        (letrec ([half (floor (/ (length x) 2))]
                [left (take x half)]
                [right (drop x half)]
                [merge (lambda (a b)
                            (cond
                                [(empty? a) b]
                                [(empty? b) a]
                                [(<= (first a) (first b)) (cons (first a) (merge (rest a) b))]
                                [else (cons (first b) (merge a (rest b)))]))])
;                          the "invisible" parentheses generated by the ] ^^
            (merge (mergesort left) (mergesort right)))))
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

## Pipes and colons

A single pipe character can be used in place of square brackets. It generates an opening square bracket
that is automatically closed by the above rules on indentation and explicit use of parentheses. These can be
used to simplify the appearance of expressions that involve collections of subexpressions (e.g. `let` or `cond` forms).

Colons can be used like pipe characters, but they generate opening parentheses instead of opening square brackets.

Here's an example of both being used in an implementation of quicksort:
```racket
define (quicksort x)
    if empty? x
        x
        letrec : | pivot  first x
                 | tail   rest x
                 | lower  filter lambda (y) <= y pivot. tail
                 | upper  filter lambda (y) > y pivot. tail
            append (quicksort lower) (list pivot) (quicksort upper)
```

