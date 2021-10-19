import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas
import os
import scipy
from scipy import signal
import sys
import argparse
import json

from all_envs import all_environments

def get_algo_name(experiment_name):
    if 'shared_ppo' in experiment_name:
        return 'shared_ppo'
    else:
        return "shared_rainbow"

def get_env_name(experiment_name):
    for env_name in all_environments:
        if env_name in experiment_name:
            return env_name
    raise AssertionError(f"{experiment_name} does not contain any environment name: {list(sorted(all_environments))}")
    # # env_name = env_name[:env_name.rfind("_")]
    # if 'boxing' in env_name:
    #     game_env = 'Boxing'
    # elif 'combat_plane' in env_name:
    #     game_env = 'Combat Plane'
    # elif 'combat_tank' in env_name:
    #     game_env = 'Combat Tank'
    # elif 'double_dunk' in env_name:
    #     game_env = 'Double Dunk'
    # elif 'entombed_competitive' in env_name:
    #     game_env = 'Entombed Competitive'
    # elif 'entombed_cooperative' in env_name:
    #     game_env = 'Entombed Cooperative'
    # elif 'flag_capture' in env_name:
    #     game_env = 'Flag Capture'
    # elif 'ice_hockey' in env_name:
    #     game_env = 'Ice Hockey'
    # elif 'joust' in env_name:
    #     game_env = 'Joust'
    # elif 'mario_bros' in env_name:
    #     game_env = 'Mario Bros'
    # elif 'maze_craze' in env_name:
    #     game_env = 'Maze Craze'
    # elif 'othello' in env_name:
    #     game_env = 'Othello'
    # elif 'basketball_pong' in env_name:
    #     game_env = 'Basketball Pong'
    # elif 'pong' in env_name:
    #     game_env = 'Pong'
    # elif 'foozpong' in env_name:
    #     game_env = 'Foozpong'
    # elif 'quadrapong' in env_name:
    #     game_env = 'Quadrapong'
    # elif 'volleyball_pong' in env_name:
    #     game_env = 'Volleyball Pong'
    # elif 'space_invaders' in env_name:
    #     game_env = 'Space Invaders'
    # elif 'space_war' in env_name:
    #     game_env = 'Space War'
    # elif 'surround' in env_name:
    #     game_env = 'Surround'
    # elif 'tennis' in env_name:
    #     game_env = 'Tennis'
    # elif 'video_checkers' in env_name:
    #     game_env = 'Video Checkers'
    # elif 'warlords' in env_name:
    #     game_env = 'Warlords'
    # elif 'wizard_of_wor' in env_name:
    #     game_env = 'Wizard of Wor'
    # else:
    #     raise RuntimeError(f"{env_name} not found")
    # return game_env


def get_exp_label(exp):
    start = exp.find("/")+1
    end = exp.rfind("_")
    return exp[start:end]


