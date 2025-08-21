import random
import numpy as np
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import matplotlib.pyplot as plt

# --- Step 1: Superdense coding circuit builder ---
def superdense_coding(bits):
    b1, b0 = bits
    qc = QuantumCircuit(2, 2)
    
    # Create Bell/entangled pair
    qc.h(0)
    qc.cx(0, 1)
    
    # Alice encodes her two bits
    if b0 == 1:
        qc.x(0)
    if b1 == 1:
        qc.z(0)
    
    # Bob decodes
    qc.cx(0, 1)
    qc.h(0)
    
    # Measure both qubits
    qc.measure([0, 1], [0, 1])
    return qc

# --- IBM Service and backend setup ---
service = QiskitRuntimeService(channel="ibm_quantum_platform", token="_v9gTYOWfOOwvrDL9E00jnZxsKVyP0k9LwO6bKI9Q1ik")
backend = service.backend("ibm_brisbane")
sampler = Sampler(mode=backend)

# Transpiler setup
target = backend.target
pm = generate_preset_pass_manager(target=target, optimization_level=3)

# --- Step 2: Alice's 2-bit message ---
# --- Step 2: Randomly choose c and d ---
c = random.randint(0, 1)
d = random.randint(0, 1)
alice_bits = (c, d)  # MSB, LSB
qc_sdc = superdense_coding(alice_bits)

# Draw the circuit
print(f"Alice sends bits: {alice_bits}")
qc_sdc.draw("mpl")
plt.show()

# Transpile for backend
qc_isa = pm.run(qc_sdc)

# --- Step 3: Run on real backend ---
job = sampler.run([qc_isa], shots=1)
res = job.result()

# Extract measurement counts
try:
    counts = res[0].data.c.get_counts()
except:
    counts = res[0].data.get("c")

print("\nMeasurement counts:", counts)

# --- Step 4: Decode Bob's measurement ---
measured = list(counts.keys())[0]  # single shot
# Qiskit little-endian: 'c1c0'
bob_bits = (int(measured[1]), int(measured[0]))  # qubit0 -> c0, qubit1 -> c1

print(f"Bob received: {bob_bits}")