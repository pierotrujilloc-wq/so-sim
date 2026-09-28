"""Algoritmos escritos explícitamente, sin bibliotecas de simulación."""

from .fcfs import fcfs
from .sjf import sjf
from .prioridad import por_prioridad
from .round_robin import round_robin

__all__ = ["fcfs", "sjf", "por_prioridad", "round_robin"]
