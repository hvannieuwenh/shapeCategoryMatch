from psychopy import core, visual, gui, data, event, hardware
from psychopy.hardware import keyboard
from psychopy.tools.filetools import fromFile, toFile
from collections import deque
import numpy as np
import random
import time
import os

def update_difficulty(current_diff, max_diff, thrs_acc, past_data) :
    N = len(past_data)
    if (N == past_data.maxlen) and (all(map(lambda d: d['difficulty'] == current_diff, past_data))) :
        N_corrects = sum([d['correct'] for d in past_data])
        acc = N_corrects / N

        if (acc >= thrs_acc) and (current_diff < max_diff) : 
            current_diff += 1
        elif (acc < thrs_acc) and (current_diff > 1) :
            current_diff -= 1

    return current_diff


def find_in_object(obj, name, value):
    for (i,x) in enumerate(obj):
        if x[name] == value:
            return i


core.checkPygletDuringWait = False

win = visual.Window(size=(800,600), fullscr=True, color=(-1,-1,-1), allowGUI=True, monitor='testMonitor', units='height')

msg_welcome = visual.TextBox2(
    win, 
    pos=[0, 0], 
    text="Welcome to the Category Learning experiment! Press any key to continue.",
    alignment='center'
)

msg_intro_1 = visual.TextBox2(
    win, 
    pos=[0, 0], 
    text="""
        This task is divided into trials. In each trial you will see a white shape.\n 
        After a short delay you will see two other shapes, one left and one right. \n
        When you see the two shapes you will need to choose which of the two best matches the first shape you saw.\n
        Press any left hand button if the first shape matches the left one and any right hand button if it matches the right one.\n
        After you choose, the screen will show you whether you were correct or not.\n
        You will receive a bonus of $0.05 for each correct answer!\n
        Press any key to continue.
        """,
    alignment='center'
)

msg_intro_2 = visual.TextBox2(
    win, 
    pos=[0, 0], 
    text="""
        The first 10 trials are a practice round that will not count towards your bonus payment.\n
        You will be notified when practice finishes and the test begins.\n
        Press any key to begin the practice round.
        """,
    alignment='center'
)

ITI = visual.TextBox2(
    win, 
    pos=[0, 0], 
    text="Please press any button to continue to the next trial.",
    alignment='center'
)

feedback = visual.TextBox2(
    win, 
    pos=[0, 0], 
    text="",
    letterHeight = 0.05,
    alignment='center'
)

debug_msg = visual.TextBox2(win, pos=[0.0, -0.1], text="", alignment='center')

current_score = 0.0
score = visual.TextBox2(
    win, 
    pos=[0, 0.4], 
    text=f'Bonus : ${np.round(current_score,3)}', 
    letterHeight = 0.05,
    alignment='center'
)

kb = keyboard.Keyboard()

T_experiment = 10 # minutes
T_stim = 1 # seconds
T_choice = 4 # seconds
T_delay = 0.85 # seconds
delay_jitter_range = [0.0, 0.4] # seconds
T_correct_fbdk = 1.5 # seconds
T_incorrect_fdbk = 5 # seconds

correct_bonus = 0.05
thrs_acc = 0.75
IS_DEBUG_MODE = False

correct_fdbk = f'Correct category! + ${correct_bonus}'
correct_fdbk_no_bonus = f'Correct category!'
wrong_fdbk_no_bonus = "Wrong category!"
timeout_fdbk_no_bonus = f'Time out! \nPlease try to respond as quickly as possible.'

shape_set = 2
pack_path = f'stimuli/pack_shapes_{shape_set}/'

N_categories = 2
N_difficulty_levels = 5
N_trials_per_difficulty = 5
N_training_trials = 10
P_difficulty_training = [0.6, 0.4, 0.0, 0.0, 0.0]

stim_train = []
stim_test = [[] for i in range(N_difficulty_levels)]

for i in range(N_difficulty_levels) :
    P = P_difficulty_training[i]
    for j in range(N_categories) :
        stim_path = pack_path + f'cat_{j+1}/diff_{i+1}/'
        files = os.listdir(stim_path)
        files = [os.path.join(stim_path, f) for f in files]

        shapes_train = random.choices(files, k = int(np.floor(P * (N_training_trials/2))))
        shapes_test = [f for f in files if f not in shapes_train]


        #correct_response = 'right' if j == 1 else 'left'
        correct_response = ['1','2','3','4','5'] if j == 1 else ['6','7','8','9','0']
        
        stim_test[i] += [
            {
                'stimulus' : visual.ImageStim(win, s, pos=[0, 0], size=(0.7, 0.7), units='height'), 
                'stimulus_ID' : int(s.split('_')[-1].split('.')[0]),
                'difficulty' : i+1, 
                'category' : j+1,
                'phase' : 'test'
            } 
        for s in shapes_test]

        stim_train += [
            {
                'stimulus' : visual.ImageStim(win, s, pos=[0, 0], size=(0.7, 0.7), units='height'), 
                'stimulus_ID' : int(s.split('_')[-1].split('.')[0]),
                'difficulty' : i+1, 
                'category' : j+1,
                'phase' : 'train'
            } 
        for s in shapes_train]

prototypes = [
    {
        'stimulus' : visual.ImageStim(win, pack_path + f'cat_{i+1}/prototype_{i+1}.png', size=(0.7, 0.7), units='height'), 
        'category' : i+1,
    }
for i in range(N_categories)]

choice_positions = [[-0.5, 0], [0.5, 0]]

trial_handler = data.TrialHandler(
    trialList = stim_train,
    nReps = 1
)

info = {'participant':'', 'session':''}

info['date'] = data.getDateStr()

exp = data.ExperimentHandler(
    name='SCL_mixed',
    extraInfo = info, #the info we created earlier
    dataFileName = 'output', 
)

