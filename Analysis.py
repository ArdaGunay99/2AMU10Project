# Dependencies
import subprocess
import pandas as pd

#%% Create the dataframe
result_dict = {"Player 1": [], "Player 2": [], "Board": [], "Time": [], "Winner":[]}

rep = 5 #number of repetitions for each player 1/player 2 combination

players = [("team5_A2","greedy_player"), ("greedy_player","team5_A2"), ("team5_A2","team5_A1"), ("team5_A1","team5_A2")]
boards = ["empty-3x3","random-3x3","hard-3x3","empty-4x4","random-4x4"]
time = rep*['0.1'] + rep*['0.5'] + rep*['1.0'] + rep*['5.0']

i = 1 #keep track of iterations and make checkpoints in case smth goes wrong, so nothing is lost
for p in players:
    print(f"Testing {p}")
    for b in boards:
        print(f'\t Testing {b}')
        for t in time:
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
            
            if i%50==0:
                results = pd.DataFrame(data = result_dict)
                results.to_csv(f'checkpoint{i}.csv',index=False)
                
            i += 1

results = pd.DataFrame(data = result_dict)
results.to_csv("final-results.csv",index=False)

#%% Create the plots


#to be added