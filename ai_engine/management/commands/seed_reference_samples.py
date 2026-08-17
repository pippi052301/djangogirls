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

        file_path = os.path.join(settings.BASE_DIR, 'ai_engine', 'data', 'sample_data.json')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'[ERROR] Data file not found at: {file_path}'))
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sample_data = json.load(f)
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('[ERROR] JSON file syntax error. Please check the file.'))
            return

        self.stdout.write(f'[OK] Found {len(sample_data)} samples. Ingesting...')

        created_count = 0
        for item in sample_data:
            exists = ReferenceSample.objects.filter(
                exercise_id=item["exercise_id"], 
                content=item["content"]
            ).exists()

            if not exists:
                self.stdout.write(f"Processing exercise_id: {item['exercise_id']} (Score: {item['score']})...")
                
                embedding_vector = get_text_embedding(item["content"])
                
                # Bypassing vector storing error if SQLite dev DB is used without pgvector
                if embedding_vector is None:
                    self.stdout.write(
                        self.style.ERROR(
                            f"[ERROR] Failed to create embedding for {item['score']}pts"
                        )
                    )

                try:
                    ReferenceSample.objects.create(
                        exercise_id=item["exercise_id"],
                        content=item["content"],
                        score=item["score"],
                        feedback=item["feedback"],
                        embedding=embedding_vector
                    )
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"  [SUCCESS] Saved sample {item['score']} pts"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  [ERROR] Failed to save sample: {e}"))
            else:
                self.stdout.write(f"[INFO] Sample (Score: {item['score']}) already exists, skipped.")

        self.stdout.write(self.style.SUCCESS(f'\n[DONE] Successfully ingested {created_count} samples.'))