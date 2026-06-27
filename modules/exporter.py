import json
import os
from datetime import datetime


class Exporter:

    OUTPUT_FOLDER = "outputs"

    @staticmethod
    def save_analysis(resume_json, jd_json, match_result):

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        analysis_folder = os.path.join(
            Exporter.OUTPUT_FOLDER,
            f"analysis_{timestamp}"
        )

        os.makedirs(analysis_folder, exist_ok=True)

        # Save Resume
        with open(
            os.path.join(analysis_folder, "resume.json"),
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                resume_json,
                f,
                indent=4,
                ensure_ascii=False
            )

        # Save Job Description
        with open(
            os.path.join(analysis_folder, "job_description.json"),
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                jd_json,
                f,
                indent=4,
                ensure_ascii=False
            )

        # Save Match Result
        with open(
            os.path.join(analysis_folder, "match_result.json"),
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                match_result,
                f,
                indent=4,
                ensure_ascii=False
            )

        # Metadata
        metadata = {
            "timestamp": timestamp,
            "match_score": match_result["match_score"]
        }

        with open(
            os.path.join(analysis_folder, "metadata.json"),
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                metadata,
                f,
                indent=4
            )

        return analysis_folder