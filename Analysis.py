# Dependencies
import subprocess
import pandas as pd

#%% Create the dataframe
result_dict = {"Player 1": [], "Player 2": [], "Board": [], "Time": [], "Winner":[]}

rep = 5 #number of repetitions for each player 1/player 2 combination


#players = [("team5_A2","team5_MCTS"), ("team5_MCTS","team5_A2")] #Arda
players = [("expert_player","team5_MCTS")("team5_MCTS","expert_player")] #Rozanne
#players = [("team5_A3_Extending_A2","team5_MCTS"), ("team5_MCTS","team5_A3_Extending_A2")] #Mennolt
boards = ["empty-3x3","hard-3x3","random-3x3"]#,"empty-4x4","random-4x4"]
time = rep*['0.1'] + rep*['0.5'] + rep*['1.0'] + rep*['2.0'] + rep*['5.0']

i = 1 #keep track of iterations and make checkpoints in case smth goes wrong, so nothing is lost
for p in players:
    print(f"Testing {p}")
    for b in boards:
        print(f'\t Testing {b}')
        for t in time:
            if i > -1:
                print(f'\t\t Testing {t}')
                result_dict["Player 1"].append(p[0])
                result_dict["Player 2"].append(p[1])
                result_dict["Board"].append(b)
                result_dict["Time"].append(t)

                #get the winner
                outp = subprocess.run(['python','simulate_game.py','--first', p[0], '--second', p[1], '--board',
                                       f'./boards/{b}.txt', '--time', t], stdout = subprocess.PIPE).stdout.decode('cp1252')
                winner = outp[-18]
                result_dict["Winner"].append(winner)

                if i%10==0:
                    results = pd.DataFrame(data = result_dict)
                    results.to_csv(f'checkpoint{i}_22_01_12.csv',index=False)
                
            i += 1

results = pd.DataFrame(data = result_dict)

#name = "final-results_A2_vs_MCTS.csv" #Arda
name = "final-results_Expert_vs_MCTS.csv" #Rozanne
#name = "final-results_A2_Extended_vs_MCTS.csv"

results.to_csv(name,index=False)

#%% Create the plots


#to be added