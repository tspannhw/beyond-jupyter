from sklearn import linear_model
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from pop.features import COL_YEAR, COLS_MUSICAL_DEGREES, COL_KEY, COL_MODE, COL_TEMPO, COL_TIME_SIGNATURE, COL_LOUDNESS, COL_DURATION_MS


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