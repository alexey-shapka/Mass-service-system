import random
import numpy
import matplotlib.pyplot as plt

avg_solution_time1 = 0.04623239994049072
avg_solution_time2 = 0.07163769721984864

first_range = (0.025087356567382812, 0.057845115661621094)
second_range = (0.059018850326538086, 0.10165119171142578) 

class Task:
    def __init__(self, t, s_t, d):
        self.time = t
        self.solution_time = s_t
        self.deadline = d

def GenerateQueue(periods, solution_time, range_random, tact_size):
    queue = []
    for i in range(len(periods)):
        tasks_per_tact = []
        for j in range(periods[i]):
            error = random.uniform(range_random[0], range_random[1])/2
            if random.random() < 0.5:
                tasks_per_tact.append(Task(i * tact_size, solution_time + error, i * tact_size + (solution_time + error) * random.randint(4,10)))
            else:
                tasks_per_tact.append(Task(i * tact_size, solution_time - error, i * tact_size + (solution_time + error) * random.randint(4,10)))                
        queue.append(tasks_per_tact)
    return queue

def SMO(queue, tact_size, number_of_tasks, type_smo):
    Statistic = {
    'average_wait_in_system' : 0,
    'solved_tasks' : 0,
    'average_queue_length' : [],
    'free_time' : 0,
    'skiped_tasks' : []}
    real_time_queue = []
    time = 0
    in_processor = 0
    remained_time = 0

    while True:
        #delete overdue tasks
        if in_processor == 0:
            before = len(real_time_queue)
            real_time_queue = [i for i in real_time_queue if i.deadline > time]
            after = len(real_time_queue)
            diff = before - after
            Statistic['skiped_tasks'].append(diff)

        #if all tasks already prepared
        if len(real_time_queue) == 0 and len(queue) == 0:
            print("Finished.")
            break
        #add tasks if it is new tact
        if len(queue) != 0 and remained_time == 0:
            real_time_queue += queue.pop(0)
            Statistic['average_queue_length'].append(len(real_time_queue))

        #if processor is empty - choose the shortest
        if in_processor == 0:
            if type_smo == 'RM':
                real_time_queue.sort(key=lambda x: x.solution_time)
            elif type_smo == 'EDF':
                real_time_queue.sort(key=lambda x: x.deadline)

        if len(real_time_queue) != 0:
            #calculate tasks in the same tact
            if remained_time != 0:
                if real_time_queue[0].solution_time > remained_time:
                    time += remained_time
                    real_time_queue[0].solution_time -= remained_time
                    in_processor = 1
                    remained_time = 0
                else:
                    remained_time -= real_time_queue[0].solution_time
                    time += real_time_queue[0].solution_time
                    Statistic['average_wait_in_system'] += time - real_time_queue[0].time - real_time_queue[0].solution_time
                    Statistic['solved_tasks'] += 1
                    del real_time_queue[0]
                    in_processor = 0
            #calculate in the new tact
            else:
                if real_time_queue[0].solution_time > tact_size:
                    real_time_queue[0].solution_time -= tact_size
                    in_processor = 1
                    remained_time = 0
                    time += tact_size
                else:
                    time += real_time_queue[0].solution_time
                    Statistic['average_wait_in_system'] += time - real_time_queue[0].time - real_time_queue[0].solution_time
                    Statistic['solved_tasks'] += 1
                    remained_time = tact_size - real_time_queue[0].solution_time
                    in_processor = 0
                    del real_time_queue[0] 
        #if real queue is empty add remained time and start next tact 
        else:
            if remained_time != 0:
                Statistic['free_time'] += remained_time
                time += remained_time
                remained_time = 0
        #add tact time to system time if no tasks in current tact
            else:
                Statistic['free_time'] += tact_size
                time += tact_size

    print(time, number_of_tasks * tact_size)
    Statistic['average_wait_in_system'] = Statistic['average_wait_in_system'] / Statistic['solved_tasks']
    Statistic['average_queue_length'] = sum(Statistic['average_queue_length']) / number_of_tasks
    return Statistic

def Execute(lambda_p, size, avg_sol_time, range, tact_size, type_smo):
    period = numpy.random.poisson(lambda_p, size)
    queue = GenerateQueue(period, avg_sol_time, range, tact_size)
    Stats  = SMO(queue, tact_size, size, type_smo)
    print("Number of tasks : {} Solved : {}".format(sum(period), Stats['solved_tasks']))
    return Stats

def CreateGraph(type_smo, tact_size):
    wait_time, queue_length, free_time = [], [], []
    for i in numpy.linspace(0.1, 10):
        one_smo = Execute(i, 100, avg_solution_time1, first_range, tact_size, type_smo)
        wait_time.append(one_smo['average_wait_in_system'])
        queue_length.append(one_smo['average_queue_length'])
        free_time.append(one_smo['free_time'])

    figure = plt.figure(figsize=(10,5))
    figure.canvas.set_window_title('Laboratory Work №5 ' + type_smo)

    t_i = figure.add_subplot(311)
    t_i.set_title("Average wait time / Intencities")
    t_i.set_xlabel('Intencities')
    t_i.set_ylabel('Time')
    t_i.plot(numpy.linspace(0.1, 10), wait_time, color = '#b2154f')

    w_ql = figure.add_subplot(312)
    w_ql.set_title("Average queue length / Average wait time")
    w_ql.set_xlabel('Average queue length')
    w_ql.set_ylabel('Average wait time')
    w_ql.plot(sorted(queue_length), wait_time, color = '#b2154f')

    f_p = figure.add_subplot(313)
    f_p.set_title("Free processor time / Intencities")
    f_p.set_xlabel('Intencities')
    f_p.set_ylabel('Free processor time')
    f_p.plot(numpy.linspace(0.1, 10), free_time, color = '#b2154f')

    plt.subplots_adjust(wspace=0.1, hspace=1, bottom=0.1, top=0.9)
    plt.show()

def AddTask():
    dots = []
    first = Execute(6.3, 100, avg_solution_time1, first_range, 0.1, 'RM')['skiped_tasks']
    second = Execute(6.3, 100, avg_solution_time1, first_range, 0.1, 'EDF')['skiped_tasks']
    for i in range(100):
        num = 0
        for j in range(i):
            num += first[j]
        dots.append(num)
    plt.plot(range(100), dots)
    plt.title('Overdue tasks / tact')
    plt.xlabel('Tact')
    plt.ylabel('Overdue tasks')
    plt.show()


AddTask()
CreateGraph('RM', 0.5)
CreateGraph('EDF', 0.5)