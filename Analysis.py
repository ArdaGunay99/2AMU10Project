# Dependencies
import subprocess
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#%% Create the dataframe
result_dict = {"Player 1": [], "Player 2": [], "Board": [], "Time": [], "Winner":[]}

rep = 5 #number of repetitions for each player 1/player 2 combination

players = [("team5_A2","greedy_player"),("greedy_player","team5_A2"),("team5_A2","team5_A1"),("team5_A1","team5_A2")]
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
            outp = subprocess.run(['python','./simulate_game.py','--first', p[0], '--second', p[1], '--board',
                                   f'./boards/{b}.txt', '--time', t], stdout = subprocess.PIPE).stdout.decode('cp1252')
            winner = outp[-18]
            result_dict["Winner"].append(winner)
            
            if i%6==0:
                results = pd.DataFrame(data = result_dict)
                results.to_csv(f'checkpoint{i}.csv',index=False)
                
            i += 1

results = pd.DataFrame(data = result_dict)
results.to_csv("final-results.csv",index=False)

#%% Load the data

result_DF = pd.read_csv('final-results.csv')
result_arr = np.array(np.zeros((4,5,4))) #player combi x boards x time per turn, order of indices same as lists above

for i in result_DF.index:
    if (result_DF.loc[i]['Winner'] == 1 and result_DF.loc[i]['Player 1'] == "team5_A2") or (result_DF.loc[i]['Winner'] == 2 and result_DF.loc[i]['Player 2'] == "team5_A2"):
        win = True
    elif result_DF.loc[i]['Winner'] != 1 and result_DF.loc[i]['Winner'] != 2:
        raise Exception(f"win is wrong at {i}")
    else:
        continue
    
    if result_DF.loc[i]['Player 2'] == "greedy_player":
        j = 0
    elif result_DF.loc[i]['Player 1'] == "greedy_player":
        j = 1
    elif result_DF.loc[i]['Player 2'] == "team5_A1":
        j = 2
    elif result_DF.loc[i]['Player 1'] == "team5_A1":
        j = 3
    else:
        raise Exception(f"player is wrong at {i}")
        
    if result_DF.loc[i]['Board'] == "empty-3x3":
        k = 0
    elif result_DF.loc[i]['Board'] == "random-3x3":
        k = 1
    elif result_DF.loc[i]['Board'] == "hard-3x3":
        k = 2
    elif result_DF.loc[i]['Board'] == "empty-4x4":
        k = 3
    elif result_DF.loc[i]['Board'] == "random-4x4":
        k = 4
    else:
        raise Exception(f"board is wrong at {i}")
        
    if result_DF.loc[i]['Time'] == 0.1:
        l = 0
    elif result_DF.loc[i]['Time'] == 0.5:
        l = 1
    elif result_DF.loc[i]['Time'] == 1.0:
        l = 2
    elif result_DF.loc[i]['Time'] == 5.0:
        l = 3
    else:
        raise Exception(f"time is wrong at {i}")
        
    if win:
        result_arr[j,k,l] += 1

#%% Create the plots
# create a plot for opponent vs opponent
x = [1,2]
x_labels = ["greedy_player","team5_A1"]

greedy = sum([result_arr[p,b,t] for p in range(2) for b in range(5) for t in range(1,4)]) / 120 * 100
A1 = sum([result_arr[p,b,t] for p in range(2,4) for b in range(5) for t in range(1,4)]) / 120 * 100

y = [greedy, A1]

plt.figure(1)
plt.bar(x, y, width=0.5, color='grey',edgecolor='black',linewidth=0.65)
plt.xticks(x, labels=x_labels)
plt.xlim(0.5,2.5)
plt.xlabel("Opponent")
plt.yticks([0,10,20,30,40,50,60,70,80,90,100])
plt.ylim(0,110)
plt.ylabel("% of wins")

#%%create plot for boards and opponents
x = [1,2,3,4,5]
x_labels = ['empty-3x3','random-3x3','hard-3x3','empty-4x4','random-4x4']

greedy_empty3x3 = sum([result_arr[p,0,t] for p in range(2) for t in range(1,4)]) / 30 * 100
greedy_random3x3 = sum([result_arr[p,1,t] for p in range(2) for t in range(1,4)]) / 30 * 100
greedy_hard3x3 = sum([result_arr[p,2,t] for p in range(2) for t in range(1,4)]) / 30 * 100
greedy_empty4x4 = sum([result_arr[p,3,t] for p in range(2) for t in range(1,4)]) / 12 * 100
greedy_random4x4 = sum([result_arr[p,4,t] for p in range(2) for t in range(1,4)]) / 18 * 100

