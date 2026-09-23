import pandas as pd


POLLUTANT_COLUMNS = [
    "PM2.5",
    "PM10",
    "SO2",
    "NO2",
    "CO",
    "O3"
]


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create the same features used in AirShift Notebook 03.

    The input dataframe should contain chronological hourly
    observations for one or more monitoring stations.
    """

    df = df.copy()

    # Ensure datetime is properly formatted
    df["datetime"] = pd.to_datetime(df["datetime"])

    # Sort exactly as in Notebook 03
    df = (
        df.sort_values(
            ["station", "datetime"]
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------
    # Time-based features
    # --------------------------------------------------

    df["hour"] = df["datetime"].dt.hour

    df["day_of_week"] = (
        df["datetime"].dt.dayofweek
    )

    df["month"] = (
        df["datetime"].dt.month
    )

    df["is_weekend"] = (
        df["day_of_week"] >= 5
    ).astype(int)

    # --------------------------------------------------
    # Lag features
    # --------------------------------------------------

    lag_hours = [1, 3, 6]

    for column in POLLUTANT_COLUMNS:
        for lag in lag_hours:
            df[f"{column}_lag_{lag}h"] = (
                df.groupby("station")[column]
                .shift(lag)
            )

    # --------------------------------------------------
    # Rolling features
    # --------------------------------------------------

    rolling_windows = [3, 6]

    for column in POLLUTANT_COLUMNS:
        for window in rolling_windows:

            df[f"{column}_rolling_mean_{window}h"] = (
                df.groupby("station")[column]
                .transform(
                    lambda x: (
                        x.shift(1)
                        .rolling(window=window)
                        .mean()
                    )
                )
            )

            df[f"{column}_rolling_max_{window}h"] = (
                df.groupby("station")[column]
                .transform(
                    lambda x: (
                        x.shift(1)
                        .rolling(window=window)
                        .max()
                    )
                )
            )

            df[f"{column}_rolling_std_{window}h"] = (
                df.groupby("station")[column]
                .transform(
                    lambda x: (
                        x.shift(1)
                        .rolling(window=window)
                        .std()
                    )
                )
            )

    # --------------------------------------------------
    # Change features
    # --------------------------------------------------

    change_hours = [1, 3]

    for column in POLLUTANT_COLUMNS:
        for lag in change_hours:
            df[f"{column}_change_{lag}h"] = (
                df.groupby("station")[column]
                .diff(lag)
            )

    # --------------------------------------------------
    # Trend features
    # --------------------------------------------------

    # 3-hour trend
    for column in POLLUTANT_COLUMNS:

        previous_1 = (
            df.groupby("station")[column]
            .shift(1)
        )

        previous_3 = (
            df.groupby("station")[column]
            .shift(3)
        )

        df[f"{column}_trend_3h"] = (
            previous_1 - previous_3
        ) / 2

        # 6-hour trend
        x1 = df.groupby("station")[column].shift(1)
        x2 = df.groupby("station")[column].shift(2)
        x3 = df.groupby("station")[column].shift(3)
        x4 = df.groupby("station")[column].shift(4)
        x5 = df.groupby("station")[column].shift(5)
        x6 = df.groupby("station")[column].shift(6)

        df[f"{column}_trend_6h"] = (
            -5 * x6
            -3 * x5
            -1 * x4
            +1 * x3
            +3 * x2
            +5 * x1
        ) / 35

    return df