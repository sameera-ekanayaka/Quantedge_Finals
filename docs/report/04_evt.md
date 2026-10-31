# Section 4: Extreme Value Theory and tail uncertainty

POT models loss exceedances Y = X − u. Under appropriate asymptotic conditions their conditional distribution approaches GPD: G(y) = 1 − (1 + ξy/σ)<sup>−1/ξ</sup>, σ > 0, y ≥ 0, 1 + ξy/σ > 0. Positive ξ means a power-law heavy tail; ξ = 0 is an unbounded exponential/Gumbel tail; negative ξ has a finite endpoint. This is an asymptotic approximation, not proof that financial losses follow a stable GPD.

## 4.1 Justified threshold and a second rule

The headline threshold is the 90th percentile of portfolio losses, 0.447%, with 552 exceedances in 5,518 observations. Mean-excess, shape/modified-scale stability and Q–Q plots support visual review. They do not automatically select the threshold. Fitted ξ = 0.1843 and σ = 0.002696 imply heavy tails. App and dashboard use the same threshold-selection function.

| Threshold quantile   | Threshold   |   Exceedances |   Shape | VaR    | ES     |
|:---------------------|:------------|--------------:|--------:|:-------|:-------|
| 80.0%                | 0.240%      |          1104 |   0.137 | 1.239% | 1.710% |
| 85.0%                | 0.318%      |           828 |   0.13  | 1.240% | 1.705% |
| 90.0%                | 0.447%      |           552 |   0.184 | 1.220% | 1.726% |
| 92.5%                | 0.531%      |           414 |   0.2   | 1.215% | 1.730% |
| 95.0%                | 0.662%      |           276 |   0.271 | 1.190% | 1.746% |
| 97.5%                | 0.881%      |           138 |   0.342 | 1.177% | 1.748% |

All risk columns above are at 99%. VaR/ES vary modestly over this grid while shape changes materially. A second exploratory rule minimises the fitted GPD's in-sample KS CDF discrepancy over this same prespecified grid, requiring at least 100 exceedances. It selects the 80th percentile, giving 99% VaR 1.239% and ES 1.710%. The fitted KS score is not a valid unadjusted hypothesis test, and this rule is not claimed statistically optimal. The 90th-percentile model remains the headline estimate.

## 4.2 Formulas and intervals

Let p = N<sub>u</sub>/N. For α inside the fitted tail and ξ ≠ 0, VaR<sub>α</sub> = u + (σ/ξ)[(p/(1 − α))<sup>ξ</sup> − 1]. ES<sub>α</sub> = (VaR<sub>α</sub> + σ − ξu)/(1 − ξ), requiring ξ < 1. At ξ = 0, VaR = u + σ log(p/(1 − α)) and ES = VaR + σ. For ξ ≥ 1 theoretical ES is infinite. Requests below the fitted tail are rejected, not extrapolated into the body.

| Measure   | 2.5%   | 97.5%   |   Valid replicates |   Failed replicates |
|:----------|:-------|:--------|-------------------:|--------------------:|
| VaR       | 1.123% | 1.299%  |                200 |                   0 |
| ES        | 1.488% | 1.966%  |                200 |                   0 |

These are 95% percentile intervals at 99% confidence from 200 IID bootstrap samples, seed 42, reselecting the 90th percentile and refitting the GPD each time. Failed/nonfinite replicates are counted; too many failures stop reporting. IID resampling ignores clustering and may understate uncertainty. Sensitivity tables and intervals measure different uncertainties and neither guarantees future coverage. At 90% confidence the bootstrap page uses an 89th-percentile threshold to avoid boundary/body extrapolation with resampled ties.
