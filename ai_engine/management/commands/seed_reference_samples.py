import json
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from ai_engine.models import ReferenceSample
from ai_engine.services.embedding_service import get_text_embedding

class Command(BaseCommand):
    help = 'Import sample grading data from JSON files, along with vector embeddings, into the database.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Initializing the ingestion of sample grading data from JSON files...'))

        # Automatically retrieve the absolute path to the JSON file in the 'data' directory.
        file_path = os.path.join(settings.BASE_DIR, 'ai_engine', 'data', 'sample_data.json')

        # Check if the file exists.
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'❌ Data file not found at: {file_path}'))
            return

        #Read data from the JSON file.
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sample_data = json.load(f)
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('❌JSON file syntax error. Please check the file..'))
            return

        self.stdout.write(f'✅ Found {len(sample_data)} sample. Starting Vector...')

        created_count = 0
        for item in sample_data:
            # Check if this sample already exists (to prevent duplication when running multiple times).
            exists = ReferenceSample.objects.filter(
                exercise_id=item["exercise_id"], 
                content=item["content"]
            ).exists()

            if not exists:
                self.stdout.write(
                    f"Processing exercise_id: {item['exercise_id']} "
                    f"(Score: {item['score']})..."
                )

                embedding_vector = get_text_embedding(item["content"])

                # Embedding生成に失敗した場合は保存しない
                if embedding_vector is None:
                    self.stdout.write(
                        self.style.ERROR(
                            f"  [ERROR] Failed to create embedding "
                            f"for {item['score']} pts"
                        )
                    )
                    continue

                try:
                    ReferenceSample.objects.create(
                        exercise_id=item["exercise_id"],
                        content=item["content"],
                        score=item["score"],
                        feedback=item["feedback"],
                        embedding=embedding_vector
                    )

                    created_count += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  [SUCCESS] Saved sample "
                            f"{item['score']} pts"
                        )
                    )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"  [ERROR] Failed to save sample: {e}"
                        )
                    )

            else:
                self.stdout.write(
                    f"[INFO] Sample (Score: {item['score']}) "
                    "already exists, skipped."
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n[DONE] Successfully ingested "
                f"{created_count} samples."
            )
        )