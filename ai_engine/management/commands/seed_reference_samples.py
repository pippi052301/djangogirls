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
                self.stdout.write(f"⏳ Creating Vector for exercise_id: {item['exercise_id']} (Score: {item['score']})...")
                
                # Call API Gemini to create Vector for sample
                embedding_vector = get_text_embedding(item["content"])
                
                if embedding_vector:
                    ReferenceSample.objects.create(
                        exercise_id=item["exercise_id"],
                        content=item["content"],
                        score=item["score"],
                        feedback=item["feedback"],
                        embedding=embedding_vector
                    )
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"  ✓ save sample  {item['score']}đ"))
                else:
                    self.stdout.write(self.style.ERROR(f"  ✗ error in creating vector {item['score']}đ"))
            else:
                self.stdout.write(f"ℹ️ Sample (Score: {item['score']}) existed, skip.")

        self.stdout.write(self.style.SUCCESS(f'\n🎉 Done! Success {created_count} new sample to DB.'))