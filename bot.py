from typing import Any
import os
import math
import random
import io
import discord
from discord.ext import commands
import EMF.boolean_logic as bl
import EMF.applications as app
import EMF.equivmargolusfuscation as emf
import SPN.instances as spn_i
import hamiltonian_paths.maker as hp_maker
import hamiltonian_paths.display as hp_display
import minizinc_run.run as mz_run
import patterns.game as pat_game
import patterns.mcts as mcts
import patterns.display as pat_display

intents = discord.Intents.default()

bot = commands.Bot(command_prefix = '!', intents = intents)

sat_challenges = {}
hp_challenges = {}
patterns_games = {}

random.seed(1)

hasher = spn_i.rand_SPHash(256, 8, 100)

random.seed()

@bot.event
async def on_ready():
    await bot.tree.sync()

    print('Connected')

@bot.tree.command(name = 'help', description = 'Learn about this bot\'s commands.')
async def help(interaction: discord.Interaction):
    await interaction.response.send_message('Coming soon!')

@bot.tree.command(name = 'big_bruo', description = 'Big bruo.')
async def big_bruo(interaction: discord.Interaction):
    await interaction.response.send_message('big bruo')

@bot.tree.command(name = 'py_random_number', description = 'Get a pseudorandom integer from "min_incl" inclusive to "max_excl" exclusive.')
async def py_random_number(interaction: discord.Interaction, min_incl: int, max_excl: int):
    rand_n = random.randrange(min_incl, max_excl)

    await interaction.response.send_message(str(rand_n))

def to_str_file(s: Any, filename: str) -> discord.File:
    s = str(s)

    return discord.File(io.BytesIO(s.encode()), filename = filename)

@bot.tree.command(name = 'obfuscate', description = 'Obfuscate the boolean formula "formula" using "n_iterations" iterations of equivmargolusfuscate!')
async def obfuscate(interaction: discord.Interaction, formula: str, n_iterations: int):
    await interaction.response.defer()

    s = bl.str_to_statement(formula)

    s = emf.equivmargolusfuscate(s, n_iterations)

    await interaction.followup.send(file = to_str_file(s, filename = 'obfuscated.txt'))

@bot.tree.command(name = 'random_b_formula', description = 'Generate a random boolean formula.')
async def random_b_formula(interaction: discord.Interaction, n_vars: int, n_depth: int):
    await interaction.response.defer()

    s = bl.rand_statement(n_vars, n_depth, bl.STD_CONST, bl.STD_UNARY, bl.STD_BINARY)

    await interaction.followup.send(file = to_str_file(s, filename = 'random-boolean-formula.txt'))

def parse_assignment(s: str) -> list[bool]:
    original_s = s

    s = s.split(' ')

    result = []

    for c in s:
        if c == 'T':
            result.append(True)

        elif c == 'F':
            result.append(False)

        else:
            raise SyntaxError(f'The assignment {original_s} should be a list of "T" and "F" separated by spaces')

    return result

@bot.tree.command(name = 'evaluate', description = 'Evaluate the boolean formula "formula" with assignment "assignment".')
async def evaluate(interaction: discord.Interaction, formula: str, assignment: str):
    await interaction.response.defer()

    s = bl.str_to_statement(formula)

    s_eval = s.eval(parse_assignment(assignment))

    answer = 'F'

    if s_eval:
        answer = 'T'

    await interaction.followup.send(answer)

@bot.tree.command(name = 'make_sat_challenge', description = 'Give yourself a new SAT challenge!')
async def make_sat_challenge(interaction: discord.Interaction, n_vars: int, up_to_n_sol: int):
    await interaction.response.defer()

    s = bl.Contradiction()

    for i in range(up_to_n_sol):
        sat = [random.choice([False, True]) for _ in range(n_vars)]

        s = bl.Or(s, app.obfuscated_sat_formula(sat, 100, i * n_vars))

    sat_challenges[interaction.user.id] = s

    await interaction.followup.send(f'Your SAT formula is in the file below. Use the command "answer_sat_challenge" when you found the assignment!',
                                    file = to_str_file(s, filename = 'sat-challenge-formula.txt'))

@bot.tree.command(name = 'answer_sat_challenge', description = 'Answer your SAT challenge! The command "make_sat_challenge" must be done first.')
async def answer_sat_challenge(interaction: discord.Interaction, assignment: str):
    await interaction.response.defer()

    if interaction.user.id not in sat_challenges:
        await interaction.followup.send(f'You do not have a SAT challenge. Use the command "make_sat_challenge" to create one.')

        return

    s = sat_challenges[interaction.user.id]

    s_eval = s.eval(parse_assignment(assignment))

    if s_eval:
        await interaction.followup.send(f'Congrats, that was one of the satisfying assignments! :tada: You have completed your SAT challenge.')
        sat_challenges.pop(interaction.user.id)

        return

    await interaction.followup.send(f'That was not a satisfying assignment. :x: To view your SAT challenge again, use the "view_sat_challenge" command.')

