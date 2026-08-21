from typing import Any, Optional, Self, Callable
import random
from sympy import Symbol
import sympy.logic.boolalg as slb

def all_lists(domain: list[Any], n: int):
    if n == 0:
        yield []

    else:
        for l in all_lists(domain, n - 1):
            for e in domain:
                yield l + [e]

class Statement:
    """
    Abstract class
    """
    def __str__(self) -> str:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return str(self)

    def copy(self) -> "Statement":
        raise NotImplementedError()

    def eval(self, v: list[bool]) -> bool:
        """
        Precondition:
        - len(v) == self.n_var()
        """
        raise NotImplementedError()

    def n_var(self) -> int:
        raise NotImplementedError()

    def is_tautology(self) -> bool:
        for v in all_lists([False, True], self.n_var()):
            if not self.eval(v):
                return False

        return True

    def table_id(self, n_vars: int) -> int:
        result = 0

        for i, v in enumerate(all_lists([False, True], n_vars)):
            if self.eval(v):
                result += 2 ** i
        
        return result

    def substitute(self, l: list["Statement"]) -> "Statement":
        raise NotImplementedError()

    def depth(self) -> int:
        raise NotImplementedError()
    
    def get_skeleton(self, n_depth: int, context: list["Statement"]) -> Optional["Statement"]:
        if n_depth == 0:
            self_c = self.copy()
        
            n = len(context)
        
            context.append(self_c)
        
            return Var(n)

    def to_sympy(self) -> slb.Boolean:
        raise NotImplementedError()

    def to_std(self) -> "Statement":
        raise NotImplementedError()

    def to_cf(self) -> "Statement":
        raise NotImplementedError()

class Var(Statement):
    def __init__(self, n: int) -> None:
        self.n = n

    def __str__(self) -> str:
        return f'x{self.n}'

    def copy(self) -> "Var":
        return Var(self.n)
    
    def eval(self, v: list[bool]) -> bool:
        return v[self.n]

    def n_var(self) -> int:
        return self.n + 1

    def substitute(self, l: list[Statement]) -> Statement:
        return l[self.n]

    def depth(self) -> int:
        return 1

    def get_skeleton(self, n_depth: int, context: list[Statement]) -> Statement:
        self_c = self.copy()

        n = len(context)

        context.append(self_c)

        return Var(n)

    def to_sympy(self) -> slb.Boolean:
        return Symbol(f'x{self.n}')

    def to_std(self) -> "Var":
        return self.copy()

    def to_cf(self) -> "Var":
        return self.copy()

class BinaryOp(Statement):
    def __init__(self, phi: Statement, tau: Statement) -> None:
        self.phi = phi
        self.tau = tau
    
    def copy(self) -> Self:
        return type(self)(self.phi.copy(), self.tau.copy())

    def n_var(self) -> int:
        return max(self.phi.n_var(), self.tau.n_var())

    def substitute(self, l: list[Statement]) -> Self:
        return type(self)(self.phi.substitute(l), self.tau.substitute(l))

    def depth(self) -> int:
        return 1 + max(self.phi.depth(), self.tau.depth())
    
    def get_skeleton(self, n_depth: int, context: list[Statement]) -> Statement:
        early = super().get_skeleton(n_depth, context)

        if early is not None:
            return early

        new_phi = self.phi.get_skeleton(n_depth - 1, context)
        new_tau = self.tau.get_skeleton(n_depth - 1, context)

        return type(self)(new_phi, new_tau)

class And(BinaryOp):
    def __str__(self) -> str:
        return f'({self.phi} and {self.tau})'

    def eval(self, v: list[bool]) -> bool:
        return self.phi.eval(v) and self.tau.eval(v)

    def to_sympy(self) -> slb.Boolean:
        return slb.And(self.phi.to_sympy(), self.tau.to_sympy())

    def to_std(self) -> "And":
        return And(self.phi.to_std(), self.tau.to_std())
    
    def to_cf(self) -> "Conditional":
        return Conditional(Conditional(self.phi.to_cf(), Conditional(self.tau.to_cf(), Contradiction())), Contradiction())

class Or(BinaryOp):
    def __str__(self) -> str:
        return f'({self.phi} or {self.tau})'

    def eval(self, v: list[bool]) -> bool:
        return self.phi.eval(v) or self.tau.eval(v)

    def to_sympy(self) -> slb.Boolean:
        return slb.Or(self.phi.to_sympy(), self.tau.to_sympy())

    def to_std(self) -> "Or":
        return Or(self.phi.to_std(), self.tau.to_std())

    def to_cf(self) -> "Conditional":
        return Conditional(Conditional(self.phi.to_cf(), Contradiction()), self.tau.to_cf())

