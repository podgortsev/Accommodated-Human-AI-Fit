# Methodology checklist, paper 4

The checklist from the paper 2 repository's `CLAUDE.md`, item by item, against
e0 to e5 and the draft. Rule 3 of START-HERE: a paper that has not passed it does
not go out. Worked 2026-10-06.

| item | status | evidence |
|---|---|---|
| Pair the data | pass | every contrast paired within question (e0 to e5) or within first turn (e3) |
| Test named precisely | pass | Wilcoxon signed-rank plus sign-flip permutation on the mean, both required; named in the paper, Design |
| Correct for multiplicity | pass | Benjamini-Hochberg per contrast type per model; floors Holm per model, either test |
| Run a control that carries no signal | pass | three neutral details at each length, and the no-lead-in cell, in every experiment |
| Several neutral wrappers | pass | e5: the deafness headline holds under three wrappers on all three models; the spread across wrappers (up to 0.25 on the need benefit) is reported as the error bar |
| Check coherence | pass | for deafness the two parts move in opposite directions as they should (text route up, phone instruction down); specificity checks show a need moves its own delivery more than other needs' |
| Counterbalance position | pass | e5's "after" wrapper puts the lead-in after the question; the headline holds on all three models |
| Match length | pass | need form and neutral details 16 words, label and neutral details 5 words, checked mechanically; e3 follow-ups 14 words each |
| Do not dilute the signal | pass, one exception reported | the lead-in sits next to the question everywhere except e4, where the calculation sits between; e4's deafness shrinkage is reported with dilution as one explanation |
| Negative trait words suppressed | not applicable | no trait words |
| Check the format the model was meant to answer in | pass | e4 counts missing Answer lines separately; no probability reads in this paper |
| A control must vary the thing under test | pass | the neutral arm varies the presence of a personal detail, which is what a benefit read against nothing confounds |
| A degenerate control does not measure the instrument | pass | no residual computed from identical comparisons |
| Refusal is not a low number | **pass after 2026-10-06** | not counted in e0 to e2 at first; `experiments/exploratory-refusals/scripts/analyse_refusals.py` now counts them: Llama refuses after the learning-disability and screen-reader labels; scoring refusals as not delivered leaves every registered finding standing. Exploratory, reported as such |
| Watch for anchoring | not applicable | no numeric estimates about the person |
| Do not put the answer in the question | pass | need forms never name a checked property (validated offline) |
| Parse in the right order | pass | e4 looks for the Answer number first; refusal is never inferred from a missing number |
| Fix ranges before discarding data | not applicable | nothing discarded |
| Register expectations before running | pass | e0 to e5 each committed before its first generation |

Corrections made during the work, each reported where it occurs: the
plain-language splitter (e0), the deafness item set (e1), the wheelchair reading
(e1, H2 in absolute points), the hotline example wording (e0).

**Status: passes, 2026-10-07.** Every applicable item passes.
