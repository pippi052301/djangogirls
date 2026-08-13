import json
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from ai_engine.models import ReferenceSample
from ai_engine.services.embedding_service import get_text_embedding

class Command(BaseCommand):
    help = 'Nạp dữ liệu bài chấm mẫu từ file JSON kèm Vector Embedding vào Database'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🚀 Đang bắt đầu đọc dữ liệu mẫu từ file JSON...'))

        # Tự động lấy đường dẫn tuyệt đối tới file JSON trong thư mục 'data'
        file_path = os.path.join(settings.BASE_DIR, 'ai_engine', 'data', 'sample_data.json')

        # Kiểm tra xem file có tồn tại không
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'❌ Không tìm thấy file dữ liệu tại: {file_path}'))
            return

        # Đọc dữ liệu từ file JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sample_data = json.load(f)
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('❌ File JSON bị lỗi cú pháp. Vui lòng kiểm tra lại.'))
            return

        self.stdout.write(f'✅ Tìm thấy {len(sample_data)} bài mẫu. Bắt đầu xử lý Vector...')

        created_count = 0
        for item in sample_data:
            # Kiểm tra xem bài mẫu này đã tồn tại chưa (tránh trùng lặp khi chạy lệnh nhiều lần)
            exists = ReferenceSample.objects.filter(
                exercise_id=item["exercise_id"], 
                content=item["content"]
            ).exists()

            if not exists:
                self.stdout.write(f"⏳ Đang tạo Vector cho exercise_id: {item['exercise_id']} (Điểm: {item['score']})...")
                
                # Gọi API Gemini để tạo Vector cho bài làm mẫu
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
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Đã lưu thành công bài mẫu {item['score']}đ"))
                else:
                    self.stdout.write(self.style.ERROR(f"  ✗ Lỗi tạo Vector cho bài mẫu {item['score']}đ"))
            else:
                self.stdout.write(f"ℹ️ Bài mẫu (Điểm: {item['score']}) đã tồn tại, bỏ qua.")

        self.stdout.write(self.style.SUCCESS(f'\n🎉 Hoàn thành! Đã nạp thành công {created_count} bài chấm mẫu mới vào CSDL.'))