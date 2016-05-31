import seaborn
import numpy as np
import pandas as pd


class WaterfallGraph(object):

    def __init__(self):
        pass

    def get_ranking_by_impact(self, df, metric_name):

        abs_metric_col = '{}_abs'.format(metric_name)
        df[abs_metric_col] = abs(df[metric_name])
        df = df.sort_values(abs_metric_col, ascending=False)
        df = df.head(10)
        df = pd.DataFrame(df[metric_name])
        return df

    def plot(self, data=None, metric_type=None, metric_name=None, metric_cols=None, split_dimension=None, **kwargs):
        """
        Generates Waterfall inside a figure

        Key arguments:
        - data: data frame
        - metric_type: enum['absolute', 'relative']
        - metric_name: Metric name in lower case and no spaces to show in the graph
        - metric_cols: waterfall metric (Eg.: Rides [0] [%])
          - relative: ['boarded','boarded_1_period'] >> [0] = boarded/boarded_1_period
          - absolute: ['boarded'] >> boarded
        - split_dimension: dimension to break (Eg.: dimension = country so waterfall shows contribution to total [0] by country)
        - kwargs:
          - ax = axis array of figure
          - title

        Adds subplot to the figure with the waterfall graph
        """

        assert metric_type == 'relative'  # in ('relative','absolute') Absolute not implemented
        assert metric_cols is not None
        assert metric_name is not None
        if metric_type == 'absolute':
            assert len(metric_cols) == 1
        if metric_type == 'relative':
            assert len(metric_cols) == 2

        formatted_metric_name = metric_name.capitalize()
        data = data[data[split_dimension].notnull()]
        data[metric_name] = ((data[metric_cols[0]] / data[metric_cols[1]] - 1) * (data[metric_cols[1]] / data[metric_cols[1]].sum())) * 100
        data = data[[split_dimension, metric_name]].set_index(split_dimension)
        total = data.sum()[0]
        trans = self.get_ranking_by_impact(data, metric_name)

        trans.loc["Others"] = total - trans.sum()[0]
        blank = trans[metric_name].cumsum().shift(1).fillna(0)

        col_name = "Total {}".format(formatted_metric_name)
        trans.loc[col_name] = total
        blank.loc[col_name] = total

        trans.loc[col_name, '{}_2'.format(metric_name)] = total
        trans.loc[col_name, metric_name] = np.nan

        step = blank.reset_index(drop=True).repeat(3).shift(-1)
        step[1::3] = np.nan

        blank.loc[col_name] = 0
        my_plot = trans.plot(
            kind='bar', stacked=True, bottom=blank, legend=None, title=kwargs.get('title', None), ax=kwargs.get('ax', None), sharex=False)
        my_plot.plot(step.index, step.values, '#808080')
        my_plot.axes.get_yaxis().set_visible(False)
        y_height = trans[metric_name].cumsum().shift(1).fillna(0)

        max = trans[metric_name].max()
        neg_offset = max / 25
        pos_offset = max / 50
        plot_offset = int(max / 15)

        trans.loc[col_name, metric_name] = total

        # Start label loop
        loop = 0
        for index, row in trans.iterrows():
            # For the last item in the list, we don't want to double count
            if row[metric_name] == total:
                y = y_height[loop]
            else:
                y = y_height[loop] + row[metric_name]
            # Determine if we want a neg or pos offset
            if row[metric_name] > 0:
                y += pos_offset
            else:
                y -= neg_offset
            if row[metric_name] < 0:
                vertical_align = "top"
            else:
                vertical_align = "bottom"
            my_plot.annotate("{:,.1f}%".format(
                row[metric_name]), (loop, y), ha="center", weight="medium", size="large", va=vertical_align)
            loop += 1

        return None
