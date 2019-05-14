import numpy as np
import sys


class Queue:
    def __init__(self, n, u):
        self.n, self.u, self.broadcasting_time, self.waiting_time = n, u, 0, 0
        self.q = []
        self.tries = 0

    # get remaining time of all packages in queue
    def remainingTime(self):
        if len(self.q) == 0:
            return 0

        return sum([pkg.time_left for pkg in self.q])

    # add a package to queue
    def add(self, start_time):
        self.tries += 1
        if len(self.q) == self.n:
            return False

        self.q.append(Package(start_time, self.u))
        return True

    # move the time forward, proceed to next package in line when needed
    def forward(self, current_time, time_to_forward):
        time_forwarded = 0
        i, max_iterations = 0, len(self.q)
        while time_to_forward > time_forwarded and i < max_iterations:
            time_forwarded += self.q[0].forward(time_to_forward - time_forwarded)
            if self.q[0].time_left == 0:
                self.q.pop(0)
                if len(self.q) > 0:
                    self.waiting_time += (current_time + time_forwarded) - self.q[0].start_time
            i += 1
        self.broadcasting_time += time_forwarded

class Package:
    def __init__(self, start_time, u):
        self.start_time = start_time
        self.time_left = np.random.exponential(u)

    def forward(self, time_to_forward):
        delta = self.time_left
        self.time_left = max(self.time_left - time_to_forward, 0)
        delta -= self.time_left

        return delta


if __name__ == "__main__":
    total_time = float(sys.argv[1])
    number_of_ports = int(sys.argv[2])
    probs = [float(sys.argv[p]) for p in range(3, 3 + number_of_ports)]
    #print(probs)
    lam = 1/float(sys.argv[3 + number_of_ports])
    q_sizes = [int(sys.argv[p]) for p in range(4 + number_of_ports, 4 + number_of_ports*2)]
    q_u = [1/float(sys.argv[p]) for p in range(4 + number_of_ports*2, 4 + number_of_ports*3)]

    ports = [Queue(q_sizes[i], q_u[i]) for i in range(number_of_ports)]

    current_time = 0
    time_to_forward = np.random.exponential(lam)
    packages = 0
    success_packages = 0

    while current_time + time_to_forward < total_time:
        for port in ports:
            port.forward(current_time, time_to_forward)

        packages += 1
        chosen_port = np.random.choice(a=ports, size=None, p=probs)
        if chosen_port.add(current_time + time_to_forward):
            success_packages += 1

        # prepare for next iteration
        current_time += time_to_forward
        time_to_forward = np.random.exponential(lam)

    total_waiting_time, total_broadcasting_time = 0, 0
    end_time = 0
    for port in ports:
        #print("tries: {} => {}".format(port.tries, port.tries/packages))
        end_time = max(end_time, current_time + port.remainingTime())
        port.forward(current_time, port.remainingTime())
        total_waiting_time += port.waiting_time
        total_broadcasting_time += port.broadcasting_time

    mean_waiting_time = total_waiting_time / success_packages
    mean_broadcasting_time = total_broadcasting_time / success_packages
    failed_packages = packages - success_packages

    print("{} {} {} {} {}".format(success_packages, failed_packages,
                                  end_time, mean_waiting_time, mean_broadcasting_time))
