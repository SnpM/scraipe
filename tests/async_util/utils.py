def generate_tasks(tasks_lambda, n):
    return [t for _ in range(n) for t in tasks_lambda()]