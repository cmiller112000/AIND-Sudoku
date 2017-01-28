# AIND - Solve a diagonal sudoko puzzle
# Cheryl Miller 1/27/2017
# Jan cohort
#
#  using the following rules:
#   eliminate -
assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'
rcols = cols[::-1]

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def printsorted(mydict):
    outstr = ""
    lastrow = ""
    for key in sorted(mydict):
        if lastrow == "":
            lastrow = key[0]
        elif lastrow != key[0]:
            print("\n" + outstr)
            outstr=""
            lastrow = key[0]
        outstr = outstr + "  %s: %s" % (key, mydict[key])
    print ("\n" + outstr)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers

    # check each unit, find any values that are of length 2, these are potential twin candidates
    for unit in unitlist:
        two_values = [box for box in unit if len(values[box]) == 2]
        twins = []
        for two_value in two_values:
        # for each 2 digit value found, find its twins.
        # save off any twins found so we don't double process it
            if two_value in twins:
                continue
            twins = [box for box in unit if (box != two_value and values[two_value] == values[box])]
        # if we find a twin, there should only be one that equals the current value we're processing
            if len(twins) == 1:
                # now for each other box in this unit, find the 'non-twins'
                for box in unit:
                    if values[box] != values[two_value]:
                        # and for each non-twin, remove any digits in it that are in the current
                        # 2 digit value, because only the current value and its twin can contain
                        # these 2 digits.
                        for d in values[two_value]:
                            if d in values[box]:
                                assign_value(values,box, values[box].replace(d,''))
    return values

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# Add 2 new units one for each diagonal
diag_units = []
d1 = []
d2 = []
for i in range(len(rows)):
    d1.append(rows[i] + cols[i])
    d2.append(rows[i] + rcols[i])
diag_units.append(d1)
diag_units.append(d2)

#unitlist = row_units + column_units + square_units
# + the new diag_units as well to solve a the diagonal sudoku
unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

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
    print("")

def eliminate(values):
    # for each box that has a single digit, it must already be solved, so we remove this digit
    # from all peer boxes
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values,peer, values[peer].replace(digit,''))
    return values

def only_choice(values):
    # if all boxes in a unit are solved except one, that last one has only
    # one choice and can only be the last unused digit
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values,dplaces[0],digit)
    return values

def reduce_puzzle(values):
    # repeatedly apply our solution rules until either its solved, or we stall
    # and cannot solve this version

    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    # solve the the puzzle, if we stall, try a finding boxes with the least number of possible
    # values, and try each one in a depth first search manner, until the puzzle is solved.
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!
    # Chose one of the unfilled square s with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
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
    values=grid_values(grid)
    values=search(values)
    return values

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
