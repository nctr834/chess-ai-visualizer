## Installation

### Download and install the latest releases: (Requires Python 3.7+):

pip install chess

pip install pygame

pip install numpy

### What to do

You can simply play chess vs AI normally, or you can choose to visualize the AI's "thought process."

If visualization is on:

- When the square colors are dark green, that indicates the number of moves in the line being equal to the depth.

- When the square colors are a light magenta-like color, that indicates the number of moves in the line being equal to the depth - 1

- When the square colors are a dark magenta-like color, that indicates the number of moves in the line being equal to the depth - 2

##### If you are on Windows, a black screen might pop up when not visualizing AI. If this happens, you may have to alt-tab from the black screen, or run this on a different OS (i.e., MacOS). For some reason, this happens on windows when using multithreading and pygame.

There are buttons on the UI for choosing to show AI thought process, forcing the AI to make a move, and loading a random board state.

### Controls

Left and right arrow keys undo and redo a move, respectively.

Space bar resets the board to the initial board loaded on launch.

## Algorithms Used

### Negamax
Negamax is a variant of the minimax algorithm which has same efficiency, but less code. It does this based on the fact that max(a,b) = -min(-a,-b). The minimax algorithm is a search algorithm which makes use of game trees and includes a maximizing player (white pieces), and a minimizing player (black pieces). The maximizing player wants to maximize the result, and the minimizing player wants to minimize the result. To do that, Depth First Search is used. The algorithm goes to a depth of zero, and then backtracks, comparing all child values. Depending on the turn, the maximum value or minimum value is passed to their parent. These values are determined by an evaluation function, which evaluates the current position of the board, not considering attacks.

##### Alpha-beta pruning
Alpha-beta pruning is a way to eliminate branches of the search tree that aren't needed, greatly reducing amount of computations. It works by keeping track of the best possible score for the maximizing player (alpha) and the best possible score for the minimizing player (beta). If the maximizing player can ever guarantee a score greater than beta, then the minimizing player will never choose that branch, so it can be eliminated. Similarly, if the minimizing player can guarantee a score less than alpha, then the maximizing player will never choose that branch, so it can be eliminated.

Alpha-beta pruning is why you don't typically see lines which include the number of moves equal to the depth.

### Quiescence Search (only used when AI's "thoughts" aren't being shown)
This search is used with negamax and alpha-beta pruning. It is a way to improve the evaluation of a position by searching the tree of possible moves to a certain depth, and then evaluating the position with more depth. This search only looks at captures moves, which is done to avoid making a move that looks good but actually loses material on the next move(s) from a capture. For example, if a queen thinks it's winning a piece, but the opponent can actually take the queen on the next move (which isn't seen because of the limited depth), then the queen should not take the piece.
