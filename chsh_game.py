from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import numpy as np
import random
import matplotlib.pyplot as plt

# --- Step 1: Define CHSH circuit builder ---
def chsh_circuit(x, y):
    qc = QuantumCircuit(2, 2)

    # Alice: If x == 1, apply X gate (as in the image)
    if x == 1:
        qc.x(0)

    # Create Bell state
    qc.h(0)
    qc.cx(0, 1)

    # Alice's measurement basis (U_0 or U_{π/4})
    if x == 0:
        # U_0 = I (do nothing)
        pass
    else:
        # U_{π/4} = RY(π/2) = H (Hadamard)    U_{α}​=Ry​(2α)
        qc.ry(np.pi/2, 0)

    # Bob's measurement basis (U_{π/8} or U_{-π/8})
    if y == 0:
        qc.ry(np.pi/4, 1)  # U_{π/8}
    else:
        qc.ry(-np.pi/4, 1)   # U_{-π/8}

    # Measure
    qc.measure([0, 1], [0, 1])
    return qc


# --- IBM Service and backend setup ---
service = QiskitRuntimeService(channel="ibm_quantum_platform", token="")
backend = service.backend("ibm_brisbane")
sampler = Sampler(mode=backend)

# Transpiler setup
target = backend.target
pm = generate_preset_pass_manager(target=target, optimization_level=3)

# --- Step 2: Randomly choose x and y ---
x = random.randint(0, 1)
y = random.randint(0, 1)

qc_chsh = chsh_circuit(x, y)

# Draw the original circuit
print(f"Inputs: x = {x}, y = {y}")
qc_chsh.draw("mpl")
plt.show()

# Transpile for backend
qc_isa = pm.run(qc_chsh)

# --- Step 3: Run on real backend (or simulator) ---
job = sampler.run([qc_isa], shots=1)
res = job.result()

# Extract measurement counts
try:
    counts = res[0].data.c.get_counts()
except:
    counts = res[0].data.get("c")  # fallback if API version differs

print("\nMeasurement counts:", counts)

# --- Step 4: Analyze ---
# For single shot, pick the key
measured = list(counts.keys())[0]
alice = int(measured[1])  # c[0] corresponds to Alice
bob = int(measured[0])    # c[1] corresponds to Bob

print(f"Alice's output (a): {alice}")
print(f"Bob's output   (b): {bob}")




