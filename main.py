"""
Sudoku Solver using MILP with HiGHS (highspy)

Solves a Sudoku puzzle using Mixed Integer Linear Programming
with binary decision variables x[r,c,v] indicating if cell (r,c) contains value v.
"""

import highspy



def solve_sudoku(puzzle):
    """
    Solve a Sudoku puzzle using MILP.
    
    Args:
        puzzle: 9x9 list of lists, with 0 representing empty cells
        
    Returns:
        Solved puzzle as 9x9 list, or None if no solution exists
    """
    n = 9
    block = 3
    values = range(1, n + 1)
    rows = range(n)
    cols = range(n)
    
    # Total number of binary variables (r, c, v)
    num_vars = n * n * n
    
    # -------------------------------
    # Build MILP model (Modern API)
    # -------------------------------
    h = highspy.Highs()
    h.silent()
    
    # Create binary variables
    x = h.addBinaries(num_vars)
    

        # Map (r, c, v) → flat index
    def var_index(r, c, v):
        return r * n * n + c * n + (v - 1)
    

        # Constraint 1: Each cell has exactly one value
    for r in rows:
        for c in cols:
            h.addConstr(sum(x[var_index(r, c, v)] for v in values) == 1)
    
    # Constraint 2: Each value appears once per row
    for r in rows:
        for v in values:
            h.addConstr(sum(x[var_index(r, c, v)] for c in cols) == 1)
    
    # Constraint 3: Each value appears once per column
    for c in cols:
        for v in values:
            h.addConstr(sum(x[var_index(r, c, v)] for r in rows) == 1)
    
    # Constraint 4: Each value appears once per 3×3 block
    for br in range(0, n, block):
        for bc in range(0, n, block):
            for v in values:
                h.addConstr(
                    sum(x[var_index(r, c, v)] 
                        for r in range(br, br + block)
                        for c in range(bc, bc + block)) == 1
                )
    
    # Constraint 5: Fix given numbers
    for r in rows:
        for c in cols:
            val = puzzle[r][c]
            if val != 0:
                h.addConstr(x[var_index(r, c, val)] == 1)

      # Solve (this is a feasibility problem, no objective needed)
    h.run()
    
    # Check if solution was found
    status = h.getModelStatus()
    if status != highspy.HighsModelStatus.kOptimal:
        print(f"No solution found. Solver status: {status}")
        return None
    
    # Extract solution using modern API
    solution = [[0 for _ in cols] for _ in rows]
    
    for r in rows:
        for c in cols:
            for v in values:
                idx = var_index(r, c, v)
                if abs(h.val(x[idx])) > 0.5:
                    solution[r][c] = v
    
    return solution


def print_sudoku(puzzle, title="Sudoku"):
    """Pretty print a Sudoku puzzle."""
    print(f"\n{title}:\n")
    for r in range(9):
        row = ""
        for c in range(9):
            val = puzzle[r][c]
            row += f"{val if val != 0 else '.'} "
            if (c + 1) % 3 == 0 and c < 8:
                row += "| "
        print(row)
        if (r + 1) % 3 == 0 and r < 8:
            print("-" * 21)
    print()


def validate_sudoku(puzzle):
    """Check if a completed Sudoku solution is valid."""
    n = 9
    
    # Check rows
    for r in range(n):
        if len(set(puzzle[r])) != n or sum(puzzle[r]) != 45:
            return False
    
    # Check columns
    for c in range(n):
        col = [puzzle[r][c] for r in range(n)]
        if len(set(col)) != n or sum(col) != 45:
            return False
    
    # Check 3x3 blocks
    for br in range(0, n, 3):
        for bc in range(0, n, 3):
            block = [puzzle[r][c] for r in range(br, br+3) for c in range(bc, bc+3)]
            if len(set(block)) != n or sum(block) != 45:
                return False
    
    return True


# -------------------------------
# Main execution
# -------------------------------
if __name__ == "__main__":
    # Example Sudoku puzzle (0 = empty)
    puzzle = [
        [5,3,0, 0,7,0, 0,0,0],
        [6,0,0, 1,9,5, 0,0,0],
        [0,9,8, 0,0,0, 0,6,0],
        [8,0,0, 0,6,0, 0,0,3],
        [4,0,0, 8,0,3, 0,0,1],
        [7,0,0, 0,2,0, 0,0,6],
        [0,6,0, 0,0,0, 2,8,0],
        [0,0,0, 4,1,9, 0,0,5],
        [0,0,0, 0,8,0, 0,7,9],
    ]
    
    print_sudoku(puzzle, "Original Puzzle")
    
    solution = solve_sudoku(puzzle)
    
    if solution:
        print_sudoku(solution, "Solved Sudoku")
        
        if validate_sudoku(solution):
            print("✓ Solution is valid!")
        else:
            print("✗ Solution is invalid!")
    else:
        print("No solution exists for this puzzle.")