class Conditional(BinaryOp):
    def __str__(self) -> str:
        return f'({self.phi} -> {self.tau})'

    def eval(self, v: list[bool]) -> bool:
        return not self.phi.eval(v) or self.tau.eval(v)

    def to_std(self) -> Or:
        return Or(Not(self.phi.to_std()), self.tau.to_std())

    def to_cf(self) -> "Conditional":
        return Conditional(self.phi.to_cf(), self.tau.to_cf())

class Biconditional(BinaryOp):
    def __str__(self) -> str:
        return f'({self.phi} <-> {self.tau})'

    def eval(self, v: list[bool]) -> bool:
        return self.phi.eval(v) == self.tau.eval(v)

    def to_std(self) -> And:
        new_phi = self.phi.to_std()
        new_tau = self.tau.to_std()

        left = Or(Not(new_phi), new_tau)
        right = Or(Not(new_tau), new_phi)

        return And(left, right)

class Nand(BinaryOp):
    def __str__(self) -> str:
        return f'({self.phi} nand {self.tau})'

    def eval(self, v: list[bool]) -> bool:
        return not(self.phi.eval(v) and self.tau.eval(v))

    def to_std(self) -> "Not":
        return Not(And(self.phi.to_std(), self.tau.to_std()))

class Xor(BinaryOp):
    def __str__(self) -> str:
        return f'({self.phi} xor {self.tau})'

    def eval(self, v: list[bool]) -> bool:
        return self.phi.eval(v) ^ self.tau.eval(v)

    def to_std(self) -> And:
        new_phi = self.phi.to_std()
        new_tau = self.tau.to_std()

        return And(Or(new_phi, new_tau), Not(And(new_phi, new_tau)))

def two_deep_copy_dict(d: dict[Any, dict[Any, Any]]) -> dict[Any, dict[Any, Any]]:
    result = {}

    for key, value in d.items():
        result[key] = value.copy()

    return result

class LUTBinaryOp(BinaryOp):
    def __init__(self, phi: Statement, tau: Statement,
                 table: dict[bool, dict[bool, bool]], id: int) -> None:
        BinaryOp.__init__(self, phi, tau)

        self.table = table
        self.id = id

    def __str__(self) -> str:
        return f'{self.phi} blut{self.id} {self.tau}'
    
    def copy(self) -> "LUTBinaryOp":
        return LUTBinaryOp(self.phi.copy(), self.tau.copy(), two_deep_copy_dict(self.table), self.id)

    def eval(self, v: list[bool]) -> bool:
        return self.table[self.phi.eval(v)][self.tau.eval(v)]

    def substitute(self, l: list[Statement]) -> Statement:
        return LUTBinaryOp(self.phi.substitute(l), self.tau.substitute(l),
                           two_deep_copy_dict(self.table), self.id)

    def get_skeleton(self, n_depth: int, context: list[Statement]) -> Statement:
        early = Statement.get_skeleton(self, n_depth, context)
    
        if early is not None:
            return early
    
        new_phi = self.phi.get_skeleton(n_depth - 1, context)
        new_tau = self.tau.get_skeleton(n_depth - 1, context)
    
        return LUTBinaryOp(new_phi, new_tau, two_deep_copy_dict(self.table), self.id)

    def to_std(self) -> "Statement":
        new_phi = self.phi.to_std()
        new_tau = self.tau.to_std()

        result = Contradiction()

        if self.table[False][False]:
            result = Or(result, And(Not(new_phi), Not(new_tau)))

        if self.table[False][True]:
            result = Or(result, And(Not(new_phi), new_tau))

        if self.table[True][False]:
            result = Or(result, And(new_phi, Not(new_tau)))

        if self.table[True][True]:
            result = Or(result, And(new_phi, new_tau))

        return result

def rand_binary_lut() -> dict[bool, dict[bool, bool]]:
    column = [random.choice([False, True]) for _ in range(4)]

    result = {False: {False: column[0], True: column[1]}, True: {False: column[2], True: column[3]}}

    return result

def rand_binary_ops(n: int) -> list[Callable[[Statement, Statement], LUTBinaryOp]]:
    result = []

    for i in range(n):
        rand_lut = rand_binary_lut()

        def rand_binary_op(phi: Statement, tau: Statement, *, rand_lut = rand_lut, i = i) -> Statement:
            return LUTBinaryOp(phi, tau, rand_lut, i)

        result.append(rand_binary_op)

    return result

