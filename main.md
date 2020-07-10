title: "computing-nash-equilibria-in-R"
description: Using vertex enumeration to compute equilibria in R
output: md_document
---



There are a number of ways of computing Nash equilibria for Normal Form Games 
defined by two matrices \((A, B)\). The approach I'm going to describe here is
to use vertex enumeration. This is not necessarily the most efficient algorithm
(that honor goes to 
[The Lemke Howson algorithm](https://vknight.org/gt/chapters/07/)). The vertex 
enumeration algorithm involves finding vertices of Polytopes and R has a nice 
library for that called `vertexenum`.

### The theory (skip if you just want the code)

You can read my course notes on this here: 
[vknight.org/gt/chapters/06/](https://vknight.org/gt/chapters/06/) but 
here is a brief outline:

- Consider a two player game defined by 
  \((A, B)\in\mathbb{R}^{({m \times n})^2}\) where \(A\) denotes the row 
  player's utilities and \(B\) the column player's utilities.
- Define the row player's best response polytope as:

  \[
  \mathcal{P} = \left\{x\in\mathbb{R}^{m}\;|\;x\geq 0; xB\leq 1\right\}
  \]
  
- Define the row player's best response polytope as:

  \[
  \mathcal{Q} = \left\{y\in\mathbb{R}^{n}\;|\;Ay\leq 1; y\geq 0right\}
  \]
  
- Elements of \(\mathcal{P}, \mathcal{Q}\) are labelled by the defining 
  inequalities for which they are binding. For example in \(P\) for \(m=3\) the 
  vertex \(x=(0,0,0)\) would have labels \(1, 2, 3\) as the first 3 inequlities 
  of \(\mathcal{P}\) are in fact equalities. In \(Q\) for \(n=2\) the  vertex 
  \(y=(0,0)\) would have labels \(4, 5\) as the last 2 inequlities of 
  \(\mathcal{Q}\) are in fact equalities.
  
- Nash equilibria corresponds to pairs of vertices of \(\mathcal{P}\) and 
  \(\mathcal{Q}\) for which the union of the labels give the full set of 
  integers from \(1\) to \(m + n\). One such pair will always be the pair of 
  vertices with all values 0 (as in the previous bullet point)
  however this is a so called "artificial" equilibria.    
- To convert these pairs of vertices to pairs of strategies, we normalise so 
  that their elements sum to 1.
  
  
Throughout this blog post we will use the following game as an example:

\[
  A = \begin{pmatrix}
    3 & 1\\
    0 & 2
    \end{pmatrix}
  \quad
  B = \begin{pmatrix}
    2 & 1\\
    0 & 3
    \end{pmatrix}
\]

### Implementation of vertex enumeration in R.

We are going to make use of the `vertexenum` library which given a general 
polytope will return all vertices. This library's function `enumerate.vertices` 
takes 2 inputs `M, b` that define the Polytope in the general form as 
\(Mx\leq b\).  So the first step is to create these two inputs from a given set 
of payoff matrices.


```r
#' Returns the matrix M that corresponds to the column players best response
#' polytope defined by the row players utility matrix A.
#' 
#' @param A The row players utility matrix.
get_linear_system_coeffients <- function(A) {
  dimensions <- dim(A)
  number_of_row_strategies <- dimensions[2]
  positivity_constraints <- -diag(number_of_row_strategies)
  do.call(rbind, list(positivity_constraints, A))
}
```

For example if we use this on the row players utility matrix of our running 
example:


```r
A <- rbind(c(3, 1), c(0, 2))
A
```

```
##      [,1] [,2]
## [1,]    3    1
## [2,]    0    2
```

We get:


```r
get_linear_system_coeffients(A)
```

```
##      [,1] [,2]
## [1,]   -1    0
## [2,]    0   -1
## [3,]    3    1
## [4,]    0    2
```

We also need to get the right hand side vector:


```r
#' Returns the vector b that corresponds to the column players best response
#' polytope defined by the row players utility matrix A.
#' 
#' @param A The row players utility matrix.
get_linear_system_rhs <- function(A) {
  dimensions <- dim(A)
  number_of_col_strategies <- dimensions[1]
  number_of_row_strategies <- dimensions[2]
  c(rep(0, number_of_row_strategies), rep(1, number_of_col_strategies))
}
```

If we now use this we get:


```r
get_linear_system_rhs(A)
```

```
## [1] 0 0 1 1
```

We can use the `vertexenum` library to get the vertices of the row player's 
polytope:


```r
library(vertexenum)
M <- get_linear_system_coeffients(A)
b <- get_linear_system_rhs(A)
enumerate.vertices(M, b)
```

```
##           [,1] [,2]
## [1,] 0.1666667  0.5
## [2,] 0.0000000  0.5
## [3,] 0.3333333  0.0
## [4,] 0.0000000  0.0
```

For the row player we need to consider the transpose of \(B\) 
(as all of the code we have written is from the perspective of the column player):


```r
B <- rbind(c(2, 1), c(0, 3))
M <- get_linear_system_coeffients(t(B))
b <- get_linear_system_rhs(t(B))
enumerate.vertices(M, b)
```

```
##      [,1]      [,2]
## [1,]  0.5 0.1666667
## [2,]  0.0 0.3333333
## [3,]  0.5 0.0000000
## [4,]  0.0 0.0000000
```

Given a vertex we want to know its labels (which of the defining inequalities 
are binding) so let us write a function to do that:


```r
library(berryFunctions)
#' Returns the set of labels of a given vertex for the polytope defined
#' by M and b.
#' 
#' @param vertex The vertex
#' @param M The coefficient matrix defining the polytope
#' @param b The right hand side vector defining the polytope
get_labels <- function(vertex, M, b) {
  almost.equal(c(M %*% vertex), b)
}
```

For example:


```r
get_labels(c(1 / 2, 0), M, b)
```

```
## [1] FALSE  TRUE  TRUE FALSE
```

We can now compute all vertices of a polytope and the corresponding labels:


```r
#' Returns the set of vertices and labels for the column player's best 
#' response polytope.
#' The format of the output is:
#' 
#' x_1 x_2 ... x_n B_1 B_2 ... B_(m+n)
#'
#' Where B_i is 0 (False) or 1 (True) dependent on whether or not the vector has
#' label i.
#' 
#' @param A The row players utility matrix.
get_vertices <- function(A) {
  M <- get_linear_system_coeffients(A)
  b <- get_linear_system_rhs(A)
  vertices <- enumerate.vertices(M, b)
  vertices <- vertices[rowSums(vertices) != 0, ]

  labels <- t(apply(vertices, 1, function(vertex) {
    get_labels(vertex, M, b)
  }))
  cbind(vertices, labels)
}
```


```r
col_vertices <- get_vertices(A)
row_vertices <- get_vertices(t(B))
col_vertices
```

```
##           [,1] [,2] [,3] [,4] [,5] [,6]
## [1,] 0.1666667  0.5    0    0    1    1
## [2,] 0.0000000  0.5    1    0    0    1
## [3,] 0.3333333  0.0    0    1    1    0
```


```r
row_vertices
```

```
##      [,1]      [,2] [,3] [,4] [,5] [,6]
## [1,]  0.5 0.1666667    0    0    1    1
## [2,]  0.0 0.3333333    1    0    0    1
## [3,]  0.5 0.0000000    0    1    1    0
```

Using all of the above, we can now consider two potential vertices, and their 
labels and see if they form a fully labeled pair:



```r
#' Returns whether or not a given pair of vertices is fully labeled.
#' Takes a vertex x in the following form:
#' 
#' x_1 x_2 ... x_n B_1 B_2 ... B_(m+n)
#'
#' Where B_i is 0 (False) or 1 (True) dependent on whether or not the vector has
#' label i.
#' 
#' @param x A row player vertex
#' @param y A column player vertex
#' @param number_of_row_strategies  # TODO Remove this as an argument.
#' @param number_of_col_strategies
is_fully_labeled <- function(x,  
                             y, 
                             number_of_row_strategies, 
                             number_of_col_strategies) {
  dimension <- number_of_row_strategies + number_of_col_strategies
  row_labels <- (which(x[-c(1:number_of_row_strategies)] > 0) %% dimension)
  col_labels <- (which(y[-c(1:number_of_col_strategies)] > 0) + number_of_row_strategies) %% dimension
  setequal(union(row_labels, col_labels), 0:(dimension - 1))
}
```


```r
x <- row_vertices[3, ]
y <- col_vertices[3, ]
is_fully_labeled(x, y, 2, 2)
```

```
## [1] TRUE
```



```r
x <- row_vertices[3, ]
y <- col_vertices[2, ]
is_fully_labeled(x, y, 2, 2)
```

```
## [1] FALSE
```
This gives us all the tools we need to iterate over all pairs of vertices and identify the fully labeled vertex pairs (and thus the Nash equilibria):


```r
#' Return the nash equilibria for a two player game defined by utility matrices 
#' A and B
#'
#' @param A The row player utility matrix
#' @param B The column player utility matrix
obtain_nash_equilibra <- function(A, B) {
  dimensions <- dim(A)
  number_of_row_strategies <- dimensions[1]
  number_of_col_strategies <- dimensions[2]

  row_vertices <- get_vertices(t(B))
  col_vertices <- get_vertices(A)
  number_of_row_vertices <- dim(row_vertices)[1]
  number_of_col_vertices <- dim(col_vertices)[1]

  output <- c()
  for (i in 1:number_of_row_vertices) {
    row_vertex_and_labels <- row_vertices[i, ]
    for (j in 1:number_of_col_vertices) {
      column_vertex_and_labels <- col_vertices[j, ]
      if (is_fully_labeled(
        x = row_vertex_and_labels,
        y = column_vertex_and_labels,
        number_of_row_strategies = number_of_row_strategies,
        number_of_col_strategies = number_of_col_strategies
      )) {
        row_vertex <- head(row_vertex_and_labels, number_of_row_strategies)
        row_strategy <- row_vertex / sum(row_vertex)
        column_vertex <- head(column_vertex_and_labels, number_of_col_strategies)
        column_strategy <- column_vertex / sum(column_vertex)
        
        max_size <- max(number_of_row_strategies, number_of_col_strategies)
        length(row_strategy) <- max_size
        length(column_strategy) <- max_size
        
        output <- rbind(output, row_strategy, column_strategy)
      }
    }
  }
  output
}
```


```r
ne <- obtain_nash_equilibra(A, B)
ne
```

```
##                 [,1] [,2]
## row_strategy    0.75 0.25
## column_strategy 0.25 0.75
## row_strategy    0.00 1.00
## column_strategy 0.00 1.00
## row_strategy    1.00 0.00
## column_strategy 1.00 0.00
```
We see there that we have 3 Nash equilibria. We can confirm the output using the
Python [nashpy](https://nashpy.readthedocs.io/) library:


```python
#import nashpy as nash
#import numpy as np
#A = np.array([[3, 1], [0, 2]])
#B = np.array([[2, 1], [0, 3]])
#game = nash.Game(A, B)
#for eq in game.vertex_enumeration():
#  print(eq)
```

We can experiment with a slightly larger game, for example here is rock 
paper scissors:


```r
rps <- rbind(c(0, -1, 1), c(1, 0, -1), c(-1, 1, 0))
rps_row <- rps + 2
rps_col <- -rps + 2
ne <- obtain_nash_equilibra(rps_row, rps_col)
ne
```

```
##                      [,1]      [,2]      [,3]
## row_strategy    0.3333333 0.3333333 0.3333333
## column_strategy 0.3333333 0.3333333 0.3333333
```

And here is a non square game:


```r
A <- rbind(c(3, 3), c(2, 5), c(0, 6))
B <- rbind(c(3, 2), c(2, 6), c(3, 1))
ne <- obtain_nash_equilibra(A, B)
ne
```

```
##                      [,1]      [,2]      [,3]
## row_strategy    0.8000000 0.2000000 0.0000000
## column_strategy 0.6666667 0.3333333        NA
## row_strategy    0.0000000 0.3333333 0.6666667
## column_strategy 0.3333333 0.6666667        NA
## row_strategy    1.0000000 0.0000000 0.0000000
## column_strategy 1.0000000 0.0000000        NA
```

There are a number of other (**better**) algorithms for computing equilbria and
the python [Nashpy](https://nashpy.readthedocs.io/) library document has
reference material on them.

If you have any thoughts/improvement on the R code (I'm not terribly satisfied with how `obtain_nash_equilibria` is written for example), I'd welcome your thoughts: [@drvinceknight](http://twitter.com/drvinceknight).
