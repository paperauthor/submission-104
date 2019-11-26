# Requirements

This code is written for Python 3.6 and external requirements are listed in the `requirements.txt` file.

To install them, start a fresh environment (virtualenv, conda, etc.), navigate to the `src` directory (also containing this `README.md`) and run

```shell
pip install -r requirements.txt
```

# Run experiments

This is the code to train different kinds of policies (logistic, semi-logistic, deterministic thresholded predictive model) via two different strategies (update on most recent data batch, update on all data).

The main driver file is `run.py` which takes a single argument, the path to a configuration json file:

```shell
python run.py --path path/to/config/file/config.json
```

There is a single config file for each experiment, which reside in the `experiments` folder:

* `config_uncalibrated.json`: This is the config file for the first synthetic 1D example with monotonically increasing $P(y = 1 | x)$, which is not calibrated however.
* `config_split.json`: This is the config file for the second synthetic 1D example with two disjoint green regions.
* `config_compas.json`: This is the config file for the real-world COMPAS dataset example.

In effect, each run of `run.py` is specific to a single dataset. However, it runs multiple different policies and training strategy combinations in a single run as specified by the `perform` option in the config file.

The standard setting is

```json
"perform": [
  ["recent", "logistic"],
  ["all", "logistic"],
  ["recent", "semi_logistic"],
  ["all", "semi_logistic"],
  ["recent", "deterministic_threshold"]
  ["all", "deterministic_threshold"],
]
```

This is a list of pairs consisting of `strategy` and `policy`. In this example we would run all combinations also shown in the paper.

The abbreviations `recent` and `all` refer to the iterative and aggregated sequences of policies, i.e., to the data on which the model is updated at each time step: `recent` means that we only update on the most recently observed batch of data, whereas `all` stands for updating on all data that has been seen so far.

For the policies, `logistic` and `semi-logistic` are the policies to directly learn decisions as described in the paper. They both use *IPS* (inverse propensity score weighting), i.e., the training strategy is aware of the data shift induced by the existing policy and corrects for it via inverse propensity score weighting as described in the paper.
The `deterministic_threshold` policy internally learns a predictive model for the labels $y$ (not for decisions!), i.e., $Q(y = 1| x, s)$ and then thresholds by the cost parameters, i.e., $d = 1[Q(y = 1 | x, s) \ge c]$.

The field `fairness` in the config files can take the values `null`, `"demographic_parity"`, and `"equal_opportunity"`, corresponding to no fairness constraints (`lamabda` is ignored), or constraining demographic parity and equal opportunity respectively.
The field `lambda` can be set to different values to tweak the relative importance of the penalty term to enforce fairness.

## Multiple runs

In order to understand the variance due to randomness, we perform multiple runs with different random seeds.

This can be done with `multiple_run.py`. For example, the command

```shell
python multiple_runs.py --path path/to/config/file/config_compas.json --runs 30 --offset 0 --processes 4
```

essentially runs `run.py` 30 times where it just replaces the `seed` setting as well as the `name` option within the `results` section of the config file for each run.
This way we just get enumerated directories starting at `000` containing the results for runs with different random seeds.
The `offset` option can be used to later add more runs, i.e., if we already did `--runs 30 --offset 0` , we can later continue with `--runs 20 --offset30` to add another 20 runs.
It uses the `multiprocessing` package to run multiple processes for the different runs in parallel (here 4).
To run the experiments used in the paper, call

```shell
python multiple_runs.py --path experiments/config_uncalibrated.json --runs 30 --processes 4
python multiple_runs.py --path experiments/config_split.json --runs 30 --processes 4
python multiple_runs.py --path experiments/config_compas.json --runs 30 --processes 4
```

where the number of processes can be adjusted of course.
For the experiments analyzing the dependence of $\lambda$, we need to sweep the `"lambda"` in the config json files.