msg_intro_1.draw()
win.flip()
keys = kb.waitKeys()

msg_intro_2.draw()
win.flip()
keys = kb.waitKeys()

#-------------------
#--Training trials--
#-------------------
for trial in trial_handler:
    stim = trial['stimulus']

    ITI.draw()
    score.draw()
    win.flip()
    keys = kb.waitKeys()

    stim.draw()
    score.draw()
    win.flip()
    core.wait(T_stim)
    
    T_delay_jitter = T_delay + np.random.uniform(*delay_jitter_range)
    score.draw()
    win.flip()
    core.wait(T_delay_jitter)

    random.shuffle(prototypes)
    idx = find_in_object(prototypes, 'category', trial['category'])
    correct_response = ['left'] if idx == 0 else ['right']

    for (i,p) in enumerate(prototypes):
        p['stimulus'].setPos(choice_positions[i]) 
        p['stimulus'].draw()

    score.draw()

    if IS_DEBUG_MODE :
        debug_msg.setText(f"cat : {trial['category']} \n diff : {trial['difficulty']} \n ID : {trial['stimulus_ID']}")
        debug_msg.draw()

    win.callOnFlip(kb.clock.reset)
    win.flip()

    keys = kb.waitKeys(maxWait=T_choice, keyList=['left', 'right'])

    correct = 0 
    T_feedback = 0
    if not keys:
        feedback.setText(timeout_fdbk_no_bonus)
        response = ""
        rt = None
        T_feedback = T_incorrect_fdbk
    else:
        response = keys[-1].name
        rt = keys[-1].rt

        if response in correct_response:
            feedback.setText(correct_fdbk_no_bonus)
            correct = 1
            T_feedback = T_correct_fbdk
        else:
            feedback.setText(wrong_fdbk_no_bonus)
            T_feedback = T_incorrect_fdbk

    exp.addData('response', response)
    exp.addData('correct', correct)
    exp.addData('correct_response', correct_response)
    exp.addData('response_time', rt)
    exp.addData('bonus', 0.0)
    exp.addData('difficulty', trial['difficulty'])
    exp.addData('category', trial['category'])
    exp.addData('phase', trial['phase'])
    exp.addData('t_delay', T_delay_jitter)
    exp.nextEntry()

    score.setText(f'Bonus : ${np.round(current_score,3)}')
    feedback.draw()
    score.draw()
    win.flip()
    core.wait(T_feedback)

    if 'escape' in event.waitKeys():
        exp.saveAsWideText('output.csv')
        win.close()
        core.quit()

intermission = visual.TextBox2(
    win, 
    pos=[0, 0], 
    text="""
        The practice round has finished. \n
        For the rest of the experiment you will receive a $0.05 bonus for each correct answer and lose $0.05 from your bonus for each incorrect answer! \n
        The bonus can not become less than $0. \n
        Press any key to begin the test.
    """,
    alignment='center'
)
intermission.draw()
win.flip()
keys = kb.waitKeys()

timer = core.CountdownTimer(T_experiment * 60)
#-------------------
#----Test trials----
#-------------------
current_difficulty = 1
past_data = deque([], N_trials_per_difficulty)
while timer.getTime() > 0 :

    current_difficulty = update_difficulty(current_difficulty, N_difficulty_levels, thrs_acc, past_data)

    trial = random.choice(stim_test[current_difficulty - 1])

    stim = trial['stimulus']

    ITI.draw()
    score.draw()
    win.flip()
    keys = kb.waitKeys()

    stim.draw()
    score.draw()
    win.flip()
    core.wait(T_stim)
    
    score.draw()
    win.flip()
    core.wait(T_delay)

    random.shuffle(prototypes)
    idx = find_in_object(prototypes, 'category', trial['category'])
    correct_response = ['left'] if idx == 0 else ['right']

    for (i,p) in enumerate(prototypes):
        p['stimulus'].setPos(choice_positions[i]) 
        p['stimulus'].draw()

    score.draw()

    if IS_DEBUG_MODE :
        debug_msg.setText(f"cat : {trial['category']} \n diff : {trial['difficulty']} \n ID : {trial['stimulus_ID']}")
        debug_msg.draw()

    win.callOnFlip(kb.clock.reset)
    win.flip()

    keys = kb.waitKeys(maxWait=T_choice, keyList=['left', 'right'])
    correct = 0 
    T_feedback = 0
    trial_bonus = 0
    if not keys:
        response = ""
        rt = None
        feedback.setText(timeout_fdbk_no_bonus)
        T_feedback = T_incorrect_fdbk
    else:
        response = keys[-1].name
        rt = keys[-1].rt

        if response in correct_response:
            trial_bonus = correct_bonus
            feedback.setText(correct_fdbk)
            correct = 1
            current_score += trial_bonus
            T_feedback = T_correct_fbdk
        else:
            feedback.setText(wrong_fdbk_no_bonus)
            T_feedback = T_incorrect_fdbk

    exp.addData('response', response)
    exp.addData('correct', correct)
    exp.addData('correct_response', correct_response)
    exp.addData('response_time', rt)
    exp.addData('bonus', trial_bonus)
    exp.addData('difficulty', trial['difficulty'])
    exp.addData('category', trial['category'])
    exp.addData('phase', trial['phase'])
    exp.nextEntry()

    past_data.appendleft({'correct' : correct, 'difficulty' : trial['difficulty']})

    score.setText(f'Bonus : ${np.round(current_score, 3)}')
    feedback.draw()
    score.draw()
    win.flip()
    core.wait(T_feedback)

    if 'escape' in event.waitKeys():
        exp.saveAsWideText('output.csv')
        win.close()
        core.quit()

win.close()
core.quit()

