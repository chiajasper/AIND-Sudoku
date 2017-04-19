assignments = []

#Providing the environment of the sudoku game
rows = 'ABCDEFGHI'
cols = '123456789'

def cross(a, b):
    return [s+t for s in a for t in b]

#simple function to pair rows and cols symbol for diagonal line
def pair(a, b):
    return [ a[i] + b[i] for i in range(len(a))]


boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = [ pair(rows, cols) , pair(rows, list(reversed(cols)))]
# including diagonal units for the diagonal sudoku game
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)



def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    nTwins = []
    for box in boxes:
        # Only consider box with 2 possible digits for the naked twin scenario
        if len(values[box]) == 2:
            #search for twin in my peers
            for peer in peers[box]:
                # note that we want to avoid adding the duplicate pair in reverse form
                if values[peer] == values[box] and (peer, box) not in nTwins:
                    nTwins.append((box,peer))

    # Eliminate the naked twins as possibilities for their peers
    for (t1, t2) in nTwins:
        for box in peers[t1].intersection(peers[t2]):
            for v in values[box]:
                if v in values[t1]:
                    # eliminate all digits that collide with the nake twins
                    assign_value(values, box, values[box].replace(v, ''))
    return values

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in a for t in b]

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Input: A grid in string form.
    Output: A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    # get a list of all boxes with confirmed digit
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        # based on the solved box, we can eliminate the digit from all its peers since it is violating the sudoku rule
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit,''))
    return values

def only_choice(values):
    for unit in unitlist:
        for digit in '123456789':
            # if the digit only appears in one box of the unit, we know the box must be set by that digit
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # applying all the constraints
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # stop the loop if we cannot make any more progress
        stalled = solved_values_before == solved_values_after
        # if any box has empty value, it means we must have done something wrong (assigning the wrong value)
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    # run through the constraints
    values = reduce_puzzle(values)
    # fail fast
    if values is False:
        return False
    # return if we have finished the game
    if all(len(values[s]) == 1 for s in boxes):
        return values

    # find the box with the fewest possibility to start the search
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # for each possible digit, we assume it is the right answer
    #   and traverse through the rest of the board to see if we can find the solution
    for value in values[s]:
        new_sudoku = values.copy()
        assign_value(new_sudoku, s, value)
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
