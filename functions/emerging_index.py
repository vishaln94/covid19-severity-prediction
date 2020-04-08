import numpy as np

def compute_new_deaths(df, in_col='deaths'):
    '''
    compute new deaths
    '''
    return(
        df[in_col].apply(
            lambda x: np.array(
                [x[i+1] - x[i] for i in range(len(x) - 1)]
            )
        )
    )


def compute_emerging_index(x, n_days):
    growth = [x[i + 1] / np.maximum(x[i], 1) for i in range(len(x) - 1)]
    past_growth = growth[:n_days]
    pred_growth = growth[n_days:]
    past_growth_factor = np.mean(past_growth) + \
        np.cov(np.arange(n_days), past_growth)[0][1]
    pred_growth_factor = np.mean(pred_growth) + \
        np.cov(np.arange(len(pred_growth)), pred_growth)[0][1]
    return pred_growth_factor - past_growth_factor


def add_emerging_index(df, target_days=[1,2,3], n_days=3, min_deaths=20, new_deaths=True):
    """
    Computes differences in avg. predicted growth rate over next `n_days` days
    and the avg. observed growth rate over past `n_days` days.

    The reference day is the last observed.

    Parameters
    ----------
    df : a pandas.DataFrame with predictions (via add_preds)
    """
    assert len(target_days) >= n_days, "target_days length is less than n_days"

    # num_days = len(days) + target_days.size

    # get col names of past obs, plus one more as the baseline
    past_cols = df.filter(regex='#Deaths_').columns[-(n_days + 1):].tolist()

    # get col names of predictions
    pred_cols = [f'Predicted Deaths {day}-day' for day in target_days]

    assert set(pred_cols).issubset(df.columns), \
        f'not all predictions for target_days={str(target_days)} are in df!'

    past_days = list(map(lambda x: x.replace('#Deaths_', ''), past_cols))
    print("Reference Day: " + past_days[-1])

    # create a list column with past and predicted deaths
    d = df
    d['past_pred_deaths'] = d[past_cols + pred_cols].values.tolist()

    # TODO: stability of new_deaths vs. cumulative
    if new_deaths:
        # compute new deaths
        d['past_pred_deaths'] = compute_new_deaths(df, 'past_pred_deaths')

    # TODO: stability of n_days
    df['emerging_index'] = d['past_pred_deaths'].apply(lambda x: compute_emerging_index(x, n_days))

    # TODO: look into stability of this threshold
    # 0 out any county with less than min_deaths
    df['emerging_index'] = (1 - (df['tot_deaths'] < min_deaths)) * df['emerging_index']

    # scale to be between 0 and 1
    df['emerging_index'] = (df['emerging_index'] - df['emerging_index'].min()) / \
        (df['emerging_index'].max() - df['emerging_index'].min())

    return None
