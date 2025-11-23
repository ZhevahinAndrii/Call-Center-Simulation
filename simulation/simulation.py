import simpy
import random
import numpy as np

# Глобальні змінні для збору статистики
wait_times = []
queue_lengths = []
time_points = []

def call(env, name, handler, service_rate):
    """
    Представляє один дзвінок, який обробляється оператором або чат-ботом.
    """
    arrival_time = env.now
    with handler.request() as request:
        yield request
        wait = env.now - arrival_time
        wait_times.append(wait)
        service_time = random.expovariate(service_rate)
        yield env.timeout(service_time)

def call_generator(env, operator_res, chatbot_res, arrival_rate, service_rate, chatbots_enabled=True):
    call_id = 0
    while True:
        interarrival = random.expovariate(arrival_rate)
        yield env.timeout(interarrival)
        call_id += 1

        if chatbots_enabled and chatbot_res is not None:
            if random.random() < 0.8:
                env.process(call(env, f"Call_{call_id}_bot", chatbot_res, service_rate * 1.5))
            else:
                env.process(call(env, f"Call_{call_id}_op", operator_res, service_rate))
        else:
            env.process(call(env, f"Call_{call_id}", operator_res, service_rate))

def monitor(env, operator_res):
    """
    Моніторить довжину черги операторів.
    """
    while True:
        queue_lengths.append(len(operator_res.queue))
        time_points.append(env.now)
        yield env.timeout(1)

def run_simulation(lambda_calls, call_duration, operators, chatbots, simulation_time, random_seed, chatbots_enabled=True):
    global wait_times, queue_lengths, time_points
    wait_times = []
    queue_lengths = []
    time_points = []

    random.seed(random_seed)
    env = simpy.Environment()
    service_rate = 1 / call_duration

    operator_res = simpy.Resource(env, capacity=operators)
    chatbot_res = simpy.Resource(env, capacity=chatbots) if chatbots_enabled and chatbots > 0 else None

    env.process(call_generator(env, operator_res, chatbot_res, lambda_calls, service_rate, chatbots_enabled))
    env.process(monitor(env, operator_res))

    env.run(until=simulation_time)

    return {
        "wait_times": wait_times,
        "queue_lengths": queue_lengths,
        "time_points": time_points
    }

def calculate_metrics(simulation_results, operators, chatbots, lambda_calls, call_duration):
    """
    Обчислює ключові показники ефективності.
    """
    mu = 1 / call_duration
    total_handlers = operators + chatbots
    rho = lambda_calls / (total_handlers * mu) if total_handlers > 0 else float('inf')

    ANT = call_duration
    avg_wait = np.mean(simulation_results["wait_times"]) if simulation_results["wait_times"] else 0

    FCR = max(0.5, 1 - (rho - 0.8) * 0.5) if rho > 0.8 else 1.0
    CSAT = max(0, 100 - min(rho * 30, 60) - min(avg_wait * 5, 30))
    KLN = "High" if rho <= 0.9 else "Medium" if rho <= 1.0 else "Low"

    return {
        "rho": rho,
        "ANT": ANT,
        "FCR": FCR,
        "CSAT": CSAT,
        "KLN": KLN
    }
