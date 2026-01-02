"""Simulation script for LLM prototype"""
import random

import os
from edi_minimal_llm import generate, train


# Specialist users and their fields
SPECIALISTS = {
    "Economist": [
        "What is inflation?",
        "Explain supply and demand.",
        "How do interest rates affect the economy?",
        "Describe fiscal policy.",
        "What is GDP?",
        "How do markets work?",
        "What is monetary policy?",
        "Explain unemployment.",
        "What is a recession?",
        "How do taxes impact growth?"
    ],
    "Physicist": [
        "Explain quantum mechanics.",
        "What is relativity?",
        "Describe the Standard Model.",
        "What is dark energy?",
        "How does gravity work?",
        "What is a black hole?",
        "Explain string theory.",
        "What is a photon?",
        "Describe wave-particle duality.",
        "What is thermodynamics?"
    ],
    "Biologist": [
        "Explain evolution.",
        "What is DNA?",
        "Describe photosynthesis.",
        "What is a cell?",
        "How do genes work?",
        "What is natural selection?",
        "Describe ecosystems.",
        "What is a protein?",
        "Explain mitosis.",
        "What is biodiversity?"
    ],
    "Chemist": [
        "What is an atom?",
        "Explain chemical bonding.",
        "Describe acids and bases.",
        "What is a molecule?",
        "How does catalysis work?",
        "What is pH?",
        "Explain oxidation and reduction.",
        "What is a polymer?",
        "Describe the periodic table.",
        "What is a reaction rate?"
    ],
    "Computer Scientist": [
        "What is an algorithm?",
        "Explain machine learning.",
        "Describe a neural network.",
        "What is a database?",
        "How does encryption work?",
        "What is recursion?",
        "Explain big data.",
        "What is a compiler?",
        "Describe cloud computing.",
        "What is artificial intelligence?"
    ],
    "Historian": [
        "Describe the Renaissance.",
        "What caused World War II?",
        "Explain the Industrial Revolution.",
        "Who was Cleopatra?",
        "What is the Silk Road?",
        "Describe ancient Rome.",
        "What is feudalism?",
        "Explain the Cold War.",
        "Who was Genghis Khan?",
        "Describe the Enlightenment."
    ],
    "Philosopher": [
        "What is existentialism?",
        "Explain utilitarianism.",
        "Describe Plato's philosophy.",
        "What is ethics?",
        "What is consciousness?",
        "Explain logic.",
        "What is metaphysics?",
        "Describe the meaning of life.",
        "What is free will?",
        "Explain epistemology."
    ],
    "Mathematician": [
        "What is calculus?",
        "Explain prime numbers.",
        "Describe probability theory.",
        "What is a matrix?",
        "How does statistics work?",
        "What is geometry?",
        "Explain algebra.",
        "What is a function?",
        "Describe number theory.",
        "What is topology?"
    ],
    "Medical Doctor": [
        "What is diabetes?",
        "Explain the immune system.",
        "Describe hypertension.",
        "What is a virus?",
        "How do vaccines work?",
        "What is cancer?",
        "Explain antibiotics.",
        "What is a symptom?",
        "Describe the heart.",
        "What is mental health?"
    ],
    "Engineer": [
        "What is thermodynamics?",
        "Explain fluid mechanics.",
        "Describe a circuit.",
        "What is structural analysis?",
        "How does a motor work?",
        "What is robotics?",
        "Explain control systems.",
        "What is CAD?",
        "Describe materials science.",
        "What is an actuator?"
    ]
}

NUM_USERS = 10
PROMPTS_PER_USER = 500
results = []

model_path = 'edi_minigpt_epoch1.pth'
if not os.path.exists(model_path):
    print(f"Model weights '{model_path}' not found. Starting training...")
    train()
    print(f"Training complete. Model weights saved as '{model_path}'.")

for user_idx, (specialist, prompts) in enumerate(SPECIALISTS.items()):
    print(f"\n=== User {user_idx+1}: {specialist} ===")
    for prompt_idx in range(PROMPTS_PER_USER):
        prompt = random.choice(prompts)
        output = generate(prompt)
        print(f"[{specialist} Q{prompt_idx+1}] {prompt}\n[EDI] {output}\n")
        results.append({
            'user': specialist,
            'prompt_num': prompt_idx+1,
            'prompt': prompt,
            'output': output
        })

# Save results to file
import json
with open('edi_simulation_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Simulation complete. Results saved to edi_simulation_results.json.")
