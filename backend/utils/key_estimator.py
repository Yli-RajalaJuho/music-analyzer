import numpy as np
import scipy.linalg
from scipy.stats import zscore
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class KeyEstimator:
    """
    Estimate musical key using the Krumhansl-Kessler algorithm.
    Produces correlations for all 12 major and 12 minor keys.
    """

    major_profile = np.asarray(
        [6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
         2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
    )
    minor_profile = np.asarray(
        [6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
         2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
    )

    def __post_init__(self):
        self.major_profile = zscore(self.major_profile)
        self.major_norm = scipy.linalg.norm(self.major_profile)
        self.major_profile = scipy.linalg.circulant(self.major_profile)

        self.minor_profile = zscore(self.minor_profile)
        self.minor_norm = scipy.linalg.norm(self.minor_profile)
        self.minor_profile = scipy.linalg.circulant(self.minor_profile)

    def __call__(self, chroma_vector: np.ndarray) -> Tuple[str, str]:
        """
        Takes an averaged chroma vector (12 bins) and returns (key, mode)
        """
        chroma_vector = zscore(chroma_vector)
        x_norm = scipy.linalg.norm(chroma_vector)

        coeffs_major = self.major_profile.T.dot(chroma_vector) / self.major_norm / x_norm
        coeffs_minor = self.minor_profile.T.dot(chroma_vector) / self.minor_norm / x_norm

        pitch_classes = ['C', 'C#', 'D', 'D#', 'E',
                         'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        best_major = np.argmax(coeffs_major)
        best_minor = np.argmax(coeffs_minor)

        if coeffs_major[best_major] >= coeffs_minor[best_minor]:
            return pitch_classes[best_major], "major"
        else:
            return pitch_classes[best_minor], "minor"