@bot.tree.command(name = 'view_sat_challenge', description = 'View your SAT challenge if you have any.')
async def view_sat_challenge(interaction: discord.Interaction):
    await interaction.response.defer()

    if interaction.user.id not in sat_challenges:
        await interaction.followup.send(f'You do not have a SAT challenge. Use the command "make_sat_challenge" to create one.')
    
        return

    s = sat_challenges[interaction.user.id]

    await interaction.followup.send(f'Your SAT formula is in the file below. Use the command "answer_sat_challenge" when you\'ve found the assignment!',
                                    file = to_str_file(s, filename = 'sat-challenge-formula.txt'))

@bot.tree.command(name = 'hash', description = 'Hash your text using a hash function derived from a SPN cipher.')
async def hashing(interaction: discord.Interaction, text: str):
    await interaction.response.defer()

    bits = spn_i.str_to_bool_l(text)

    result = spn_i.bool_l_to_hex(hasher.hash(bits))

    await interaction.followup.send(result)

@bot.tree.command(name = 'numberfy', description = 'Convert your text to a number.')
async def numberfy(interaction: discord.Interaction, text: str):
    await interaction.response.defer()

    await interaction.followup.send(str(spn_i.str_to_int(text)))

@bot.tree.command(name = 'make_hp_challenge', description = 'Give yourself a new Hamiltonian path challenge!')
async def make_hp_challenge(interaction: discord.Interaction, n_nodes: int, p_extra: float):
    await interaction.response.defer()

    path, graph = hp_maker.rand_hp_graph(n_nodes, p_extra)

    file_name = hp_display.graph_image(graph, 'hamiltonian_paths/images/')

    hp_challenges[interaction.user.id] = (path, graph, file_name)

    await interaction.followup.send(f'Your challenge graph is in the file below. The start node is {path[0]} and the end node is {path[-1]}. Use the command "answer_hp_challenge" when you\'ve found the Hamiltonian path!',
                                    file = discord.File(file_name))

@bot.tree.command(name = 'clarify_hp_graph', description = 'Ask whether there is an edge from e1 to e2. This can be used when the graph is ambiguous.')
async def clarify_hp_graph(interaction: discord.Interaction, e1: int, e2: int):
    await interaction.response.defer()

    if interaction.user.id not in hp_challenges:
        await interaction.followup.send(f'You do not have a HP challenge. Use the command "make_hp_challenge" to create one.')
    
        return

    _, graph, _ = hp_challenges[interaction.user.id]

    s = f'No. There is not an edge from {e1} to {e2}'

    if e2 in graph[e1]:
        s = f'Yes. There is an edge from {e1} to {e2}'

    await interaction.followup.send(s)

@bot.tree.command(name = 'answer_hp_challenge', description = 'Answer your HP challenge! The command "make_hp_challenge" must be done first.')
async def answer_hp_challenge(interaction: discord.Interaction, path: str):
    await interaction.response.defer()

    if interaction.user.id not in hp_challenges:
        await interaction.followup.send(f'You do not have a HP challenge. Use the command "make_hp_challenge" to create one.')

        return

    path = path.split(' ')

    path = [int(s) for s in path]

    answer_path, graph, _ = hp_challenges[interaction.user.id]

    if hp_maker.is_hamiltonian_path(graph, answer_path[0], answer_path[-1], path):
        file_name = hp_display.graph_path_image(graph, answer_path, 'green', 'lightblue', 'hamiltonian_paths/images/')

        await interaction.followup.send(f'Congrats, that was one of the Hamiltonian paths! :tada: Attached below is the solution which the graph was generated from. That solution could be different from your solution. You have completed your HP challenge.',
                                        file = discord.File(file_name))

        hp_challenges.pop(interaction.user.id)

        return

    await interaction.followup.send(f'That was not a Hamiltonian path. :x: To view your HP challenge again, use the "view_hp_challenge" command.')

@bot.tree.command(name = 'view_hp_challenge', description = 'View your HP challenge if you have any.')
async def view_hp_challenge(interaction: discord.Interaction):
    await interaction.response.defer()

    if interaction.user.id not in hp_challenges:
        await interaction.followup.send(f'You do not have a HP challenge. Use the command "make_hp_challenge" to create one.')
    
        return

    path, _, file_name = hp_challenges[interaction.user.id]

    await interaction.followup.send(f'Your challenge graph is in the file below. The start node is {path[0]} and the end node is {path[-1]}. Use the command "answer_hp_challenge" when you\'ve found the Hamiltonian path!',
                                    file = discord.File(file_name))

