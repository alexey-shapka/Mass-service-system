import random
import numpy
import matplotlib.pyplot as plt

class Task:
    def __init__(self, t, s_t):
        self.arrival_time = t
        self.solution_time = s_t
        self.start_solution_time = s_t

def GenerateQueue(number_of_periods, lmbd, interval):
    poisson = numpy.random.poisson(lmbd, number_of_periods)
    queue = [[Task(i * interval, random.uniform(0.6, 25)) for j in range(poisson[i])] for i in range(len(poisson))]
    return queue

def SMO(queue, interval):
    Statistic = {
        'Average_wait_in_system' : 0,
        'Solved_tasks' : 0,
        'free_time' : 0
    }
    time = 0 #sys time
    real_time_queues = [[], [], []] #8,16,infinity

    smo_mode = 0
    time_for_solve = 0 #allotted time for task in current queue
    remained_time = 0 #remained time in current interval
    in_processor = 0 #check if processor is free

    while True:
        #finish if all tasks complete and queues are empty
        if len(queue) == 0 and len(real_time_queues[0]) == 0 and len(real_time_queues[1]) == 0 and len(real_time_queues[2]) == 0:
            break

        #add tasks if interval was overed
        if len(queue) != 0 and remained_time == 0:
            real_time_queues[0] += queue.pop(0)

        #check all queues and select smo mode to work
        if in_processor == 0:
            if len(real_time_queues[0]) != 0:
                smo_mode = 0
                time_for_solve = 8
            elif len(real_time_queues[1]) != 0:
                smo_mode = 1
                time_for_solve = 16
            elif len(real_time_queues[2]) != 0:
                smo_mode = 2
                time_for_solve = 999

        if len(real_time_queues[smo_mode]) != 0:
            #check if it is new interval or not
            if remained_time != 0:
                #if solving time more than remained time - calculate otherwise send to next queue
                if time_for_solve >= remained_time:
                    #check if task can be completed in this interval otherwise sub remained time from sol_time
                    if real_time_queues[smo_mode][0].solution_time >= remained_time:
                        time += remained_time
                        real_time_queues[smo_mode][0].solution_time -= remained_time
                        time_for_solve -= remained_time
                        in_processor = 1
                        remained_time = 0
                    #calculate new remained time and del task from queue (==completed)
                    else:
                        remained_time -= real_time_queues[smo_mode][0].solution_time
                        time += real_time_queues[smo_mode][0].solution_time
                        in_processor = 0
                        Statistic['Average_wait_in_system'] = time - real_time_queues[smo_mode][0].arrival_time - real_time_queues[smo_mode][0].start_solution_time
                        Statistic['Solved_tasks'] += 1
                        del real_time_queues[smo_mode][0]
                #send to another queue with new sol_time (sub remained time for solve from old sol_time )
                else:
                    real_time_queues[smo_mode][0].solution_time -= time_for_solve
                    remained_time -= time_for_solve
                    time += time_for_solve
                    in_processor == 0
                    if smo_mode == 0:
                        real_time_queues[1].append(real_time_queues[0].pop(0))
                    elif smo_mode == 1:
                        real_time_queues[2].append(real_time_queues[1].pop(0))

            #calculate in the new tact
            else:
                #if remained solving time more than interval do one interval
                if time_for_solve >= interval:
                    if real_time_queues[smo_mode][0].solution_time >= interval:
                        real_time_queues[smo_mode][0].solution_time -= interval
                        in_processor = 1
                        remained_time = 0
                        time += interval
                        time_for_solve -= interval
                    #calculate remained time in current interval and complete the task (del from queue)
                    else:
                        time += real_time_queues[smo_mode][0].solution_time
                        remained_time = interval - real_time_queues[smo_mode][0].solution_time
                        in_processor = 0
                        Statistic['Average_wait_in_system'] = time - real_time_queues[smo_mode][0].arrival_time - real_time_queues[smo_mode][0].start_solution_time
                        Statistic['Solved_tasks'] += 1
                        del real_time_queues[smo_mode][0] 
                #calculate remained time in current interval and complete the part of task that can be passed in current queue (send it to next queue)
                else:
                    real_time_queues[smo_mode][0].solution_time -= time_for_solve
                    time += time_for_solve
                    remained_time = interval - time_for_solve
                    in_processor = 0
                    if smo_mode == 0:
                        real_time_queues[1].append(real_time_queues[0].pop(0))
                    elif smo_mode == 1:
                        real_time_queues[2].append(real_time_queues[1].pop(0))
        #if all queues are empty - add interval or remained time to system clock
        else:
            if remained_time != 0: 
                Statistic['free_time'] += remained_time
                time += remained_time
                remained_time = 0
            else:
                Statistic['free_time'] += interval
                time += interval

    Statistic['Average_wait_in_system'] = Statistic['Average_wait_in_system'] / Statistic['Solved_tasks']
    return Statistic

def CreateGraphics(start, end, steps, interval):
    wait_time, free_time, number_of_tasks = [], [], []
    
    for i in numpy.linspace(start, end, num = steps):
        one_generation = SMO(GenerateQueue(100, i, interval), interval)
        wait_time.append(one_generation['Average_wait_in_system'])
        free_time.append(one_generation['free_time'])
        number_of_tasks.append((one_generation['Solved_tasks'], one_generation['Average_wait_in_system']))

    number_of_tasks.sort(key=lambda x: x[0])

    figure = plt.figure(figsize=(10,5))
    figure.canvas.set_window_title('Laboratory Work №3 MFQS')

    wt_i = figure.add_subplot(311)
    wt_i.set_title("Average wait time / Intencities")
    wt_i.set_xlabel('Intencities')
    wt_i.set_ylabel('Wait time')
    wt_i.plot(numpy.linspace(start, end, num = steps), wait_time, color = '#b2154f')

    f_i = figure.add_subplot(312)
    f_i.set_title("Free processor time / Intencities")
    f_i.set_xlabel('Intencities')
    f_i.set_ylabel('Free processor time')
    f_i.plot(numpy.linspace(start, end, num = steps), free_time, color = '#b2154f')

    t_i = figure.add_subplot(313)
    t_i.set_title("Number of tasks / Average wait time")
    t_i.set_xlabel('Number of tasks')
    t_i.set_ylabel('Wait time')
    t_i.plot([i[0] for i in number_of_tasks], [i[1] for i in number_of_tasks], color = '#b2154f')
    
    plt.subplots_adjust(wspace=0.1, hspace=1, bottom=0.1, top=0.9)
    plt.show()

CreateGraphics(0.1, 30, 50, 6)