def main():

    parser = argparse.ArgumentParser(description="Run an multiagent Atari benchmark.")
    parser.add_argument("csv_name", help="Checkpoint number.")
    parser.add_argument(
        "--no-vs-random", action="store_true", help="Play first_0 vs random for all other players."
    )
    parser.add_argument(
        "--vs-builtin", action="store_true", help="Play first_0 vs random for all other players."
    )
    args = parser.parse_args()

    # assert len(sys.argv) == 3, "must supply name of csv file and vs_random as arguments"

    csv_name = args.csv_name#sys.argv[1]
    vs_random = not args.no_vs_random#bool(sys.argv[2])
    vs_builtin = args.vs_builtin#bool(sys.argv[2])

    matplotlib.use("pgf")
    plt.rcParams.update({
        "pgf.texsystem": "pdflatex",
        "font.family": "serif",
        "font.size": 6,
        "legend.fontsize": 5,
        "ytick.labelsize": 4,
        "text.usetex": True,
        "pgf.rcfonts": False
    });

    csv_data = pandas.read_csv(csv_name)
    # print(csv_data['vs_random'])
    if not vs_builtin:
        csv_data = csv_data[csv_data['vs_random'] == vs_random]
    csv_data['no_seed_experiment'] = [s.rsplit('_', 1)[0] for s in csv_data['experiment']]
    # print(len(csv_data['no_seed_experiment']))
    # print(len(set(csv_data['no_seed_experiment'])))
    # print(len(set(csv_data['checkpoint'])))
    # print(len(set(csv_data['agent'])))
    # print(len(set(csv_data['vs_random'])))
    del csv_data['experiment']
    grouped = csv_data.groupby([
        'no_seed_experiment',
        'checkpoint',
        'agent',
        'vs_random'
    ])
    accumed = grouped.agg({
        'agent1_rew': ['mean', 'min', 'max'],
        'agent2_rew': ['mean', 'min', 'max'],
        'agent3_rew': ['mean', 'min', 'max'],
        'agent4_rew': ['mean', 'min', 'max'],
    })
    # print(accumed)
    accumed.reset_index(inplace=True)
    # print(len(csv_data['agent1_rew']))
    # print(len(accumed['agent1_rew']['mean']))
    # return
    # print(accumed['agent1_rew']['mean'])
    # print(accumed)
    # return
    # random rewards gleaned with ale_rand_test.py
    if vs_builtin:
        random_data = json.load(open("plot_data/builtin_env_rewards.json"))
    else:
        random_data = json.load(open("plot_data/rand_rewards.json"))
    csv_data = accumed#[(accumed['agent'] == "first_0")]
    #print(data)
    all_envs = list(sorted(set(csv_data['no_seed_experiment'])))

    all_env_map = {get_env_name(env): env for env in all_envs}
    all_algo_env_map = {(get_env_name(env), get_algo_name(env)): env for env in all_envs}
    all_algo_names = {get_algo_name(env) for env in all_envs}
    # print(all_algo_env_map)
    all_envs = sorted(all_env_map.keys(), key=str.lower)
    # print(all_algo_names)
    algo_lines = {}
    color_map = {
        'shared_ppo': "blue",
        'shared_rainbow': "orange",
    }
    plot_ind = 0
    num_envs = len(all_envs)
    num_rows = (num_envs+2)//3
    fig, axs = plt.subplots(num_rows, 3, figsize=(2.65*3*1.0, 1.5*7*1.0/8*num_rows))
    for env in all_envs:
        ax = axs[plot_ind // 3][plot_ind % 3]
        #df = pd.read_csv(os.path.join(data_path, env+'.csv'))
        # data = df.to_numpy()
        #filtered = scipy.signal.savgol_filter(data[:, 1], int(len(data[:, 1])/110)+2, 5)
        for algo in all_algo_names:
            df = csv_data[(csv_data['no_seed_experiment'] == all_algo_env_map[(env,algo)])]
            x_axis = df['checkpoint'].to_numpy()
            # print('\n'.join(str(v1) + v2 for v1, v2 in zip(df['checkpoint'],df['no_seed_experiment'])))
            mean_val = df['agent1_rew']['mean'].to_numpy()
            max_val = df['agent1_rew']['max'].to_numpy()
            min_val = df['agent1_rew']['min'].to_numpy()
            line, = ax.plot(x_axis, mean_val, label=env, linewidth=0.6, color=color_map[algo], linestyle='-')
            algo_lines[algo] = line
            # print(mean_val, max_val, min_val)
            ax.fill_between(x_axis, min_val, max_val, alpha=0.3, facecolor=color_map[algo])
        # plt.set_ylabel('between y1 and 0')
        rand_reward = random_data[env]['mean_rewards']['first']
        rand_line, = ax.plot(x_axis, rand_reward*np.ones_like(x_axis), label=env, linewidth=0.6, color='#A0522D', linestyle='-')

        ax.set_xlabel('Steps', labelpad=1)
        ax.set_ylabel('Average Total Reward', labelpad=1)
        ax.set_title(get_exp_label(env))
        ax.ticklabel_format(style='sci', scilimits = [-3, 3])
        #plt.xticks(ticks=[10000,20000,30000,40000,50000],labels=['10k','20k','30k','40k','50k'])
        #plt.xlim(0, 60000)
        #plt.yticks(ticks=[0,150,300,450,600],labels=['0','150','300','450','600'])
        #plt.ylim(-150, 750)
        # plt.tight_layout()
        #plt.legend(loc='lower center', ncol=2, labelspacing=.2, columnspacing=.25, borderpad=.25, bbox_to_anchor=(0.5, -0.6))
        ax.margins(x = 0)

        plot_ind += 1

    plt.tight_layout(pad=1.00)
    oop_name = "Random" if not vs_builtin else "Builtin"
    name_map = {
        'shared_ppo': f"PPO Agent vs {oop_name} Agent",
        'shared_rainbow': f"Rainbow Agent vs {oop_name} Agent",
    }
    name_sublist = [name_map[algo] for algo in all_algo_names]
    lint_sublist = [algo_lines[algo] for algo in all_algo_names]
    legend_y = -0.20 if vs_builtin else -0.05
    plt.figlegend(lint_sublist+[rand_line], name_sublist + [f"Random Agent vs {oop_name} Agent"], fontsize='x-large', loc='lower center', ncol=1, labelspacing=.2, columnspacing=.25, borderpad=.25, bbox_to_anchor=(0.5, legend_y))
    plt.savefig(f"{csv_name}.pgf", bbox_inches='tight', pad_inches=.025)
    plt.savefig(f"{csv_name}.png", bbox_inches='tight', pad_inches=.025, dpi=600)


if __name__ == "__main__":
    main()
