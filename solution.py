from utils import *

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units
d1_unit = [[rows[i]+cols[i] for i in range(len(rows))]]
d2_unit = [[rows[::-1][i]+cols[i] for i in range(len(rows))]]

# TODO: Update the unit list to add the new diagonal units
unitlist = unitlist + d1_unit + d2_unit

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

# implement naked pairs
def naked_twins(values_para):
    values = values_para.copy()
    potential_twins = [box for box in values.keys() if len(values[box]) == 2]
    naked_twins = [[box1,box2] for box1 in potential_twins
                                for box2 in potential_twins
                                    if box2 in peers[box1] and values[box1] == values[box2] and box1 < box2]

    for naked_twin in naked_twins:
        box1, box2 = naked_twin
        digits = values[box1]
        
        # 1- compute intersection of peers
        peers_twin = peers[box1] & peers[box2]
        
        # 2- Delete the two digits in naked twins from all common peers.
        for peer_twin in peers_twin:
            if len(values[peer_twin]) >= 2:
                for digit in digits:
                    values = assign_value(values, peer_twin, values[peer_twin].replace(digit,''))
    return values

# implement naked triples
def naked_triples(values_para):
    values = values_para.copy()
    potential_triples = [box for box in values.keys() if len(values[box]) >= 2 and len(values[box]) <= 3]
    naked_triples = [[box1, box2, box3]
                    for box1 in potential_triples
                        for box2 in potential_triples
                            for box3 in potential_triples
                                if box1 in peers[box2] and box1 in peers[box3] and box2 in peers[box3]
                                 and len(set(values[box1] + values[box2] + values[box3])) == 3
                                 and box1 < box2 and box2 < box3]

    for naked_triple in naked_triples:
        box1, box2, box3 = naked_triple
        digits = set(values[box1] + values[box2] + values[box3])
        
        # 1- compute intersection of peers
        peers_triple = peers[box1] & peers[box2] & peers[box3]
        
        # 2- Delete the three digits in naked triples from all common peers.
        for peer_triple in peers_triple:
            if len(values[peer_triple]) >= 2:
                for digit in digits:
                    #values = assign_value(values, peer_triple, values[peer_triple].replace(digit,''))
                    values[peer_triple] = values[peer_triple].replace(digit,'')
    return values

# implement naked quads
def naked_quads(values_para):
    values = values_para.copy()
    potential_quads = [box for box in values.keys() if len(values[box]) >= 2 and len(values[box]) <= 4]
    naked_quads = [[box1, box2, box3, box4]
                    for box1 in potential_quads
                        for box2 in potential_quads
                            for box3 in potential_quads
                               for box4 in potential_quads
                                if box1 in peers[box2] and box1 in peers[box3] and box2 in peers[box3]
                                 and box4 in peers[box1] and box4 in peers[box2] and box4 in peers[box3]
                                 and len(set(values[box1] + values[box2] + values[box3] + values[box4])) == 4
                                 and box1 < box2 and box2 < box3 and box3 < box4]

    for naked_quad in naked_quads:
        box1, box2, box3, box4 = naked_quad
        digits = set(values[box1] + values[box2] + values[box3] + values[box4])
        
        # 1- compute intersection of peers
        peers_quad = peers[box1] & peers[box2] & peers[box3] & peers[box4]
        
        # 2- Delete the four digits in naked quads from all common peers.
        for peer_quad in peers_quad:
            if len(values[peer_quad]) >= 2:
                for digit in digits:
                    #values = assign_value(values, peer_quad, values[peer_quad].replace(digit,''))
                    values[peer_quad] = values[peer_quad].replace(digit,'')
    return values

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values


def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    # TODO: Implement only choice strategy here
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)

        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)

        # Eliminate values using the naked twins strategy
        values = naked_twins(values)

        # Eliminate values using the naked triples strategy
        values = naked_triples(values)

        # Eliminate values using the naked quads strategy
        values = naked_quads(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])

        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after

        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