A1_empty3x3 = sum([result_arr[p,0,t] for p in range(2,4) for t in range(1,4)]) / 30 * 100
A1_random3x3 = sum([result_arr[p,1,t] for p in range(2,4) for t in range(1,4)]) / 30 * 100
A1_hard3x3 = sum([result_arr[p,2,t] for p in range(2,4) for t in range(1,4)]) / 30 * 100
A1_empty4x4 = sum([result_arr[p,3,t] for p in range(2,4) for t in range(1,4)]) / 12 * 100
A1_random4x4 = sum([result_arr[p,4,t] for p in range(2,4) for t in range(1,4)]) / 18 * 100

y1 = [greedy_empty3x3, greedy_random3x3, greedy_hard3x3, greedy_empty4x4, greedy_random4x4]
y2 = [A1_empty3x3, A1_random3x3, A1_hard3x3, A1_empty4x4, A1_random4x4]

plt.figure(2)
plt.bar(x,y1,width=0.3,align='edge',color='white',edgecolor='black',linewidth=0.65,label='against greedy_player')
plt.bar(x,y2,width=-0.3,align='edge',color='grey',edgecolor='black',linewidth=0.65,label='against team5_A1')
plt.xlabel('boards')
plt.ylabel('% of wins')
plt.xticks(x,labels=x_labels)
plt.yticks([0,10,20,30,40,50,60,70,80,90,100])
plt.ylim(0,110)
plt.legend()

#%%
#create plot for times and opponent
x = [1,2,3,4]
x_labels = ['0.1','0.5','1.0','5.0']

greedy_01 = sum([result_arr[p,b,0] for p in range(2) for b in range(5)]) / 42 * 100
greedy_05 = sum([result_arr[p,b,1] for p in range(2) for b in range(5)]) / 42 * 100
greedy_10 = sum([result_arr[p,b,2] for p in range(2) for b in range(5)]) / 42 * 100
greedy_50 = sum([result_arr[p,b,3] for p in range(2) for b in range(5)]) / 36 * 100

A1_01 = sum([result_arr[p,b,0] for p in range(2,4) for b in range(5)]) / 42 * 100
A1_05 = sum([result_arr[p,b,1] for p in range(2,4) for b in range(5)]) / 42 * 100
A1_10 = sum([result_arr[p,b,2] for p in range(2,4) for b in range(5)]) / 42 * 100
A1_50 = sum([result_arr[p,b,3] for p in range(2,4) for b in range(5)]) / 36 * 100

y1 = [greedy_01, greedy_05, greedy_10, greedy_50]
y2 = [A1_01, A1_05, A1_10, A1_50]

plt.figure(3)
plt.bar(x,y1,width=0.3,align='edge',color='white',edgecolor='black',linewidth=0.65,label='against greedy_player')
plt.bar(x,y2,width=-0.3,align='edge',color='grey',edgecolor='black',linewidth=0.65,label='against team5_A1')
plt.xlabel('seconds per turn')
plt.ylabel('% of wins')
plt.xticks(x,labels=x_labels)
plt.yticks([0,10,20,30,40,50,60,70,80,90,100])
plt.ylim(0,110)
plt.legend()

#%%
#Find where we won on 0.1 time despite being player 1
for i in result_DF.index:
    if result_DF.loc[i]['Time'] == 0.1:
        if result_DF.loc[i]['Winner'] == 1 and result_DF.loc[i]['Player 1'] == "team5_A2":
            print("won: ",result_DF.loc[i])
        #find where we lost on 0.1 time despite being player 2
        elif result_DF.loc[i]['Winner'] == 1 and result_DF.loc[i]['Player 2'] == "team5_A2":
            print("lost: ", result_DF.loc[i])


#%%
#create plot for boards x time
x = [1.5,4.5,7.5,10.5,13.5]
x_labels = ['empty-3x3','random-3x3','hard-3x3','empty-4x4','random-4x4']

empty3x3_01 = sum([result_arr[p,0,0] for p in range(4)]) / 20 * 100
empty3x3_05 = sum([result_arr[p,0,1] for p in range(4)]) / 20 * 100
empty3x3_10 = sum([result_arr[p,0,2] for p in range(4)]) / 20 * 100
empty3x3_50 = sum([result_arr[p,0,3] for p in range(4)]) / 20 * 100

random3x3_01 = sum([result_arr[p,1,0] for p in range(4)]) / 20 * 100
random3x3_05 = sum([result_arr[p,1,1] for p in range(4)]) / 20 * 100
random3x3_10 = sum([result_arr[p,1,2] for p in range(4)]) / 20 * 100
random3x3_50 = sum([result_arr[p,1,3] for p in range(4)]) / 20 * 100

hard3x3_01 = sum([result_arr[p,2,0] for p in range(4)]) / 20 * 100
hard3x3_05 = sum([result_arr[p,2,1] for p in range(4)]) / 20 * 100
hard3x3_10 = sum([result_arr[p,2,2] for p in range(4)]) / 20 * 100
hard3x3_50 = sum([result_arr[p,2,3] for p in range(4)]) / 20 * 100

