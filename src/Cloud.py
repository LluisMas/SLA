# coding=utf-8

import numpy as np
import math


class Cloud:

    def __init__(self, virtual_machines=0, VM_capacity=0, VM_task=0, service_rate=0, input_traffic=0,
                 times_between_failure=0, recover_time=0, base_consumption=0, peak_consumption=0, frequency=0):

        self.frequency = frequency  # f
        self.peak_consumption = peak_consumption  # c1
        self.base_consumption = base_consumption  # c0
        self.recover_time = recover_time  # β
        self.times_between_failure = times_between_failure  # α
        self.input_traffic = input_traffic  # Lambda
        self.service_rate = service_rate  # µ
        self.virtual_machines = virtual_machines  # N
        self.VM_task = VM_task  # Task number for each VM - b
        self.VM_capacity = VM_capacity

    def get_utilisation_factor(self):  # ρ
        return self.input_traffic / (self.virtual_machines * self.service_rate)

    def get_mean_vm_number(self):
        utilisation_factor = self.get_utilisation_factor()

        result = 0
        for i in range(1, self.VM_task * self.virtual_machines):
            result += pow(utilisation_factor, i)

        return result * utilisation_factor * self.get_steady_probability_tasks(1)

    def get_steady_probability_tasks(self, i):
        if self.input_traffic == (self.virtual_machines * self.service_rate):
            return 1 / (self.VM_task * self.virtual_machines + 1)

        utilisation_factor = self.get_utilisation_factor()
        return pow(utilisation_factor, i) * (1 - utilisation_factor) / 1 - (
            pow(utilisation_factor, self.VM_task * self.virtual_machines + 1))

    def get_unavailability(self):
        result = 0
        for i in range(1, self.virtual_machines):
            result += self.get_probability_available(i) * self.get_loss_probability_capacity(i)

        return result

    def get_availability(self):
        return 1 - self.get_unavailability()

    def get_probability_available(self, n):
        result = math.factorial(self.virtual_machines) / math.factorial(n)
        result *= pow(self.times_between_failure / self.recover_time, self.virtual_machines - n)
        result *= self.get_probability_available_N()
        return result

    def get_probability_available_N(self):
        result = 0
        for i in range(0, self.virtual_machines):
            result += (math.factorial(self.virtual_machines) / math.factorial(self.virtual_machines - i)) \
                      * pow(self.times_between_failure / self.recover_time, i)

        return pow(result, -1)

    def get_probability_available_0(self):
        return math.factorial(self.virtual_machines) * \
               pow(self.times_between_failure / self.recover_time, self.virtual_machines) * \
               self.get_probability_available_N()

    def get_loss_probability_capacity(self, n):
        return n * self.get_loss_probability_buffer_overflow()

    def get_loss_probability_buffer_overflow(self):
        if self.input_traffic != self.service_rate:
            return 1 / (self.VM_task + 1)

        utilisation_factor = self.get_utilisation_factor()

        result = pow(utilisation_factor, self.VM_task) * (1 - utilisation_factor)
        result /= 1 - pow(utilisation_factor, self.VM_task + 1)

        return result

    def get_reliability(self):
        return 1 - self.get_probability_available_0()

    def get_power_consumption(self):
        return self.base_consumption + self.peak_consumption * pow(self.frequency, 2)
