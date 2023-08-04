from typing import Tuple, Optional

import pandas as pd
from sklearn import linear_model
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

import config


COL_POPULARITY = "popularity"
COL_GEN_POPULARITY_CLASS = "popularity_class"
# identifying meta-data
COL_ARTIST_NAME = "artist_name"
COL_TRACK_NAME = "track_name"
COL_TRACK_ID = "track_id"
# categorical features
COL_GENRE = "genre"
COL_KEY = "key"
COL_MODE = "mode"  # binary
COLS_MUSICAL_CATEGORIES = [COL_GENRE, COL_KEY, COL_MODE]
# normalised numeric features
COL_DANCEABILITY = "danceability"
COL_ENERGY = "energy"
COL_SPEECHINESS = "speechiness"
COL_ACOUSTICNESS = "acousticness"
COL_INSTRUMENTALNESS = "instrumentalness"
COL_LIVENESS = "liveness"
COL_VALENCE = "valence"
COLS_MUSICAL_DEGREES = [COL_DANCEABILITY, COL_ENERGY, COL_SPEECHINESS, COL_ACOUSTICNESS, COL_INSTRUMENTALNESS,
    COL_LIVENESS, COL_VALENCE]
# other numeric features
COL_YEAR = "year"
COL_LOUDNESS = "loudness"  # probably RMS or LUFS
COL_TEMPO = "tempo"  # BPM
COL_DURATION_MS = "duration_ms"
COL_TIME_SIGNATURE = "time_signature"  # probably notes per bar (but non-uniform semantics: quarter or eighth notes)

CLASS_POPULAR = "popular"
CLASS_UNPOPULAR = "unpopular"


class Dataset:
    def __init__(self, num_samples: Optional[int] = None, drop_zero_popularity: bool = False, threshold_popular: int = 50,
            random_seed: int = 42):
        """
        :param num_samples: the number of samples to draw from the data frame; if None, use all samples
        :param drop_zero_popularity: whether to drop data points where the popularity is zero
        :param threshold_popular: the threshold below which a song is considered as unpopular
        :param random_seed: the random seed to use when sampling data points
        """
        self.num_samples = num_samples
        self.threshold_popular = threshold_popular
        self.drop_zero_popularity = drop_zero_popularity
        self.random_seed = random_seed

    def load_data_frame(self) -> pd.DataFrame:
        """
        :return: the full data frame for this dataset (including the class column)
        """
        df = pd.read_csv(config.csv_data_path())
        if self.num_samples is not None:
            df = df.sample(self.num_samples, random_state=self.random_seed)
        df[COL_GEN_POPULARITY_CLASS] = df[COL_POPULARITY].apply(lambda x: CLASS_POPULAR if x >= self.threshold_popular else CLASS_UNPOPULAR)
        return df

    def load_xy(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        :return: a pair (X, y) where X is the data frame containing all attributes and y is the corresping series of class values
        """
        df = self.load_data_frame()
        return df.drop(columns=COL_GEN_POPULARITY_CLASS), df[COL_GEN_POPULARITY_CLASS]


class ModelFactory:
    COLS_USED_BY_ORIGINAL_MODELS = [COL_YEAR, *COLS_MUSICAL_DEGREES, COL_KEY, COL_MODE, COL_TEMPO, COL_TIME_SIGNATURE, COL_LOUDNESS,
        COL_DURATION_MS]

    @classmethod
    def _create_pipeline_orig_model(cls, model) -> Pipeline:
        return Pipeline([
            ("project_scale", ColumnTransformer([("scaler", StandardScaler(), cls.COLS_USED_BY_ORIGINAL_MODELS)])),
            ("model", model)])

    @classmethod
    def create_logistic_regression_orig(cls):
        return cls._create_pipeline_orig_model(linear_model.LogisticRegression(solver='lbfgs', max_iter=1000))

    @classmethod
    def create_knn_orig(cls):
        return cls._create_pipeline_orig_model(KNeighborsClassifier(n_neighbors=1))

    @classmethod
    def create_random_forest_orig(cls):
        return cls._create_pipeline_orig_model(RandomForestClassifier(n_estimators=100))

    @classmethod
    def create_decision_tree_orig(cls):
        return cls._create_pipeline_orig_model(DecisionTreeClassifier(random_state=42, max_depth=2))


if __name__ == '__main__':
    # define & load dataset
    dataset = Dataset(10000)
    X, y = dataset.load_xy()

    # split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42, test_size=0.3, shuffle=True)

    # define models to be evaluated
    models = [
        ModelFactory.create_logistic_regression_orig(),
        ModelFactory.create_knn_orig(),
        ModelFactory.create_random_forest_orig(),
        ModelFactory.create_decision_tree_orig(),
    ]

    # evaluate models
    for model in models:
        print(f"Evaluating model:\n{model}")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        print(confusion_matrix(y_test, y_pred))
        print(classification_report(y_test, y_pred))
