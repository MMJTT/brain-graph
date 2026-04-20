---
id: map-agent-security-seed-corpus
title: Agent Security Seed Corpus
node_type: map
status: seed
tags:
  - seed-corpus
  - agent-security
created: 2026-04-20
updated: 2026-04-20
source_refs: []
related:
  - Prompt Injection
  - Red Teaming
  - Agent Benchmarks
  - Attack Paper Map
  - Defense Paper Map
  - Benchmark Paper Map
  - System Paper Map
focus: Initial survey map seeded from the local agent-papers PDF corpus.
includes:
  - Attack Paper Map
  - Defense Paper Map
  - Benchmark Paper Map
  - System Paper Map
  - Prompt Injection
  - Environmental Injection
  - Cross-Modal Injection
  - GUI Agents
  - Web Agents
  - Multimodal Agents
  - Red Teaming
  - Agent Benchmarks
  - Agent Defenses
  - Memory Poisoning
  - Jailbreak Attacks
  - DoS Attacks
  - Multi-Agent Systems
  - Computer-Use Agents
  - Evaluating the Robustness of Multimodal Agents Against Active Environmental Injection Attacks
  - AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents
  - Hijacking JARVIS: Benchmarking Mobile GUI Agents against Unprivileged Third Parties
  - AGENT POISON: Red-teaming LLM Agents via Poisoning Memory or Knowledge Bases
  - AgentSys: Secure and Dynamic LLM Agents Through Explicit Hierarchical Memory Management
  - AUTO DAN: Generating Stealthy Jailbreak Prompts on Aligned Large Language Models
  - AutoDefense: Multi-Agent LLM Defense against Jailbreak Attacks
  - Breaking Agents: Compromising Autonomous LLM Agents Through Malfunction Amplification
  - Caution for the Environment: Multimodal LLM Agents are Susceptible to Environmental Distractions
  - Manipulating Multimodal Agents via Cross-Modal Prompt Injection
  - EVA: Red-Teaming GUI Agents via Evolving Indirect Prompt Injection
  - The Obvious Invisible Threat: LLM-Powered GUI Agents' Vulnerability to Fine-Print Injections
  - Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection
  - OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments
  - Denial-of-Service Poisoning Attacks on Large Language Models
  - Red-Teaming LLM Multi-Agent Systems via Communication Attacks
  - RedTeamCUA: Realistic Adversarial Testing of Computer-Use Agents in Hybrid Web-OS Environments
  - ThinkTrap: Denial-of-Service Attacks against Black-box LLM Services via Infinite Thinking
  - UDora: A Unified Red Teaming Framework against LLM Agents by Dynamically Hijacking Their Own Reasoning
  - VisualWebArena: Evaluating Multimodal Agents on Realistic Visually Grounded Web Tasks
  - WebArena: A Realistic Web Environment for Building Autonomous Agents
  - WebInject: Prompt Injection Attack to Web Agents
questions:
  - Which attack families recur across web, GUI, and computer-use agents?
  - Which benchmark papers are best starting points for future imports?
  - Where are defense papers still sparse relative to attack papers?
---

# Agent Security Seed Corpus

## Focus
This map is the first connected view built from the local PDF corpus in `agent-papers`.

## Visual Entry
- Open [Starter Canvas](../../views/canvas/starter.canvas) for a ready-made Obsidian Canvas view.
- Use Obsidian's left sidebar graph icon for the vault-wide graph view.

```mermaid
graph LR
    corpus["Agent Security Seed Corpus"] --> attacks["Attack Paper Map"]
    corpus --> defenses["Defense Paper Map"]
    corpus --> benchmarks["Benchmark Paper Map"]
    corpus --> systems["System Paper Map"]
    attacks --> prompt["Prompt Injection"]
    defenses --> hardening["Agent Defenses"]
    benchmarks --> evals["Agent Benchmarks"]
    systems --> cua["Computer-Use Agents"]
```

## Topic Maps
- [[Attack Paper Map]]
- [[Defense Paper Map]]
- [[Benchmark Paper Map]]
- [[System Paper Map]]

## Included Nodes
- [[Prompt Injection]]
- [[Environmental Injection]]
- [[Cross-Modal Injection]]
- [[GUI Agents]]
- [[Web Agents]]
- [[Multimodal Agents]]
- [[Red Teaming]]
- [[Agent Benchmarks]]
- [[Agent Defenses]]
- [[Memory Poisoning]]
- [[Jailbreak Attacks]]
- [[DoS Attacks]]
- [[Multi-Agent Systems]]
- [[Computer-Use Agents]]

## Benchmark and Environment Papers
- [[AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents]]
- [[WebArena: A Realistic Web Environment for Building Autonomous Agents]]
- [[VisualWebArena: Evaluating Multimodal Agents on Realistic Visually Grounded Web Tasks]]
- [[OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments]]
- [[RedTeamCUA: Realistic Adversarial Testing of Computer-Use Agents in Hybrid Web-OS Environments]]
- [[Hijacking JARVIS: Benchmarking Mobile GUI Agents against Unprivileged Third Parties]]

## Injection and Environment Attack Papers
- [[Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection]]
- [[WebInject: Prompt Injection Attack to Web Agents]]
- [[EVA: Red-Teaming GUI Agents via Evolving Indirect Prompt Injection]]
- [[The Obvious Invisible Threat: LLM-Powered GUI Agents' Vulnerability to Fine-Print Injections]]
- [[Manipulating Multimodal Agents via Cross-Modal Prompt Injection]]
- [[Evaluating the Robustness of Multimodal Agents Against Active Environmental Injection Attacks]]
- [[Caution for the Environment: Multimodal LLM Agents are Susceptible to Environmental Distractions]]

## Defense, Poisoning, and DoS Papers
- [[AGENT POISON: Red-teaming LLM Agents via Poisoning Memory or Knowledge Bases]]
- [[AgentSys: Secure and Dynamic LLM Agents Through Explicit Hierarchical Memory Management]]
- [[Breaking Agents: Compromising Autonomous LLM Agents Through Malfunction Amplification]]
- [[AutoDefense: Multi-Agent LLM Defense against Jailbreak Attacks]]
- [[AUTO DAN: Generating Stealthy Jailbreak Prompts on Aligned Large Language Models]]
- [[Denial-of-Service Poisoning Attacks on Large Language Models]]
- [[ThinkTrap: Denial-of-Service Attacks against Black-box LLM Services via Infinite Thinking]]
- [[Red-Teaming LLM Multi-Agent Systems via Communication Attacks]]
- [[UDora: A Unified Red Teaming Framework against LLM Agents by Dynamically Hijacking Their Own Reasoning]]

## Open Questions
- Which nodes deserve full paper-level summaries next?
- Which concepts should become methods or gaps after manual review?
- Where are the strongest cross-links between benchmark papers and attack papers?
