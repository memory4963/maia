import os
import re
import requests
import multiprocessing
import chess
import argparse
import chess.pgn
import chess.engine
import pandas as pd
from tqdm import tqdm


def download_pgn(game_id):
    url = f"https://lichess.org/game/export/{game_id}.pgn"
    try:
        response = requests.get(url)
        response.raise_for_status()
        pgn_data = response.text
        
        return pgn_data
    except requests.exceptions.RequestException as e:
        return None


def puzzle_pgn(row):
    # 从FEN创建棋局
    board = chess.Board(row['FEN'])

    # 创建一个新的PGN游戏
    game = chess.pgn.Game()

    # 设置游戏棋盘为FEN位置
    game.setup(board)

    # 从这个位置开始走棋，手动添加几步作为示例
    node = game
    moves = row['Moves'].split(' ')
    for move in moves:
        uci_move = board.push_san(move)  # 将棋步推入棋盘
        node = node.add_main_variation(uci_move)
    exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
    return game.accept(exporter)


def gene_new_pgn(dpgn, ppgn):
    # 找到ppgn第一个步骤
    split_ppgn = ppgn.split('\n')
    ppgn_moves = split_ppgn[-1]
    # 找到当前是哪方
    for split in split_ppgn:
        if split.startswith('[FEN'):
            white = split.split(' ')[2] == 'w'
            break
    if white:
        result = ' 1-0'
    else:
        result = ' 0-1'
    first_move_str = ppgn_moves.split(' ')[0]
    # first_move = int(first_move_str.split('.'))
    pgn = dpgn.split(first_move_str)[0] + ppgn_moves
    return pgn.rsplit(' ', 1)[0] + result


def proc_row(row):
    game_id = row['GameUrl'].split('/')[3].split('#')[0]
    if os.path.exists(f'data/training_data/{game_id}.pgn'):
        return
    # 下载对应的对局
    dpgn = download_pgn(game_id)
    if dpgn is None:
        print(game_id, 'failed.')
        return
    ppgn = puzzle_pgn(row)

    # 修改对应的下法，并修改获胜者
    pgn = gene_new_pgn(dpgn, ppgn)

    # 保存pgn文件
    with open(f'data/training_data/{game_id}.pgn', 'w') as f:
        f.write(pgn)


def main(args):
    os.makedirs('data/training_data', exist_ok=True)
    # 读取CSV文件
    # PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl,OpeningTags
    df = pd.read_csv(args.csv)

    # 筛选需要的对局
    search_strings = ['attraction', 'capturingDefender', 'discoveredAttack', 'exposedKing', 'fork', 'hangingPiece', 'kingsideAttack', 'sacrifice', 'skewer', 'trappedPiece', 'deflection', 'clearance']
    regex_pattern = '|'.join(search_strings)
    selected_rows = df[df['Themes'].str.contains(regex_pattern, case=False, na=False)]

    pool = multiprocessing.Pool(processes=5)
    pbar = tqdm(total=len(selected_rows))
    update = lambda *_: pbar.update()
    for i, (_, row) in enumerate(selected_rows.iterrows()):
        pool.apply_async(proc_row, (row,), callback=update)
    pool.close()
    pool.join()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', default='data/lichess_db_puzzle.csv')
    # parser.add_argument('--csv', default='data/test.csv')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(args)
