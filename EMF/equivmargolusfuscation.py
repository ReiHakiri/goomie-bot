import EMF.boolean_logic as bl
import random

def block_substitute(s: bl.Statement,
                     block_depth: int,
                     eq_classes: list[list[bl.Statement]]) -> bl.Statement:
    if s.depth() < block_depth:
        return s.copy()

    context = []

    skeleton = s.get_skeleton(block_depth - 1, context)

    same = eq_classes[skeleton.table_id(2 ** (block_depth - 1))]

    new_skeleton = skeleton

    if len(same) != 0:
        new_skeleton = random.choice(same)

        for _ in range(2 ** (block_depth - 1) - len(context)):
            context.append(bl.rand_statement(2 ** (block_depth - 1), block_depth - 1,
                                             bl.STD_CONST,
                                             bl.STD_UNARY,
                                             bl.STD_BINARY))

    new_context = []

    for context_s in context:
        new_context.append(block_substitute(context_s, block_depth, eq_classes))

    return new_skeleton.substitute(new_context)

def equivmargolusfuscate(s: bl.Statement, n_iterations: int, verbose: bool = False) -> bl.Statement:
    result = s

    if result.depth() < 15:
        result = result.to_cf().to_std()

    first_phase = True

    for i in range(n_iterations):
        if verbose:
            if i % 10 == 0:
                print(f'Percentage done: {100 * i / n_iterations:.4f}%')

        if first_phase:
            result = block_substitute(result, 3, bl.STD_EQ_CLASSES)

        else:
            context = []
            skeleton = result.get_skeleton(2, context)

            new_context = []

            for context_s in context:
                new_context.append(block_substitute(context_s, 3, bl.STD_EQ_CLASSES))

            result = skeleton.substitute(new_context)

        first_phase = not first_phase

    return result.to_std()