@bot.tree.command(name = 'run_minizinc', description = 'run_minizinc')
@discord.app_commands.checks.has_role(1540612166984400947)
async def run_minizinc(interaction: discord.Interaction, file: discord.Attachment, solver: str):
    await interaction.response.defer()

    data = await file.read()

    file_name = f'minizinc_run/files/{random.randrange(0, 10 ** 5)}.mzn'

    with open(file_name, 'wb') as file:
        file.write(data)

    sol = await mz_run.solve(file_name, solver)

    await interaction.followup.send('Here are the results.',
                                    file = to_str_file(sol, 'minizinc_solutions.txt'))

def str_to_graph(s: str) -> list[set[int]]:
    result = []

    for line in s.splitlines():
        row = set()

        neighbors = line.split(',')

        for neighbor in neighbors:
            row.add(int(neighbor))

        result.append(row)

    return result

@bot.tree.command(name = 'draw_graph', description = 'Draw a graph!')
async def make_hp_challenge(interaction: discord.Interaction, file: discord.Attachment):
    await interaction.response.defer()

    data = await file.read()

    text = data.decode('utf-8')

    g = str_to_graph(text)

    file_name = hp_display.graph_image(g, 'hamiltonian_paths/images/')

    await interaction.followup.send(f'Here\'s your graph.',
                                    file = discord.File(file_name))

@bot.tree.command(name = 'make_patterns_game', description = 'Make a game session for the abstract strategy game "PATTERNS".')
async def make_patterns_game(interaction: discord.Interaction, width: int, height: int, human_first: bool, bot_difficulty: int = 100):
    await interaction.response.defer()

    game = pat_game.Patterns(width, height, pat_game.TILES_1_1, pat_game.TILES_1_2)

    patterns_games[interaction.user.id] = (game, bot_difficulty, human_first)

    if not human_first:
        game.do_move(mcts.find_move(game, True, math.sqrt(2), mcts.rand_simulation, bot_difficulty))

    file_name = f'patterns/board_images/{random.randrange(0, 10 ** 4)}.png'

    pat_display.draw_game(game, None, 100, file_name)

    await interaction.followup.send('Made the game!', file = discord.File(file_name))

@bot.tree.command(name = 'patterns_move', description = 'Place your piece onto the point with x-coordinate "x" and y-coordinate "y".')
async def patterns_move(interaction: discord.Interaction, x: int, y: int):
    await interaction.response.defer()

    if interaction.user.id not in patterns_games:
        await interaction.followup.send(f'You do not have a PATTERNS game. Use the command "make_patterns_game" to create one.')

        return

    game, difficulty, human_first = patterns_games[interaction.user.id]

    if game.ended():
        await interaction.followup.send(f'Our game already ended. Use the command "make_patterns_game" to create a new one.')

        return

    move = (y - 1, x - 1)

    if move not in game.all_moves():
        await interaction.followup.send('That\'s an invalid move. Note that the x-coordinate goes from left to right and starts at 1 and the y-coordinate goes from top to bottom and starts at 1.')

        return

    game.do_move(move)

    file_name = f'patterns/board_images/{random.randrange(0, 10 ** 4)}.png'

    pat_display.draw_game(game, None, 100, file_name)

    if not game.ended():
        game.do_move(mcts.find_move(game, not human_first, math.sqrt(2), mcts.rand_simulation, difficulty))

        file_name = f'patterns/board_images/{random.randrange(0, 10 ** 4)}.png'

        pat_display.draw_game(game, None, 100, file_name)

        await interaction.followup.send('Your turn now!', file = discord.File(file_name))

        return

    if game.winner() == human_first:
        await interaction.followup.send('Congrats, you won. :tada:', file = discord.File(file_name))

        return

    await interaction.followup.send(':x: I won this time.', file = discord.File(file_name))

@bot.tree.command(name = 'patterns_score', description = 'See the score ')
async def patterns_score(interaction: discord.Interaction):
    await interaction.response.defer()

    if interaction.user.id not in patterns_games:
        await interaction.followup.send(f'You do not have a PATTERNS game. Use the command "make_patterns_game" to create one.')

        return

    game, _, _ = patterns_games[interaction.user.id]

    file_name1 = f'patterns/player_1_images/{random.randrange(0, 10 ** 4)}.png'

    pat_display.draw_game(game, True, 100, file_name1)

    file_name2 = f'patterns/player_2_images/{random.randrange(0, 10 ** 4)}.png'
    
    pat_display.draw_game(game, False, 100, file_name2)

    s1, s2 = game.score()

    await interaction.followup.send(f'Points for blue: {s1}. Points for pink: {s2}.', files = [discord.File(file_name1), discord.File(file_name2)])

TOKEN = os.getenv('DISCORD_TOKEN')

bot.run(TOKEN)