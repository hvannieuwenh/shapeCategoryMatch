const IS_DEBUG = false
const IS_ONLINE = true
const time_experiment = 10; // minutes
const T_exp = time_experiment * 60 * 1000; // ms 
const N_training_trials = 10;

const thrs_accuracy = 0.75;
const N_difficulty_levels = 5;
const N_exemplars_per_difficulty = 17;
const N_trials_per_difficulty = 5;

const incorrect_penalty = -0.1;

var additional_bonus = 0.0;
const T_additional_bonus_1 = 3; // minutes
const T_additional_bonus_2 = 6; // minutes

var is_time_out = false;
var score = 0;

var current_difficulty = 1;
var current_stimulus = 0;

var timeline = []; 

const pack_name = "pack_noise_shapes_3"
const stim_path = "./stimuli/" ;
const stimulus_format = "mp4";

if (IS_ONLINE){
    var jsPsych = initJsPsych({
        on_finish: function() {
            jatos.endStudy(jsPsych.data.get().csv());
        }
    })
    jatos.onLoad(function(){
        var subj_id = jatos.urlQueryParameters.PROLIFIC_PID
        var std_id = jatos.urlQueryParameters.STUDY_ID
        var sess_id = jatos.urlQueryParameters.SESSION_ID

        jsPsych.data.addProperties({
            subject_id: subj_id,
            study_id: std_id,
            session_id: sess_id
        });
    });
}else{
    ID = rand_in_range(1001, 9999)

    var jsPsych = initJsPsych({
        on_finish: function() {
            jsPsych.data.get().localSave('csv',`results_${ID}.csv`);
        }
    })
}

setTimeout(
    function(){
        jsPsych.endExperiment(`<p> The experiment has concluded. <br> Thank you for participating! <br> <font color="green"> You have won a $${score} bonus! </font></p>`);
    }, 
    T_exp
);

setTimeout(
    function(){
        additional_bonus += 0.05;
    },
    T_additional_bonus_1 * 60 * 1000
)

setTimeout(
    function(){
        additional_bonus += 0.05;
    },
    T_additional_bonus_2 * 60 * 1000
)

const exemplar_range_per_difficulty = range(1, N_exemplars_per_difficulty)
const P_difficulty_training = [0.6, 0.4, 0.0, 0.0, 0.0];

var stimuli_training = [];
var stimuli_test = [];
for (let d of range(1, N_difficulty_levels)){
    const idx_cat_1_training = jsPsych.randomization.sampleWithoutReplacement(exemplar_range_per_difficulty, Math.floor(P_difficulty_training[d-1]*(N_training_trials/2)));
    const idx_cat_2_training = jsPsych.randomization.sampleWithoutReplacement(exemplar_range_per_difficulty, Math.floor(P_difficulty_training[d-1]*(N_training_trials/2)));
    const idx_cat_1_test = exemplar_range_per_difficulty.filter(x => !idx_cat_1_training.includes(x));
    const idx_cat_2_test = exemplar_range_per_difficulty.filter(x => !idx_cat_2_training.includes(x));

    const stimuli_cat_1_training = exemplar_stimuli(idx_cat_1_training, stim_path, pack_name, 1, d, 'train', stimulus_format);
    const stimuli_cat_2_training = exemplar_stimuli(idx_cat_2_training, stim_path, pack_name, 2, d, 'train', stimulus_format);
    stimuli_training.push(stimuli_cat_1_training.concat(stimuli_cat_2_training));

    const stimuli_cat_1_test = exemplar_stimuli(idx_cat_1_test, stim_path, pack_name, 1, d, 'test', stimulus_format);
    const stimuli_cat_2_test = exemplar_stimuli(idx_cat_2_test, stim_path, pack_name, 2, d, 'test', stimulus_format);
    stimuli_test.push(stimuli_cat_1_test.concat(stimuli_cat_2_test));
}

var prototypes = [
    {
        stimulus: `${stim_path}/${pack_name}/cat_1/prototype_1.png`, 
        exemplar_ID: 0,
        category: 1,
        difficulty: 0,
        phase: 'prototype'
    },
    {
        stimulus: `${stim_path}/${pack_name}/cat_2/prototype_2.png`, 
        exemplar_ID: 0,
        category: 2,
        difficulty: 0,
        phase: 'prototype'
    }
];

