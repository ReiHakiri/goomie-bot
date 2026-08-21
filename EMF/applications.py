import EMF.boolean_logic as bl
import EMF.equivmargolusfuscation as emf

def exact_sat_formula(l: list[bool], start_n: int = 0) -> bl.Statement:
    result = bl.Var(start_n)

    if not l[0]:
        result = bl.Not(result)

    for i, b in enumerate(l[1:]):
        next_var = bl.Var(start_n + i + 1)

        if not b:
            next_var = bl.Not(next_var)

        result = bl.And(result, next_var)

    return result

def obfuscated_sat_formula(l: list[bool], n_iterations: int, start_n: int = 0, verbose: bool = False) -> bl.Statement:
    return emf.equivmargolusfuscate(exact_sat_formula(l, start_n), n_iterations, verbose)

def locked_program(program: bl.MultiStatement, password: list[bool], n_iterations: int,
                   other_rand: bool = False, verbose: bool = False) -> bl.MultiStatement:
    result = []

    password_f = exact_sat_formula(password, program.n_var())

    n_var_password_f = password_f.n_var()

    for i, component in enumerate(program.statements):
        if verbose:
            print(f'Doing component {i + 1} of {len(program.statements)}')

        bit_f = bl.Or(bl.Not(password_f), component)

        if other_rand:
            wrong = bl.rand_statement(n_var_password_f, 5, bl.STD_CONST, bl.STD_UNARY, bl.STD_BINARY)

        else:
            wrong = bl.Contradiction()

        bit_f = bl.And(bit_f, bl.Or(password_f, wrong))

        bit_f = emf.equivmargolusfuscate(bit_f, n_iterations, verbose)

        result.append(bit_f)

    return bl.MultiStatement(result)