class UnaryOp(Statement):
    def __init__(self, phi: Statement) -> None:
        self.phi = phi

    def copy(self) -> Self:
        return type(self)(self.phi.copy())

    def n_var(self) -> int:
        return self.phi.n_var()

    def substitute(self, l: list[Statement]) -> Self:
        return type(self)(self.phi.substitute(l))

    def depth(self) -> int:
        return 1 + self.phi.depth()

    def get_skeleton(self, n_depth: int, context: list[Statement]) -> Statement:
        early = super().get_skeleton(n_depth, context)

        if early is not None:
            return early

        new_phi = self.phi.get_skeleton(n_depth - 1, context)

        return type(self)(new_phi)

class Not(UnaryOp):
    def __str__(self) -> str:
        return f'(not {self.phi})'

    def eval(self, v: list[bool]) -> bool:
        return not self.phi.eval(v)

    def to_sympy(self) -> slb.Boolean:
        return slb.Not(self.phi.to_sympy())

    def to_std(self) -> "Not":
        return Not(self.phi.to_std())

    def to_cf(self) -> Conditional:
        return Conditional(self.phi.to_cf(), Contradiction())

class Constant(Statement):
    def __init__(self) -> None:
        pass

    def copy(self) -> Self:
        return type(self)()

    def n_var(self) -> int:
        return 0
    
    def substitute(self, l: list[Statement]) -> Self:
        return self.copy()

    def depth(self) -> int:
        return 1

    def get_skeleton(self, n_depth: int, context: list[Statement]) -> Statement:
        return self.copy()

    def to_std(self) -> Self:
        return type(self)()

    def to_cf(self) -> Self:
        return type(self)()

class Tautology(Constant):
    def __str__(self) -> str:
        return 'T'

    def eval(self, v: list[bool]) -> bool:
        return True

    def to_sympy(self) -> slb.Boolean:
        return slb.true

class Contradiction(Constant):
    def __str__(self) -> str:
        return 'F'

    def eval(self, v: list[bool]) -> bool:
        return False

    def to_sympy(self) -> slb.Boolean:
        return slb.false

def all_expr(n_vars: int, n_depth: int,
             constants: list[Constant],
             unary_ops: list[UnaryOp],
             binary_ops: list[BinaryOp]) -> list[list[Statement]]:
    if n_depth == 1:
        result = [[]]

        for constant in constants:
            result[0].append(constant())

        for i in range(n_vars):
            result[0].append(Var(i))

        return result

    result = all_expr(n_vars, n_depth - 1, constants, unary_ops, binary_ops)

    new_level = []

    for s1 in result[-1]:
        for unary_op in unary_ops:
            new_level.append(unary_op(s1))

        for s2 in result[-1]:
            for binary_op in binary_ops:
                new_level.append(binary_op(s1, s2))

    result.append(new_level)

    return result

def all_expr_at_depth(n_vars: int, n_depth: int,
                      constants: list[Constant],
                      unary_ops: list[UnaryOp],
                      binary_ops: list[BinaryOp]):
    if n_depth == 1:
        for constant in constants:
            yield constant()

        for i in range(n_vars):
            yield Var(i)

    else:
        prev_s = tuple(all_expr_at_depth(n_vars, n_depth - 1, constants, unary_ops, binary_ops))

        for s1 in prev_s:
            for unary_op in unary_ops:
                yield unary_op(s1)

            for s2 in prev_s:
                for binary_op in binary_ops:
                    yield binary_op(s1, s2)

def empty_formula_map(n_vars: int) -> list[list[Statement]]:
    result = []

    for _ in range(2 ** (2 ** n_vars)):
        result.append([])

    return result

def all_equiv_classes(n_depth: int,
                      constants: list[Constant],
                      unary_ops: list[UnaryOp],
                      binary_ops: list[BinaryOp]) -> list[list[Statement]]:
    max_vars = 2 ** (n_depth - 1)

    result = empty_formula_map(max_vars)

    for l in all_expr(max_vars, n_depth, constants, unary_ops, binary_ops):
        for s in l:
            result[s.table_id(max_vars)].append(s)

    return result