var preload = {
    type: jsPsychPreload,
    video: function(){
        const s = stimuli_test.concat(stimuli_training)
        s.flat()
    }
};
timeline.push(preload);

var welcome = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: "Welcome to the Category Matching experiment! Press any key to continue.",
  data: {task: 'welcome'}
};
timeline.push(welcome)

var intro_1 = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: `
            <p>You will be shown movies. Each movie contains a shape that initially is hidden and is gradually revealed. 
            <p> While you watch a shape being revealed, you have to choose which shape from the two below it is most similar to : </p>
            <div class="container">
                <div class="photos">
                    <img class="image" src=${prototypes[0].stimulus}>
                    <span class="word"><b>Press left arrow key to choose this shape.</b></span>
                </div>
                <div class="photos">
                    <img class="image" src=${prototypes[1].stimulus} >
                    <div class="word"><b>Press right arrow key to choose this shape.</b></div>
                </div>
            </div>
            <br>
            <p>Press any key to continue.</p>
            `,
  data: {task: 'introduction_1'}
};
timeline.push(intro_1)

var intro_2 = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: `
            <p> After you choose, the screen will show you whether you were correct or not.</p>
            <p><b>You will receive a bonus payment for each correct answer! The faster you answer the higher the bonus will be!</b></p>
            <p> So you can increase your bonus by guessing as quickly and accurately as possible.</p>
            <p><b>You will lose $0.1 from your bonus payment for each incorrect answer! The bonus can not become less than $0.</b> </p>
            <p>Press any key to continue.</p>
    `,
    data: {task: 'introduction_2'}
  };
  timeline.push(intro_2)

var intro_3 = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: `
            <p> <b>The first 10 shapes are a practice round that will not count towards your bonus payment.</b></p>
            <p> You will be notified when practice finishes and the test begins. </p>
            <p> Press any key to begin the practice round.</p>
            `,
    data: {task: 'introduction_3'}
  };
timeline.push(intro_3)

var ITI = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: function (){
        return `
            ${wrap_score_in_html(score)}
            <p> Please press any key to continue to the next movie.</p>
            <p> Remember your choices : <p>
            <div class="container">
                <div class="photos">
                    <img class="image" src=${prototypes[0].stimulus}>
                    <span class="word"><b>Press left arrow key if the shape looks like this one.</b></span>
                </div>
                <div class="photos">
                    <img class="image" src=${prototypes[1].stimulus}>
                    <div class="word"><b>Press right arrow key if the shape looks like this one.</b></div>
                </div>
            </div>
        `
    },
    data: {task: 'ITI'}
};

var stim_train = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: function (){
        return wrap_video_stim_in_html(jsPsych.timelineVariable('stimulus'), score)
    },
    choices: ['ArrowLeft', 'ArrowRight'],
    data: function(){
        return {
            task: 'response',
            stimulus: jsPsych.timelineVariable('stimulus'),
            correct_response: jsPsych.timelineVariable('correct_response'),
            exemplar_ID: jsPsych.timelineVariable('exemplar_ID'),
            category: jsPsych.timelineVariable('category'),
            difficulty: jsPsych.timelineVariable('difficulty'),
            phase: jsPsych.timelineVariable('phase')
        }
    },
    trial_duration: 5500,
    on_finish: function(data){
        data.correct = jsPsych.pluginAPI.compareKeys(data.response, data.correct_response);
    },
    render_on_canvas: false
};

