<p align="center">
  <img src="static/img/logo.svg" alt="NormGym logo" width="160">
</p>

<h1 align="center">NormGym: Evaluating Normative Competence through Social Interaction</h1>

<p align="center">
  Binze Li<sup>1</sup>, Zihuan Zhang<sup>1</sup>, Seokhyun Baek<sup>1</sup>, Gillian K. Hadfield<sup>1,2,3*</sup>, Tianmin Shu<sup>1*</sup>
  <br>
  <sup>1</sup>Department of Computer Science, Johns Hopkins University&nbsp;&nbsp;
  <sup>2</sup>School of Government and Policy, Johns Hopkins University&nbsp;&nbsp;
  <sup>3</sup>Vector Institute for Artificial Intelligence
  <br>
  <sup>*</sup>Equal advising
</p>

<p align="center">
  <a href="https://binzeli.github.io/normgym-page/">Project Page</a>
</p>

---

## Overview

When people join a new community, they have to pick up its unwritten rules: where to walk, how to queue, which seats are taken. Nobody writes these down. They are learned by watching others and noticing who gets corrected.

**NormGym** is an interactive multi-agent benchmark that tests whether AI agents can do the same. A newcomer agent enters a grid-world community (a café, a post office, a grocery store) that follows a hidden norm. Breaking the norm is physically possible, but the offender is publicly sanctioned. The newcomer has its own task to complete and must infer the norm along the way, from its own sanctions and from the behavior and sanctions of others.

Every norm is deliberately arbitrary (a “silly rule”), so an agent cannot succeed by recalling familiar social conventions from pretraining.

## Benchmark

- **50 norms** in four families:
  - **Access** (12): where an agent may go
  - **Procedure** (11): how or when an agent moves
  - **Coordination** (16): position relative to others, e.g. queues
  - **Allocation** (11): how a shared resource is divided
- **10 environment layouts**, each with 6–10 agents from three social groups.
- **Two-phase evaluation:** the newcomer interacts with the community for 200 steps while updating a natural-language belief about the norm. That belief is then frozen and tested on new episodes, on both the layout it learned on and an unseen layout.
- **Joint success:** an episode counts only if the agent completes its task with zero norm violations.

## Key findings

1. **The tasks are easy; the norms are not.** The strongest model, Claude Opus 5, completes its task 95.7% of the time but reaches only 55.3% joint success. When GPT-5.6 Sol is told the norm directly, its joint success rises from 44.0% to 90.7%, so the difficulty lies in inferring the norm.
2. **Learning stalls early.** Belief correctness improves quickly over the first ~50 steps and then plateaus, even though agents keep being sanctioned.
3. **Models learn from their own mistakes, not from others'.** Beliefs improve most after the model's own violations, much less after seeing others sanctioned, and hardly at all from observing compliant behavior. Human participants, in contrast, report learning mainly by watching others.
4. **Fine-tuning helps only modestly.** Training Qwen3-VL-4B on compliant actions together with judging other agents' actions raises joint success on held-out norms from 0.0% to 13.7%, but the model still barely learns from other agents' behavior.

| Agent | Joint success (seen / unseen layout) | Task success |
|---|---|---|
| Claude Opus 5 | 55.3 / 51.3 | 95.7 / 96.7 |
| GPT-5.6 Sol | 44.0 / 40.7 | 86.3 / 83.0 |
| Gemini 3.1 Pro | 24.0 / 16.7 | 90.3 / 87.7 |
| Best open model (Ministral-3-8B) | 3.3 / 4.0 | 49.7 / 50.0 |
| Human (best observed) | 88.0 / 88.0 | 100.0 / 100.0 |

See the [project page](https://binzeli.github.io/normgym-page/) for full results.

## Citation

```bibtex
@misc{li2026normgym,
  title  = {{NormGym}: Evaluating Normative Competence through Social Interaction},
  author = {Li, Binze and Zhang, Zihuan and Baek, Seokhyun and Hadfield, Gillian K. and Shu, Tianmin},
  year   = {2026}
}
```

## About this repository

This repository hosts the source of the NormGym project page: a static site (`index.html` and `static/`) served with GitHub Pages. To preview it locally, run `python3 -m http.server` in this folder and open http://localhost:8000.