def rand_statement(n_vars: int,
                   n_depth: int,
                   constants: list[Constant],
                   unary_ops: list[UnaryOp],
                   binary_ops: list[BinaryOp]) -> Statement:
    if n_depth == 1:
        do_var = random.choice([False, True])

        if do_var:
            return Var(random.randrange(0, n_vars))

        return random.choice(constants)()

    do_binary = random.choice([False, True])

    phi = rand_statement(n_vars, n_depth - 1, constants, unary_ops, binary_ops)

    if do_binary:
        tau = rand_statement(n_vars, n_depth - 1, constants, unary_ops, binary_ops)

        binary_op = random.choice(binary_ops)

        return binary_op(phi, tau)

    unary_op = random.choice(unary_ops)

    return unary_op(phi)

STD_CONST = [Tautology, Contradiction]
STD_UNARY = [Not]
STD_BINARY = [And, Or]

STD_EQ_CLASSES = all_equiv_classes(3, STD_CONST, STD_UNARY, STD_BINARY)

print('Finished loading equivalence classes')
print()

class MultiStatement:
    def __init__(self, statements: list[Statement]) -> None:
        self.statements = statements
    
    def __str__(self) -> str:
        result = []

        for i, s in enumerate(self.statements):
            e = f'{i}) {s}\n'
            result.append(e)

        return '\n'.join(result)

    def __repr__(self) -> str:
        return str(self)

    def n_var(self) -> int:
        result = []

        for s in self.statements:
            result.append(s.n_var())

        return max(result)
    
    def eval(self, v: list[bool]) -> list[bool]:
        result = []

        for s in self.statements:
            result.append(s.eval(v))

        return result

def fold(f: Callable[[Any, Any], Any], l: list[Any]) -> Any:
    result = l[0]

    for e in l[1:]:
        result = f(result, e)

    return result

def sympy_to_statement(s: slb.Boolean) -> Statement:
    if isinstance(s, Symbol):
        n = int(s.name[1:])

        return Var(n)

    elif s == slb.true:
        return Tautology()

    elif s == slb.false:
        return Contradiction()

    elif isinstance(s, slb.And):
        inputs = []

        for input in s.args:
            inputs.append(sympy_to_statement(input))

        return fold(And, inputs)

    elif isinstance(s, slb.Or):
        inputs = []
        
        for input in s.args:
            inputs.append(sympy_to_statement(input))

        return fold(Or, inputs)

    elif isinstance(s, slb.Not):
        return Not(sympy_to_statement(s.args[0]))

def str_to_statement(s: str) -> Statement:
    original_s = s

    if len(s) == 0:
        raise SyntaxError(f'The statement or substatement "{original_s}" cannot be empty')

    if s[0] == 'x':
        n = s[1:]

        if not n.isnumeric():
            raise SyntaxError(f'The variable "{original_s}" must have a numeric index next to it')

        n = int(n)

        return Var(n)

    if s[0] == 'T':
        if len(s) != 1:
            raise SyntaxError(f'The statement or substatement "{original_s}" that isn\'t tautology cannot start with T')

        return Tautology()

    if s[0] == 'F':
        if len(s) != 1:
            raise SyntaxError(f'The statement or substatement "{original_s}" that isn\'t contradiction cannot start with F')

        return Contradiction()

    if s[0] != '(':
        raise SyntaxError(f'The statement or substatement "{original_s}" that isn\'t a variable or constant must start with "("')

    if s[-1] != ')':
        raise SyntaxError(f'The statement or substatement "{original_s}" that isn\'t a variable or constant must end with ")"')

    s = s[1:-1]

    if len(s) < 5:
        raise SyntaxError(f'The statement or substatement "{original_s}" that isn\'t a variable or constant is too short')

    if s[:3] == 'not':
        return Not(str_to_statement(s[4:]))

    i = None

    n_left_right = 0

    for j, e in enumerate(s):
        if e == '(':
            n_left_right += 1

        elif e == ')':
            n_left_right -= 1

        if n_left_right < 0:
            raise SyntaxError(f'The statement or substatement "{original_s}" cannot have an initial segment with more ")" than "("')

        if n_left_right == 0 and e == ' ':
            i = j
            break

    if i is None:
        raise SyntaxError(f'The statement or substatement "{original_s}" must have a balanced number of "(" and ")" and " " somewhere')

    if len(s) < i + 5:
        raise SyntaxError(f'The statement or substatement "{original_s}" that isn\'t a variable or constant is too short')

    s1 = s[: i]

    if s[i + 1: i + 3] == 'or':
        s2 = s[i + 4:]

        return Or(str_to_statement(s1), str_to_statement(s2))

    elif s[i + 1: i + 4] == 'and':
        s2 = s[i + 5:]

        return And(str_to_statement(s1), str_to_statement(s2))

    raise SyntaxError(f'The statement or substatement "{original_s}" can only use binary connectives "and" or "or"')