empty4x4_01 = sum([result_arr[p,3,0] for p in range(4)]) / 12 * 100
empty4x4_05 = sum([result_arr[p,3,1] for p in range(4)]) / 12 * 100
empty4x4_10 = sum([result_arr[p,3,2] for p in range(4)]) / 12 * 100

random4x4_01 = sum([result_arr[p,4,0] for p in range(4)]) / 12 * 100
random4x4_05 = sum([result_arr[p,4,1] for p in range(4)]) / 12 * 100
random4x4_10 = sum([result_arr[p,4,2] for p in range(4)]) / 12 * 100
random4x4_50 = sum([result_arr[p,4,3] for p in range(4)]) / 12 * 100

y1 = [empty3x3_01, random3x3_01, hard3x3_01, empty4x4_01, random4x4_01]
y2 = [empty3x3_05, random3x3_05, hard3x3_05, empty4x4_05, random4x4_05]
y3 = [empty3x3_10, random3x3_10, hard3x3_10, empty4x4_10, random4x4_10]
y4 = [empty3x3_50, random3x3_50, hard3x3_50, 0, random4x4_50]

x1 = [1,4,7,10,13]
x2 = [2,5,8,11,14]

plt.figure(4)
plt.bar(x1,y1,width=-0.5,align='edge',label='0.1 second per turn',color='white',edgecolor='black',linewidth=0.65)
plt.bar(x1,y2,width=0.5,align='edge',label='0.5 second per turn',color='darkgrey',edgecolor='black',linewidth=0.65)
plt.bar(x2,y3,width=-0.5,align='edge',label='1.0 second per turn',color='dimgray',edgecolor='black',linewidth=0.65)
plt.bar(x2,y4,width=0.5,align='edge',label='5.0 seconds per turn',color='black')
plt.xlabel('boards')
plt.ylabel('% of wins')
plt.xticks(x,labels=x_labels)
plt.yticks([0,10,20,30,40,50,60,70,80,90,100])
plt.ylim(0,110)
plt.legend()


#%%
#create plot for first_player x board
x = [1,2,3,4,5]
x_labels = ['empty-3x3','random-3x3','hard-3x3','empty-4x4','random-4x4']

p1_empty3x3 = sum([result_arr[p,0,t] for p in [0,2] for t in range(1,4)]) / 30 * 100
p1_random3x3 = sum([result_arr[p,1,t] for p in [0,2] for t in range(1,4)]) / 30 * 100
p1_hard3x3 = sum([result_arr[p,2,t] for p in [0,2] for t in range(1,4)]) / 30 * 100
p1_empty4x4 = sum([result_arr[p,3,t] for p in [0,2] for t in range(1,4)]) / 12 * 100
p1_random4x4 = sum([result_arr[p,4,t] for p in [0,2] for t in range(1,4)]) / 18 * 100

p2_empty3x3 = sum([result_arr[p,0,t] for p in [1,3] for t in range(1,4)]) / 30 * 100
p2_random3x3 = sum([result_arr[p,1,t] for p in [1,3] for t in range(1,4)]) / 30 * 100
p2_hard3x3 = sum([result_arr[p,2,t] for p in [1,3] for t in range(1,4)]) / 30 * 100
p2_empty4x4 = sum([result_arr[p,3,t] for p in [1,3] for t in range(1,4)]) / 12 * 100
p2_random4x4 = sum([result_arr[p,4,t] for p in [1,3] for t in range(1,4)]) / 18 * 100

y1 = [p1_empty3x3, p1_random3x3, p1_hard3x3, p1_empty4x4, p1_random4x4]
y2 = [p2_empty3x3, p2_random3x3, p2_hard3x3, p2_empty4x4, p2_random4x4]

plt.figure(5)
plt.bar(x,y1,width=0.3,align='edge',color='white',edgecolor='black',linewidth=0.65,label='team5_A2 is player 1')
plt.bar(x,y2,width=-0.3,align='edge',color='grey',edgecolor='black',linewidth=0.65,label='team5_A2 is player 2')
plt.xlabel('boards')
plt.ylabel('% of wins')
plt.xticks(x,labels=x_labels)
plt.yticks([0,10,20,30,40,50,60,70,80,90,100])
plt.ylim(0,110)
plt.legend()

#%%

#create plot for p1 vs p2
x = [1,2]
x_labels = ["Player 1","Player 2"]

p1 = sum([result_arr[p,b,t] for p in [0,2] for b in range(5) for t in range(1,4)]) / 120 * 100
p2 = sum([result_arr[p,b,t] for p in [1,3] for b in range(5) for t in range(1,4)]) / 120 * 100

y = [greedy, A1]

plt.figure(1)
plt.bar(x, y, width=0.5, color='grey',edgecolor='black',linewidth=0.65)
plt.xticks(x, labels=x_labels)
plt.xlim(0.5,2.5)
plt.xlabel("Our agent's player nr")
plt.yticks([0,10,20,30,40,50,60,70,80,90,100])
plt.ylim(0,110)
plt.ylabel("% of wins")