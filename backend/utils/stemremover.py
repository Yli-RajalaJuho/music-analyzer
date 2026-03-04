import os
import demucs.separate

def separate_vocals(input_path: str, model_name="mdx_extra"):
    """
    Runs Demucs separation and returns the paths to the separated stems.
    """

    # Run Demucs (it automatically outputs to separated/<model>/<filename>/)
    demucs.separate.main([
        "--mp3",
        "--two-stems", "vocals",
        "-n", model_name,
        input_path
    ])

    # Demucs creates separated/mdx_extra/<session_id>/...
    # base_output = f"separated/{model_name}/{session_id}"

