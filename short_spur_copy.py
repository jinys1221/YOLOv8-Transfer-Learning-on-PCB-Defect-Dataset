import glob, os, shutil

# 경로 설정
label_dir = r"D:/project/anomaly detection/train/labels"
image_dir = r"D:/project/anomaly detection/train/images"
save_dir  = r"D:/project/anomaly detection/Fine_tuning"
label_save_dir  = os.path.join(save_dir, "labels")
image_save_dir  = os.path.join(save_dir, "images")

# 폴더 생성
os.makedirs(label_save_dir, exist_ok=True)
os.makedirs(image_save_dir, exist_ok=True)

count = 0

for file in glob.glob(os.path.join(label_dir, "*.txt")):
    with open(file, 'r') as f:
        lines = f.readlines()
        class_ids = [int(line.split()[0]) for line in lines]

        short_count = class_ids.count(3)
        spur_count  = class_ids.count(4)

        # short, spur 각각 2개 이상 포함된 라벨만 선택
        if short_count >= 2 and spur_count >= 2:
            count += 1
            base = os.path.splitext(os.path.basename(file))[0]
            img_path = os.path.join(image_dir, base + ".jpg")

            # 복사본 이름에 _copy 추가
            dst_label = os.path.join(label_save_dir, f"{base}_copy.txt")
            dst_image = os.path.join(image_save_dir, f"{base}_copy.jpg")

            # 라벨, 이미지 복사
            shutil.copy(file, dst_label)
            if os.path.exists(img_path):
                shutil.copy(img_path, dst_image)

            print(f"{base}_copy.jpg  → short:{short_count}, spur:{spur_count}")

print(f"\n총 {count}개의 라벨 및 이미지가 Fine_tuning 폴더에 복사 완료되었습니다! (파일명에 '_copy' 추가됨)")