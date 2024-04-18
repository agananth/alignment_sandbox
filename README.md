## CS 323 AI Awakening Memo 2: AI Alignment Sandbox

Developed with [AutoGen](https://microsoft.github.io/autogen/).

### Scenario 1: Recruiter Candidate Negotiation

Agents:
* Candidate: Passed the interviews at an AI development company; negotiating for high compensation. 
* Recruiter: Made an offer to the candidate; wants to hire the candidate but at the right price

This scenario is interactive! There are two configurable inputs: `--recruiter_flexibility` and `candidate_flexibility`. Both range
on a scale from 1 (least flexible) to 3 (most flexible). Try different combinations to see how that impacts 1) whether a deal is reached
2) what the deal's value is

For example: 
```
python3 recruiter_candidate_negotiation.py --recruiter_flexibility=1 --candidate_flexibility=3
```

Visualizations of the candidate's salary and stock requests, and the recruiter's offers, appear in the `recruiter_candidate_plots` folder.
These plots show how the requests and offers change over the course of the negotiation and end in either an accepted, rejected, or withdrawn offer.

### Scenario 2: Human-in-the-Loop Carbon Emissions Debate

Agents:
* Developing country Prime Minister: Reluctant to curb their country's economic growth for carbon emission targets that developed countries should bear the burden of.
* Developed country President: Offering financial assistance to the developing country, but impatient with progress!

As a human-in-the-loop, can you help the two sides put aside their differences and at least talk to each other?

```
python3 resource_debate.py
```
