# Parenthesizer

A command line utility that generates properly parenthesized code for Lisp dialects.
With the help of directives that give information about operator arity,
whitespace/punctuation rules, and a few special characters (`_`, `|`, `;`, and `:`),
arbitrarily many parentheses can be omitted.

Usage: `python parenthesizer.py <input file>` outputs properly parenthesized code

## Example

An implementation of mergesort:
```racket
/use racket
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

`/describe f ...`: emit a line comment describing operators `f ...` (e.g. whether they are currently bound,
their arity, and whether they are masked).

`//`: line comment.

`/off`: disable any parenthesizing until the next `/on` directive (i.e. copy lines verbatim).

`/on`: re-enable parenthesizing.

## Basic transformations

Many parentheses can be omitted already with knowledge of operator arity:
```racket
(define (fact n)
    (if (= n 0)
        1
        (* n (fact (- n 1)))))
```
can be written as
```racket
/use racket
/def fact 1
(define fact n
    if = n 0
        1
        * n fact - n 1)
```

## Punctuation

A semicolon serves as a closing parenthesis for an operator that takes a variable number of arguments.

```racket
/use racket
define one-to-nine
    append list 1 2 3. list 4 5 6. list 7 8 9;;
```

A colon at the end of an operator name forces the operator to take a variable number of arguments:
```
// becomes (+ 1 2 3) => 6
+: 1 2 3;

// becomes (> 5 4 3 2 1) => #t
>: 5 4 3 2 1;
```

A single colon forces the "operator ` `" to take a variable number of arguments. This is essentially
equivalent to an open parenthesis that can be automatically closed by semicolons, whitespace, and
deduction rules below.

## Whitespace

Going from higher to lower-or-same indentation closes any blocks in between.

End-of-file is treated as a blank line of lowest possible indentation level.

Indentations are preserved after addition of parentheses.

For example,
```racket
/use racket
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

Using whitespace, you can drop the trailing `;;` from the earlier punctuation example:
```racket
define one-to-nine
    append list 1 2 3; list 4 5 6; list 7 8 9
```

## Automatically deducing closing parentheses for variadic operators

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

## Pipes

A single pipe character can be used in place of square brackets, like a colon that only works on the empty
"operator ` `" and generates square brackets instead of parentheses.
These can be used to simplify the appearance of expressions that involve collections of subexpressions
(e.g. `let`, `cond`, and `match` expressions).

Here's an example of pipes being used in an implementation of quicksort:
```racket
/use racket
/def quicksort 1
define (quicksort x)
    match x
        | (list)           (list)
        | (list-rest p y)  let*-values : | (f)    lambda (a) <= a p
                                         | (l r)  partition f y
                               append (quicksort l) (list p) (quicksort r)
```

## Escaping

A downside of automatically parenthesizing operators based on their assumed arity is that it's difficult to
use operators as values.

For example, to construct a list of basic arithmetic operators,
```racket
list + - * /
```
erroneously generates
```racket
(list (+ (- (* (/)))))
```

To prevent an operator from being automatically parenthesized, prefix it with an underscore. (Or use `/mask` and `/unmask` if many operators need to be escaped over many lines of code.)

So
```racket
list _+ _- _* _/
```
will generate
```racket
(list + - * /)
```
as desired.

Another option is just not to use `/def` and rely only on the whitespace and punctuation rules.
The nice thing about this approach is that it requires no
knowledge of the particular Lisp dialect that the code is being written for and just relies on simple
transformations.

Here's mergesort from earlier written in this fashion:
```racket
define: (mergesort x)
    if: or: (empty? x) (empty? rest x)
        x
        letrec: : | half   floor: /: (length x) 2
                  | left   take: x half
                  | right  drop: x half
                  | merge  lambda: (a b)
                              cond:
                                  | (empty? a)                b
                                  | (empty? b)                a
                                  | (<= (first a) (first b))  cons: (first a) (merge rest a b)
                                  | else                      cons: (first b) (merge a      rest b)
            (merge (mergesort left) (mergesort right))
```
This approach just uses colons for parentheses that span multiple lines and allows whitespace and the positions of
visible parentheses to determine when they should be closed.
