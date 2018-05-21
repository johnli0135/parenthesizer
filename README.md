# Parenthesizer

A command line utility that uses whitespace and punctuation rules to generate properly parenthesized code of LISP dialects.

Usage: `python parenthesizer.py <input file>`

## Directives

Knowledge of operator arity is given through directives. A directive is any line where the first non-whitespace character is a slash.

`/use f`: process a file `f` and include the results in the current file.

`/def f [arity]`: define an operator `f` to take `arity` arguments, or to take a variable number of arguments if `arity` is not specified.

`//`: line comment.

`/off`: disable any processing until the next `/on` directive.

`/on`: re-enable processing.

## Basic example

Since directives tell the parenthesizer the arity of many common operators, many parentheses can be omitted.

For example:
```C
define (fact n)
    if = n 1
        1
        (fact - n 1)
```

## Punctuation

A comma, semicolon, or period can serve as a closing parenthesis for an operator that takes a variable number of arguments:

```C
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

```C
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

```C
/use racket.txt
define (f x y)
    display x
   // trigger a closing parenthesis for display x
   display y
  // trigger a closing parenthesis for display y
  + x y
// close the define
```