var stim_test = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: function (){
        const responses = jsPsych.data.get().filter({task: 'response', phase: 'test'}).last(N_trials_per_difficulty).values();
        const N = responses.length;
        const is_all_same_difficulty = responses.every(x => x.difficulty == current_difficulty);

        if (is_all_same_difficulty && N == N_trials_per_difficulty){
            const N_corrects = responses.reduce((acc, x) => acc + x.correct, 0);
            const accuracy = N_corrects / N;

            if (accuracy >= thrs_accuracy && N == N_trials_per_difficulty && current_difficulty < N_difficulty_levels){
                current_difficulty += 1;
            }else if (accuracy < thrs_accuracy && N == N_trials_per_difficulty && current_difficulty > 1){
                current_difficulty -= 1;
            }
        }
        current_stimulus = sample_stimulus(stimuli_test, current_difficulty);
        return wrap_video_stim_in_html(current_stimulus.stimulus, score)
    },
    choices: ['ArrowLeft', 'ArrowRight'],
    data: function(){
        return {
            task: 'response',
            stimulus: current_stimulus.stimulus,
            correct_response: current_stimulus.correct_response,
            exemplar_ID: current_stimulus.exemplar_ID,
            category: current_stimulus.category,
            difficulty: current_stimulus.difficulty,
            phase: current_stimulus.phase
        }
    },
    trial_duration: 5500,
    on_finish: function(data){
        data.correct = jsPsych.pluginAPI.compareKeys(data.response, data.correct_response);
    },
    render_on_canvas: false
};

var trial_bonus = 0;

var feedback_test = {
    type: jsPsychHtmlKeyboardResponse,
    trial_duration: function(){
        const last_trial = jsPsych.data.get().filter({task: 'response'}).last(1).values()[0];
        if(last_trial.correct){
            return 1500
        }else{
            return 5000
        }
    },
    stimulus: function(){
        const last_trial = jsPsych.data.get().filter({task: 'response'}).last(1).values()[0];
        const is_score_zero = !(score >= Math.abs(incorrect_penalty));
        if (last_trial.response) {
            if(last_trial.correct){
                trial_bonus = RT_to_reward(last_trial.rt) + additional_bonus;
                trial_bonus = Math.round(trial_bonus * 100) / 100;

                score += trial_bonus;
                score = Math.round(score * 100) / 100;
                return positive_feedback(trial_bonus)
            } else {
                if (!is_score_zero){
                    trial_bonus = incorrect_penalty;
                    score += trial_bonus;
                    score = Math.round(score * 100) / 100;
                    return negative_feedback(trial_bonus)
                }else{
                    return negative_feedback_no_bonus()
                }
            }
        } else {
            if (!is_score_zero){
                trial_bonus = incorrect_penalty;
                score += trial_bonus;
                score = Math.round(score * 100) / 100;
                return timeout_feedback(trial_bonus)
            } else {
                return timeout_feedback_no_bonus()
            }
        }
    },
    data: function(){
        return {task: 'feedback', bonus: score, trial_bonus: trial_bonus}
    },
    choices: "NO_KEYS"
};

var feedback_train = {
    type: jsPsychHtmlKeyboardResponse,
    trial_duration: function(){
        const last_trial = jsPsych.data.get().filter({task: 'response'}).last(1).values()[0];
        if(last_trial.correct){
            return 1500
        }else{
            return 5000
        }
    },
    stimulus: function(){
        const last_trial = jsPsych.data.get().filter({task: 'response'}).last(1).values()[0];
        if (last_trial.response) {
            if(last_trial.correct){
                return `<p> <font color="green" size="5vw"> Correct category! </font> </p>`;
            } else {
                return `<p> <font color="red" size="5vw"> Wrong category! </font> </p>`;
            }
        } else {
            return `<p> <font color="red" size="5vw"> Time out! </font> <br> Please try to respond as quickly as possible. </p>`
        }
    },
    data: function(){
        return {task: 'feedback', bonus: score,  trial_bonus: trial_bonus}
    },
    choices: "NO_KEYS"
};

var trials_training = {
    timeline : [ITI, stim_train, feedback_train],
    timeline_variables : stimuli_training.flat(),
    randomize_order : true
};
timeline.push(trials_training)

var intermission = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: `
            <b> <p> The practice round has finished.</p>
            <b> <p> For the rest of the experiment you will receive a bonus payment for each correct answer, which will be higher the faster you answer!</b></p>
            <b> <p> Also you will lose $0.1 from your bonus payment for each incorrect answer!</p>
            <p> Press any key to begin the test. </p>
            `,
    data: {task: 'intermission'}
  };
timeline.push(intermission)

var trials = {
    timeline : [ITI, stim_test, feedback_test],
    loop_function: function(data){
        return true;
    }
};
timeline.push(trials)

if (IS_ONLINE){
    jatos.onLoad(() => {jsPsych.run(timeline);});
}else{
    jsPsych.run(timeline);
}
